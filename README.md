# AnviDex🔍Faster PC File Search App (Windows)

A desktop GUI tool built with **Python + Tkinter** that lets you quickly **search for files** across your system with support for:
- Wildcards (`*`) and **smart fuzzy matching** (spaces/special characters count as wildcards)
- Sorting by filename, type, modified date, or path
- Opening files directly or with a custom app
- Excluding drives during indexing
- Lightweight and fast (indexes files to a local `.csv`)

---

## 📸 Screenshots



---

## 🚀 Features

- ✅ Fast wildcard & fuzzy searching
- ✅ Modern UI with alternating row colors
- ✅ Sort results by column
- ✅ Preview full paths via tooltips
- ✅ "Open With" functionality
- ✅ Drive exclusion during indexing
- ✅ Real-time indexed file count

---

## 🛠️ Installation

### 1. ✅ Install Python (if not already installed)
Download and install the latest version of Python from:  
👉 https://www.python.org/downloads/

- Be sure to **check the box that says "Add Python to PATH"** during installation.

### 2. 📁 Clone this repository

```bash
git clone https://github.com/yourusername/file-search-app.git
cd file-search-app
```

### 3. 📦 Install dependencies

Only one third-party module is needed:

```bash
pip install psutil
```

---

## 🧠 How It Works

1. **Indexing**: Click `Re-Index` → optionally exclude drives → the app scans and saves file metadata to `file_index.csv`.
2. **Search**: Type in the search bar (e.g., `abc de`) → matches anything like `abc    de`, `abc_de`, `abc-de`, etc.
3. **Interact**:
   - Double-click a result to open the file
   - Use "Open With" to choose a custom app
   - Hover over long paths to see tooltips
   - Click on column headers to sort

---

## 🔎 Search Tips

- Typing `report 2024` will match:
  - `report_2024.pdf`
  - `report-2024-final.docx`
  - `report     2024.xlsx`

💡 Spaces, underscores `_`, dashes `-`, and even missing characters are treated as wildcards.

---

## 🖥️ Running the App

```bash
python file_search_app.py
```

Make sure the terminal stays open while the app runs.

---

## 📁 Output File

The index is saved as `file_index.csv` in the same folder. You can delete it anytime to re-index from scratch.

---

## 📌 Notes

- ⚠️ Currently works on **Windows only** due to usage of `os.startfile`.
- Works best when run as Administrator (to access all drives).
- Doesn't search inside file contents — only metadata.

---

## 🤝 Contributions

Feel free to fork and submit pull requests! Feature ideas are welcome:
- Preview file content
- Dark mode
- Saved search history

---

## 📃 License

MIT License
