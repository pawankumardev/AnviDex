import os
import csv
import fnmatch
import psutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import time
import re  # Added for regex-based search

CSV_FILE = 'file_index.csv'

class FileSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Search App")
        self.root.geometry("900x600")
        self.root.configure(bg='#f0f2f5')

        self.exclude_drives = []
        self.sort_column = None
        self.sort_reverse = False

        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("TLabel", background="#f0f2f5")
        style.configure("Treeview", font=('Segoe UI', 10), rowheight=25)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))

        self.search_var = tk.StringVar()
        self.search_frame = ttk.Frame(root)
        self.search_frame.pack(pady=10, padx=10, fill='x')

        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, font=('Segoe UI', 11))
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<KeyRelease>', self.on_key_release)

        ttk.Button(self.search_frame, text="Search", command=self.perform_search).pack(side='left', padx=5)
        ttk.Button(self.search_frame, text="Re-Index", command=self.show_exclude_options).pack(side='left', padx=5)

        columns = ("Filename", "Filetype", "Modified", "Path")
        self.result_tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.result_tree.heading(col, text=col, command=lambda _col=col: self.sort_by_column(_col))
            self.result_tree.column(col, anchor='w', stretch=True, width=250)

        self.result_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.result_tree.bind('<Double-Button-1>', self.on_double_click)
        self.result_tree.bind("<Motion>", self.on_hover)

        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(fill='x', pady=10)

        self.result_count_label = ttk.Label(bottom_frame, text="Results: 0")
        self.result_count_label.pack(side='left', padx=10)

        self.open_with_btn = ttk.Button(bottom_frame, text="Open With", command=self.open_with_selected)
        self.open_with_btn.pack(side='right', padx=10)

        self.progress = ttk.Progressbar(root, mode='indeterminate')

        self.indexed_files_label = ttk.Label(root, text="Total Indexed Files: 0", font=('Segoe UI', 9))
        self.indexed_files_label.pack(pady=5)

        self.tooltip = None
        self.search_timer = None

        self.update_indexed_files_count()

    def on_key_release(self, event):
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(500, self.perform_search)

    def index_files(self, exclude_drives=None):
        self.progress.pack(fill='x', padx=10)
        self.progress.start()

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Filename', 'File Type', 'Absolute Path', 'Modified Date'])

            for partition in psutil.disk_partitions(all=False):
                drive = partition.device
                if drive in exclude_drives:
                    print(f"Skipping {drive} as it is excluded.")
                    continue
                for root, dirs, files in os.walk(drive, topdown=True):
                    try:
                        for file in files:
                            filepath = os.path.join(root, file)
                            name, ext = os.path.splitext(file)
                            modified_time = time.ctime(os.path.getmtime(filepath))
                            writer.writerow([file, ext, filepath, modified_time])
                    except Exception:
                        continue

        self.progress.stop()
        self.progress.pack_forget()
        self.update_indexed_files_count()
        messagebox.showinfo("Done", "Indexing complete!")

    def update_indexed_files_count(self):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                total_lines = sum(1 for _ in f) - 1
            self.indexed_files_label.config(text=f"Total Indexed Files: {total_lines}")
        except FileNotFoundError:
            self.indexed_files_label.config(text="Total Indexed Files: 0")

    def threaded_index(self, exclude_drives):
        threading.Thread(target=self.index_files, args=(exclude_drives,), daemon=True).start()

    def search_files(self, query):
        matches = []
        if not query:
            return matches

        # Replace any non-alphanumeric character in the query with wildcard pattern '.*'
        safe_query = re.escape(query)
        regex_pattern = re.sub(r'[^a-zA-Z0-9]+', '.*', safe_query)
        regex = re.compile(regex_pattern, re.IGNORECASE)

        if not os.path.exists(CSV_FILE):
            messagebox.showerror("Error", "Index file not found. Please run indexing first.")
            return matches

        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row['Filename']
                if regex.search(filename):
                    matches.append((row['Filename'], row['File Type'], row['Modified Date'], row['Absolute Path']))

        return matches

    def perform_search(self):
        query = self.search_var.get()
        if not query:
            return

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        self.results_data = self.search_files(query)

        for i, data in enumerate(self.results_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.result_tree.insert('', 'end', values=data, tags=(tag,))

        self.result_tree.tag_configure('evenrow', background='#ffffff')
        self.result_tree.tag_configure('oddrow', background='#eef1f5')

        self.result_count_label.config(text=f"Results: {len(self.results_data)}")

    def sort_by_column(self, col):
        if not hasattr(self, 'results_data') or not self.results_data:
            return

        col_index = {"Filename": 0, "Filetype": 1, "Modified": 2, "Path": 3}[col]
        self.sort_reverse = not self.sort_reverse if self.sort_column == col else False
        self.sort_column = col

        sorted_data = sorted(self.results_data, key=lambda x: x[col_index].lower(), reverse=self.sort_reverse)

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        for i, data in enumerate(sorted_data):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.result_tree.insert('', 'end', values=data, tags=(tag,))

    def on_double_click(self, event):
        selection = self.result_tree.selection()
        if selection:
            values = self.result_tree.item(selection[0])['values']
            path = values[3]
            self.open_file(path)

    def open_file(self, path):
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")

    def open_with(self, path):
        filetypes = [("Executable Files", "*.exe"), ("All Files", "*.*")]
        app_path = filedialog.askopenfilename(title="Select Application to Open File", filetypes=filetypes)
        if app_path:
            try:
                subprocess.Popen([app_path, path])
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file with selected application: {e}")

    def open_with_selected(self):
        selection = self.result_tree.selection()
        if selection:
            values = self.result_tree.item(selection[0])['values']
            path = values[3]
            self.open_with(path)
        else:
            messagebox.showwarning("No Selection", "Please select a file from the list.")

    def show_exclude_options(self):
        exclude_window = tk.Toplevel(self.root)
        exclude_window.title("Select Drives to Exclude")
        exclude_window.geometry("300x200")

        drives = [partition.device for partition in psutil.disk_partitions(all=False)]
        drive_vars = {}

        for drive in drives:
            var = tk.BooleanVar(value=False)
            drive_vars[drive] = var
            ttk.Checkbutton(exclude_window, text=f"Exclude {drive}", variable=var).pack(anchor='w')

        def apply_exclusions():
            self.exclude_drives = [drive for drive, var in drive_vars.items() if var.get()]
            self.threaded_index(self.exclude_drives)
            exclude_window.destroy()

        ttk.Button(exclude_window, text="Apply Exclusions", command=apply_exclusions).pack(pady=10)

    def on_hover(self, event):
        item = self.result_tree.identify('item', event.x, event.y)
        if item:
            values = self.result_tree.item(item)['values']
            full_path = values[3]

            if len(full_path) > 50:
                self.show_tooltip(event, full_path)

    def show_tooltip(self, event, text):
        if self.tooltip:
            self.tooltip.destroy()

        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = ttk.Label(self.tooltip, text=text, background="lightyellow", relief="solid", padding=5)
        label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()
