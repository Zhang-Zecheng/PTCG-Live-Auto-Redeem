import pyautogui
import time
import cv2
import numpy as np
import clipboard
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import mouse
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import threading
import keyboard
import sys
import os


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


stop = False
redeem_button_image = resource_path('redeem.jpg')
input_field_image = resource_path('input.jpg')
submit_button_image = resource_path('submit.jpg')
collect_all_image = resource_path('collectAll.jpg')
done_image = resource_path('Done.jpg')
pokemon_tcg_image = resource_path("pokemon.jpg")
icon_image = resource_path("Mimikyu.ico")


global photo

codes = []
collect_all_coords = None
done_coords = None
input_field_coords = None
submit_button_coords = None
redeem_button_coords = None


def check_keypress():
    global stop
    keyboard.wait('esc')
    stop = True
    sys.exit()


def open_file():
    global codes, file_path_var
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[
                                           ("Text files", "*.txt"), ("All files", "*.*")])

    if file_path:
        file_path_var.set(file_path)
        with open(file_path, "r") as file:
            codes = [line.strip() for line in file.readlines()]


def get_click_position():
    mouse.wait(button='left', target_types=('down',))
    return mouse.get_position()


def find_element(image_file, threshold=0.7, scales=[1.0], timeout=2):
    start_time = time.time()

    while True:
        screenshot = pyautogui.screenshot()
        screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        template = cv2.imread(image_file, cv2.IMREAD_COLOR)

        best_val = -np.inf
        best_scale = None
        best_loc = None

        for scale in scales:
            resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
            result = cv2.matchTemplate(
                screenshot_np, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_val:
                best_val = max_val
                best_scale = scale
                best_loc = max_loc

        if best_val >= threshold:
            center_x = best_loc[0] + int(template.shape[1] * best_scale) // 2
            center_y = best_loc[1] + int(template.shape[0] * best_scale) // 2
            return center_x, center_y

        if timeout is not None and (time.time() - start_time) > timeout:
            confirm = pyautogui.confirm(
                text=f"Element '{image_file}' not found. Please click the correct location.", buttons=['OK', 'Cancel'])
            if confirm == 'OK':
                location = get_click_position()
                return location[0], location[1]
            else:
                raise Exception(f"Element '{image_file}' not found on screen.")

        time.sleep(1)


def ask_user_to_click(description):
    messagebox.showinfo(
        "Info", f"Please click the {description} on the screen within the next 5 seconds.")
    time.sleep(5)
    location = pyautogui.position()
    return location.x, location.y


def redeem_code_group(code_group, input_field_coords, submit_button_coords, redeem_button_coords):
    sleep_time = float(sleep_time_var.get())
    for code in code_group:

        pyautogui.click(input_field_coords)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        # Copy the code to the clipboard
        clipboard.copy(code)
        time.sleep(sleep_time)

        # Paste the code from the clipboard
        pyautogui.hotkey('ctrl', 'v')
        # pyautogui.press('enter')
        time.sleep(sleep_time)

        # Find and click the 'Submit' button
        pyautogui.click(submit_button_coords)
        time.sleep(sleep_time+0.5)

    pyautogui.click(redeem_button_coords)


def cancel_wait():
    continue_var.set(999)


def create_main_window():
    root = tk.Tk()
    root.title("PTCG Live Auto Redeem")

    root.iconbitmap(icon_image)

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            cancel_wait()
            root.destroy()
            sys.exit()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack()

    # Load the image
    # Replace the original file path with the new one
    image = Image.open(pokemon_tcg_image)
    global photo
    photo = ImageTk.PhotoImage(image)

    # Image canvas
    image_canvas = tk.Canvas(
        main_frame, width=image.width, height=image.height)
    image_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    image_canvas.grid(row=0, column=0, columnspan=12, padx=10, pady=10)

    # File path label
    file_path_label = tk.Label(main_frame, text="File path:")
    file_path_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    global file_path_var
    file_path_var = tk.StringVar()
    file_path_var.set("No file selected")

    # File path display
    file_path_display = tk.Label(
        main_frame, textvariable=file_path_var, anchor="w")
    file_path_display.grid(row=2, column=0, columnspan=12,
                           padx=10, pady=10, sticky="w")

    # Open button
    open_button = tk.Button(main_frame, text="Open",
                            command=open_file, width=10, height=2)
    open_button.grid(row=3, column=0, padx=20, pady=10)

    # Start button
    global start_button
    start_button = tk.Button(main_frame, text="Start",
                             command=start_redeem, width=10, height=2)
    start_button.grid(row=3, column=4, padx=20, pady=10)

    # Continue button
    global continue_button, continue_var
    continue_var = tk.IntVar(value=0)
    continue_button = tk.Button(main_frame, text="Continue",
                                command=lambda: continue_var.set(1), width=10, height=2)
    continue_button.grid(row=3, column=8, padx=20, pady=10)

    # Sleep time label
    sleep_time_label = tk.Label(main_frame, text="Sleep time (s):")
    sleep_time_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    author_label = tk.Label(main_frame, text="版权所有: @闲鱼：巨糕冷")
    author_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

    global sleep_time_var
    sleep_time_var = tk.StringVar()
    sleep_time_var.set("1")  # Set the default value to 1

    # Sleep time entry
    sleep_time_entry = tk.Entry(main_frame, textvariable=sleep_time_var)
    sleep_time_entry.grid(row=4, column=4, padx=10, pady=10, sticky="w")

    return root


def start_redeem():
    redeem_thread = threading.Thread(target=start_redeem_thread)
    redeem_thread.start()


def start_redeem_thread():
    global codes, scales, input_field_coords, submit_button_coords, redeem_button_coords
    if not codes:
        print("No codes loaded. Please open a file first.")
        return
    start_button['state'] = "disable"
    reference_width = 2560
    reference_height = 1440
    target_window_sizes = [(2560, 1440), (1920, 1080),
                           (1600, 900), (1368, 768), (1280, 720)]
    scales = [min(target_width / reference_width, target_height / reference_height)
              for target_width, target_height in target_window_sizes]
    input_field_coords = find_element(input_field_image, scales=scales)
    submit_button_coords = find_element(submit_button_image, scales=scales)
    redeem_button_coords = find_element(redeem_button_image, scales=scales)
    time.sleep(1)
    group_size = 10
    try:
        for i in range(0, len(codes), group_size):
            code_group = codes[i:i + group_size]
            redeem_code_group(code_group, input_field_coords,
                              submit_button_coords, redeem_button_coords)
            try:
                continue_button.wait_variable(continue_var)
                if continue_var.get() == 999:
                    break
            except:
                continue
    except:
        pass


if __name__ == "__main__":
    main_window = create_main_window()
    main_window.mainloop()
