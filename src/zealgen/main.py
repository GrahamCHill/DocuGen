import sys
from zealgen.cli import main as cli_main
from zealgen.app import main as gui_main

def main():
    if len(sys.argv) > 1:
        cli_main()
    else:
        gui_main()

if __name__ == "__main__":
    main()
