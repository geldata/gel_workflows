import os
import sys
import streamlit.web.cli as stcli


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")

    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())


if __name__ == "__main__":
    main()
