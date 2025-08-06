import tkinter as tk
from ui.ui import create_main_window

if __name__ == "__main__":
    root = tk.Tk()
    app = create_main_window(root)
    root.mainloop()
