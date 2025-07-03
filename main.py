import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import tempfile
import webbrowser
import psycopg2

root = tk.Tk()
root.title("PostgreSQL Auto Backup - Ahmed Shehta")
root.geometry("720x700")
root.resizable(False, False)

def open_website(event):
    webbrowser.open("https://ahmed-shehta.netlify.app")

# Header Frame
header_frame = tk.Frame(root)
header_frame.pack(pady=10)
footer_frame = tk.Frame(root)
footer_frame.place(relx=1.0, rely=1.0, anchor='se')  # Bottom-right corner

# tk.Label(footer_frame, text="© Ahmed Shehta", font=("Helvetica", 8), fg="gray").pack()
tk.Label(header_frame, text="PostgreSQL Auto Backup Tool", font=("Helvetica", 18, "bold"), fg="darkblue").pack()
powered_label = tk.Label(footer_frame, text="Ⓟ Powered by Ahmed Shehta", font=("Helvetica", 10), fg="blue", cursor="hand2")
powered_label.pack()
powered_label.bind("<Button-1>", open_website)
website_label = tk.Label(footer_frame, text="https://ahmed-shehta.netlify.app", fg="gray", font=("Courier", 9), cursor="hand2")
website_label.pack()
website_label.bind("<Button-1>", open_website)
# Footer - bottom right
# Footer - bottom right


# Input Fields Frame
fields = [
    ("Host", "host"),
    ("Port", "port"),
    ("Username", "username"),
    ("Password", "password"),
    ("Backup Folder", "backup_dir"),
    ("Interval (minutes)", "interval_minutes"),
    ("Delete after (days)", "delete_after_days"),
]

frame = tk.Frame(root)
frame.pack(pady=10)
entries = {}

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        entries['backup_dir'].delete(0, tk.END)
        entries['backup_dir'].insert(0, folder)

for i, (label_text, key) in enumerate(fields):
    tk.Label(frame, text=label_text).grid(row=i, column=0, sticky="e", padx=5, pady=5)
    entry = tk.Entry(frame, width=45, show="*" if "password" in key else None)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries[key] = entry
    if key == "backup_dir":
        browse_btn = tk.Button(frame, text="Browse", command=browse_folder)
        browse_btn.grid(row=i, column=2)

# PostgreSQL version label
version_var = tk.StringVar(value="Unknown")
tk.Label(frame, text="PostgreSQL Server Version:").grid(row=len(fields), column=0, sticky="e", padx=5, pady=5)
version_label = tk.Label(frame, textvariable=version_var, fg="green")
version_label.grid(row=len(fields), column=1, sticky="w", padx=5, pady=5)

# Connect Button
def connect_to_postgres():
    host = entries['host'].get().strip()
    port = entries['port'].get().strip()
    user = entries['username'].get().strip()
    password = entries['password'].get().strip()
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname='postgres')
        cur = conn.cursor()

        # Get PostgreSQL version
        cur.execute("SHOW server_version;")
        version = cur.fetchone()[0]
        version_var.set(version)

        # Get list of databases (exclude templates)
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = [row[0] for row in cur.fetchall()]

        if not dbs:
            messagebox.showwarning("No Databases", "No databases found on server.")
            listbox_db.delete(0, tk.END)
        else:
            listbox_db.delete(0, tk.END)
            for dbname in dbs:
                listbox_db.insert(tk.END, dbname)
            status.set(f"Connected. Select one or more databases below.")

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("Connection Error", f"Failed to connect to PostgreSQL server:\n{e}")
        status.set("Connection failed.")
        version_var.set("Unknown")
        listbox_db.delete(0, tk.END)

connect_btn = tk.Button(root, text="Connect to PostgreSQL Server", command=connect_to_postgres, width=30, bg="blue", fg="white")
connect_btn.pack(pady=5)

# Multi-select listbox for databases
tk.Label(root, text="Select Databases to Backup (Ctrl+Click or Shift+Click to select multiple):", font=("Helvetica", 11, "bold")).pack(pady=5)
listbox_db = tk.Listbox(root, selectmode=tk.EXTENDED, width=50, height=8)
listbox_db.pack()

status = tk.StringVar()
status.set("Ready.")
tk.Label(root, textvariable=status, fg="darkgreen", font=("Courier", 10)).pack(pady=10)

# Defaults
entries['host'].insert(0, "localhost")
entries['port'].insert(0, "5432")
entries['username'].insert(0, "postgres")
entries['interval_minutes'].insert(0, "15")
entries['delete_after_days'].insert(0, "14")






