# PTCG Live Auto Redeem

This is a Python script for automatically redeeming codes in PTCG Live.

## Dependencies

You will need the following Python packages installed to run the script:

- pyautogui
- opencv-python-headless
- Pillow
- pyperclip
- PyInstaller (for building the executable)

You can install these packages using `pip`:

```bash
pip install pyautogui opencv-python-headless Pillow pyperclip PyInstaller
```

## Building the Executable

To build the executable, run the following command in your terminal or command prompt:

```bash
pyinstaller --onefile --add-data "resources/pokemon.jpg;resources" --add-data "resources/Mimikyu.ico;resources" --add-data "resources/input.jpg;resources" --add-data "resources/redeem.jpg;resources" --add-data "resources/submit.jpg;resources" --add-data "resources/Done.jpg;resources" --add-data "resources/collectAll.jpg;resources" --icon=pc.ico autoRedeem.py
```

This command will create a standalone executable called autoRedeem.exe in the dist folder.