import sys
import os
import ui.main_ui as main_ui

def launch_tool():
    project_root = os.path.dirname(os.path.abspath("__file__"))

    if project_root not in sys.path:
        sys.path.append(project_root)

    main_ui.show_ui()

if __name__ == "__main__":
    launch_tool()