def find_pg_dump(version):
    # Check typical installation directories for pg_dump.exe on Windows
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    possible_paths = [
        os.path.join(program_files, f"PostgreSQL\\{version}\\bin\\pg_dump.exe"),
        os.path.join(program_files, f"PostgreSQL\\{version}.0\\bin\\pg_dump.exe"),
        os.path.join(program_files, "PostgreSQL\\bin\\pg_dump.exe")  # fallback if no version folder
    ]
    for path in possible_paths:
        if os.path.isfile(path):
            return path
    return None


# Backup script creation for multiple DBs
def create_batch_script(config, dbnames):
    backup_dir = os.path.normpath(config['backup_dir'])
    os.makedirs(backup_dir, exist_ok=True)
    bat_path = os.path.join(backup_dir, "postgres_backup_multi.bat")
    bat_path = os.path.normpath(bat_path)
    delete_after_days = int(config.get('delete_after_days', '14'))

        # Extract only major version (e.g., 17 from 17.4)
    version_raw = version_var.get()
    major_version = version_raw.split('.')[0] if version_raw else "15"  # fallback to 15

    pg_dump_path = find_pg_dump(major_version) or f"C:\\Program Files\\PostgreSQL\\{major_version}\\bin\\pg_dump.exe"


    db_list_str = " ".join(dbnames)

    script = f"""@echo off
setlocal enabledelayedexpansion
set PGPASSWORD={config['password']}
cd /d "{backup_dir}"
for %%D in ({db_list_str}) do (
    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (
        set DATE=%%d-%%b-%%c
    )
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
        set TIME=%%a-%%b
    )
    set BACKUP_FILE={backup_dir}\\%%D_!DATE!_!TIME!.backup
    echo Backing up database %%D to !BACKUP_FILE!
    "{pg_dump_path}" -h {config['host']} -p {config['port']} -U {config['username']} -F c -b -v -f "!BACKUP_FILE!" %%D
)
echo Deleting backups older than {delete_after_days} days...
forfiles /p "{backup_dir}" /s /m *.backup /D -{delete_after_days} /C "cmd /c del @path"
endlocal
"""
    with open(bat_path, 'w') as f:
        f.write(script)
    return bat_path


def create_task(bat_path, interval_minutes):
    task_name = "PostgreSQL_Backup_MultiDB_AhmedShehta"
    bat_path = os.path.abspath(os.path.normpath(bat_path))
    if not os.path.isfile(bat_path):
        raise Exception(f".bat file not found at:\n{bat_path}")

    powershell_script = f'''
$Action = New-ScheduledTaskAction -Execute "{bat_path}"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes {interval_minutes}) -RepetitionDuration (New-TimeSpan -Days 3650)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName "{task_name}" -Action $Action -Trigger $Trigger -Principal $Principal -Force
'''

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8") as temp_ps1:
        temp_ps1.write(powershell_script.strip())
        ps1_path = temp_ps1.name

    result = subprocess.run(
        ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps1_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    try:
        os.remove(ps1_path)
    except Exception:
        pass

    if result.returncode != 0:
        raise Exception(f"PowerShell task creation failed:\n\n{result.stderr.strip()}")

    print(f"✅ Task created for multiple DBs")

def delete_task():
    task_name = "PostgreSQL_Backup_MultiDB_AhmedShehta"
    try:
        subprocess.run(f'schtasks /Delete /TN "{task_name}" /F', shell=True, check=True)
        messagebox.showinfo("Task Deleted", "Scheduled backup task has been deleted.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to delete scheduled task:\n{e}")

def run_backup_setup():
    try:
        config = {k: e.get().strip() for k, e in entries.items()}
        if not config['backup_dir']:
            raise Exception("Please select a backup folder.")

        selected_indices = listbox_db.curselection()
        if not selected_indices:
            raise Exception("Please select at least one database to backup.")

        dbnames = [listbox_db.get(i) for i in selected_indices]

        status.set(f"Creating backup script for databases: {', '.join(dbnames)} ...")
        root.update()
        bat_path = create_batch_script(config, dbnames)

        status.set("Creating scheduled task...")
        root.update()
        create_task(bat_path, config['interval_minutes'])

        status.set("✅ Task created successfully!")
        messagebox.showinfo("Success", f"Scheduled backup task created for databases:\n{', '.join(dbnames)}")

    except Exception as e:
        status.set("❌ Error")
        messagebox.showerror("Setup Failed", str(e))

def exit_app():
    root.destroy()

# Buttons Frame
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Save & Run Backup", command=run_backup_setup, width=20, bg="green", fg="white").grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Delete Backup Task", command=delete_task, width=20, bg="red", fg="white").grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="Exit", command=exit_app, width=10).grid(row=0, column=2, padx=10)



root.mainloop()
