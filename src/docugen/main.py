import os
import sys
from docugen.cli import main as cli_main
from docugen.app import main as gui_main

if getattr(sys, "frozen", False):
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
            meipass, "ms-playwright"
        )

def main():
    if len(sys.argv) > 1:
        cli_main()
    else:
        gui_main()

if __name__ == "__main__":
    main()
