import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.disk_utils import get_folder_contents, delete_path
from utils.ui_helpers import format_size, filter_items_by_name


class DiskAnalyzerApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("DiskDrill")
        self.window.geometry("900x650")
        self.window.configure(bg="#f0f2f5")

        self.current_path = ""
        self.history = []

        # Style Configuration
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 11))
        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#333")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TProgressbar", thickness=20, troughcolor="#d9d9d9", background="#4a90e2")

        # Header
        self.header = ttk.Label(self.window, text="DiskDrill", style="Header.TLabel")
        self.header.pack(pady=10)

        # Control Buttons Frame
        top_frame = ttk.Frame(self.window)
        top_frame.pack(pady=5)

        self.select_btn = ttk.Button(top_frame, text="📂 Browse Folder", command=self.choose_folder)
        self.select_btn.pack(side="left", padx=10)

        self.back_btn = ttk.Button(top_frame, text="⬅ Back", command=self.go_back)
        self.back_btn.pack(side="left", padx=10)
        self.back_btn["state"] = "disabled"

        self.path_label = ttk.Label(self.window, text="", font=("Segoe UI", 9, "italic"))
        self.path_label.pack(pady=2)

        # Search bar
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.update_filter())

        search_frame = ttk.Frame(self.window)
        search_frame.pack(pady=5)

        ttk.Label(search_frame, text="🔍 Search: ").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side="left")

        # Scrollable Canvas
        self.canvas = tk.Canvas(self.window, bg="#f0f2f5", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas)

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(fill="both", expand=True, side="left", padx=(10, 0), pady=10)
        self.scroll_y.pack(fill="y", side="right", padx=(0, 10))

        self.frame.bind("<Configure>", self.update_scroll)

    def run(self):
        self.window.mainloop()

    def update_scroll(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.load_folder(folder)

    def go_back(self):
        if self.history:
            last_path = self.history.pop()
            self.load_folder(last_path)
        if not self.history:
            self.back_btn["state"] = "disabled"

    def load_folder(self, path):
        self.current_path = path
        self.path_label["text"] = f"📁 Current Path: {path}"
        self.clear_frame()
        self.back_btn["state"] = "normal" if self.history else "disabled"

        items = get_folder_contents(path)
        self.all_items = items  # Save all items for filtering

        if not items:
            ttk.Label(self.frame, text="🚫 No files or folders found.", font=("Segoe UI", 11, "italic")).pack(pady=20)
            return

        total_size = sum(item['size'] for item in items) or 1
        items.sort(key=lambda x: x['size'], reverse=True)

        for item in items:
            percent = int((item['size'] / total_size) * 100)
            self.add_item_row(item, percent)

    def update_filter(self):
        query = self.search_var.get()
        self.clear_frame()

        filtered = filter_items_by_name(self.all_items, query)
        total_size = sum(item['size'] for item in filtered) or 1

        if not filtered:
            ttk.Label(self.frame, text="🛑 No matching files or folders.", font=("Segoe UI", 11, "italic")).pack(pady=10)
            return

        for item in filtered:
            percent = int((item['size'] / total_size) * 100)
            self.add_item_row(item, percent)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def add_item_row(self, item, percent):
        row = ttk.Frame(self.frame)
        row.pack(fill="x", pady=8, padx=20)

        icon = "📁" if item['is_dir'] else "📄"
        label = ttk.Label(row, text=f"{icon} {item['name']}", width=40)
        label.pack(side="left")

        bar = ttk.Progressbar(row, value=percent, maximum=100, length=250)
        bar.pack(side="left", padx=15)

        size_str = format_size(item['size'])  # Uses the helper you imported
        percent_label = ttk.Label(row, text=f"{size_str} ({percent}%)", width=20)
        percent_label.pack(side="left")

        if item['is_dir']:
            open_btn = ttk.Button(row, text="Open", width=6,
                                  command=lambda p=item['path']: self.navigate_to(p))
            open_btn.pack(side="left", padx=5)

        del_btn = ttk.Button(row, text="Delete", width=6,
                             command=lambda p=item['path']: self.confirm_delete(p))
        del_btn.pack(side="left", padx=5)

    def navigate_to(self, folder_path):
        self.history.append(self.current_path)
        self.load_folder(folder_path)

    def confirm_delete(self, path):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n\n{path}")
        if confirm:
            success = delete_path(path)
            if success:
                self.load_folder(self.current_path)
            else:
                messagebox.showerror("Error", "Unable to delete.")
