import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.ttk import Progressbar

def rename_folder_and_file_names(project_path, old_name, new_name, progress_callback, log_callback):
    total_items = sum([len(files) + len(dirs) for _, dirs, files in os.walk(project_path)])
    current_item = 0

    for root, dirs, files in os.walk(project_path, topdown=False):
        for dir_name in dirs:
            if old_name in dir_name:
                old_dir_path = os.path.join(root, dir_name)
                new_dir_path = os.path.join(root, dir_name.replace(old_name, new_name))
                os.rename(old_dir_path, new_dir_path)
                log_callback(f"{old_dir_path} -> {new_dir_path}")
            current_item += 1
            progress_callback(current_item, total_items)

        for file_name in files:
            if old_name in file_name:
                old_file_path = os.path.join(root, file_name)
                new_file_path = os.path.join(root, file_name.replace(old_name, new_name))
                os.rename(old_file_path, new_file_path)
                log_callback(f"{old_file_path} -> {new_file_path}")
            current_item += 1
            progress_callback(current_item, total_items)

def rename_project_files_and_references(project_path, old_name, new_name, progress_callback, log_callback):
    total_files = sum(len(files) for _, _, files in os.walk(project_path))
    current_file = 0
    for root, _, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(('.uproject', '.cpp', '.h', '.cs', '.ini', '.sln', 'Target.cs', '.uplugin', '.Build.cs')):
                try:
                    update_file_references(file_path, old_name, new_name)
                    log_callback(f"Updated references in: {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error updating file: {file_path}\n{e}")
            current_file += 1
            progress_callback(current_file, total_files)

    rename_folder_and_file_names(project_path, old_name, new_name, progress_callback, log_callback)

def update_file_references(file_path, old_name, new_name):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as file:
            content = file.read()

    content = content.replace(old_name, new_name)

    old_api_name = f"{old_name.upper()}_API"
    new_api_name = f"{new_name.upper()}_API"
    content = content.replace(old_api_name, new_api_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def browse_directory(entry_field):
    directory = filedialog.askdirectory()
    if directory:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, directory)

def rename_project():
    old_name = old_name_entry.get()
    new_name = new_name_entry.get()
    project_path = project_path_entry.get()

    if not old_name or not new_name or not project_path:
        messagebox.showerror("Error", "Please fill out all fields.")
        return

    progress_bar['value'] = 0
    log_text.configure(state='normal')
    log_text.delete(1.0, tk.END)

    def update_progress(current, total):
        progress = (current / total) * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"Progress: {int(progress)}%")
        root.update_idletasks()

    def update_log(message):
        log_text.insert(tk.END, message + '\n')
        log_text.see(tk.END)

    try:
        rename_project_files_and_references(project_path, old_name, new_name, update_progress, update_log)
        messagebox.showinfo("Success", f"Project renamed from {old_name} to {new_name}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        log_text.configure(state='disabled')

root = tk.Tk()
root.title("Unreal Project Renamer")

# Inputs
tk.Label(root, text="Old Project Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
old_name_entry = tk.Entry(root, width=40)
old_name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="New Project Name:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
new_name_entry = tk.Entry(root, width=40)
new_name_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Project Directory:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
project_path_entry = tk.Entry(root, width=40)
project_path_entry.grid(row=2, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="Browse", command=lambda: browse_directory(project_path_entry))
browse_button.grid(row=2, column=2, padx=10, pady=5)

# Progressbar
progress_label = tk.Label(root, text="Progress: 0%")
progress_label.grid(row=3, column=0, columnspan=2, pady=5)
progress_bar = Progressbar(root, length=400, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=3, pady=5)

# Logbox
log_label = tk.Label(root, text="Rename Log:")
log_label.grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
log_text = scrolledtext.ScrolledText(root, width=60, height=10, state='disabled')
log_text.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

# Rename Button
rename_button = tk.Button(root, text="Rename Project", command=rename_project)
rename_button.grid(row=7, column=1, pady=20)

root.mainloop()
