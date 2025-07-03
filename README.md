# PostgreSQL Auto Backup Tool

A powerful and user-friendly Windows application to automate PostgreSQL database backups using scheduled tasks. Developed by [Ahmed Shehta](https://ahmed-shehta.netlify.app).

![App Screenshot](https://your-screenshot-url-if-any)

## 🚀 Features

- Auto-detect PostgreSQL version
- Backup multiple databases at once
- Custom backup intervals (via Task Scheduler)
- Deletes old backups automatically
- GUI made with Tkinter
- Supports custom backup directory
- Safe `.bat` script generation

## 🖥️ Requirements

- Python 3.10+
- Windows 10/11
- PostgreSQL installed

## 🔧 Installation

1. Clone or download this repository
2. Run `main.py` using Python
3. Or use the EXE version from the `dist/` folder

To build your own EXE:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=icon.ico main.py
