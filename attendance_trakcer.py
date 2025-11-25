import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os
import json
from datetime import datetime

students_file = "students.json"
attendance_file = "attendance.json"

def load_data(file, default):
    return json.load(open(file)) if os.path.exists(file) else default

students = load_data(students_file, {})
attendance = load_data(attendance_file, {})

def save_data():
    with open(students_file, 'w') as f: json.dump(students, f, indent=2)
    with open(attendance_file, 'w') as f: json.dump(attendance, f, indent=2)

def register_student():
    name, roll = name_entry.get(), roll_entry.get()
    reg_date, reg_time = reg_date_entry.get(), reg_time_entry.get()
    if not name or not roll or not reg_date or not reg_time:
        return messagebox.showerror("Error", "All fields are required.")
    if roll in students:
        return messagebox.showwarning("Exists", "Student already registered.")
    
    students[roll] = {
        "name": name,
        "registered_on": f"{reg_date} {reg_time}"
    }
    save_data()
    name_entry.delete(0, tk.END)
    roll_entry.delete(0, tk.END)
    reg_time_entry.delete(0, tk.END)
    update_student_list()

def update_student_list():
    for row in student_tree.get_children(): student_tree.delete(row)
    for roll, info in students.items():
        student_tree.insert("", tk.END, values=(roll, info["name"]))

def mark_attendance():
    selected = student_tree.selection()
    if not selected:
        return messagebox.showerror("Error", "No student selected")
    roll = student_tree.item(selected[0])['values'][0]
    date = date_entry.get()
    time = time_entry.get()
    status = attendance_var.get()
    if not time: return messagebox.showerror("Error", "Enter time")
    attendance.setdefault(roll, {})[f"{date} {time}"] = status
    save_data()
    messagebox.showinfo("Saved", "Attendance marked")

def delete_student():
    selected = student_tree.selection()
    if not selected: return
    roll = student_tree.item(selected[0])['values'][0]
    if messagebox.askyesno("Confirm", f"Delete {students[roll]['name']}?"):
        students.pop(roll, None)
        attendance.pop(roll, None)
        save_data()
        update_student_list()

def show_total_attendance():
    selected = student_tree.selection()
    if not selected:
        return messagebox.showerror("Error", "No student selected")
    roll = student_tree.item(selected[0])['values'][0]
    records = attendance.get(roll, {})
    present = sum(1 for status in records.values() if status == "Present")
    absent = sum(1 for status in records.values() if status == "Absent")
    total = present + absent
    percentage = (present / total * 100) if total > 0 else 0
    messagebox.showinfo("Total Attendance", f"Present: {present}\nAbsent: {absent}\nAttendance: {percentage:.2f}%")

def view_profile_details():
    roll = profile_roll_entry.get()
    if not roll:
        return messagebox.showerror("Error", "Enter a Roll No")
    if roll not in students:
        return messagebox.showerror("Not Found", "Student not registered")

    records = attendance.get(roll, {})
    present = sum(1 for status in records.values() if status == "Present")
    absent = sum(1 for status in records.values() if status == "Absent")
    total = present + absent
    percentage = (present / total * 100) if total > 0 else 0

    name = students[roll]["name"]
    result = f"Name: {name}\nRoll No: {roll}\nAttendance: {percentage:.2f}%"
    profile_result_label.config(text=result)

# GUI setup
root = tk.Tk()
root.title("Student Attendance Tracker")
root.geometry("800x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# --- Register Tab ---
register_tab = ttk.Frame(notebook)
notebook.add(register_tab, text="Register Student")

tk.Label(register_tab, text="Name").grid(row=0, column=0, padx=10, pady=10)
tk.Label(register_tab, text="Roll No").grid(row=1, column=0, padx=10, pady=10)
tk.Label(register_tab, text="Registration Date").grid(row=2, column=0, padx=10, pady=10)
tk.Label(register_tab, text="Registration Time (HH:MM)").grid(row=3, column=0, padx=10, pady=10)

name_entry = tk.Entry(register_tab)
roll_entry = tk.Entry(register_tab)
reg_date_entry = DateEntry(register_tab)
reg_time_entry = tk.Entry(register_tab)

name_entry.grid(row=0, column=1)
roll_entry.grid(row=1, column=1)
reg_date_entry.grid(row=2, column=1)
reg_time_entry.grid(row=3, column=1)

tk.Button(register_tab, text="Register", command=register_student).grid(row=4, column=0, columnspan=2, pady=10)

# --- Student List Tab ---
student_tab = ttk.Frame(notebook)
notebook.add(student_tab, text="Attendance")

student_tree = ttk.Treeview(student_tab, columns=("Roll", "Name"), show="headings", height=15)
student_tree.heading("Roll", text="Roll No")
student_tree.heading("Name", text="Name")
student_tree.pack(padx=10, pady=10, fill="x")

attendance_frame = tk.Frame(student_tab)
attendance_frame.pack(pady=10)

tk.Label(attendance_frame, text="Date:").grid(row=0, column=0, padx=5)
date_entry = DateEntry(attendance_frame)
date_entry.grid(row=0, column=1, padx=5)

tk.Label(attendance_frame, text="Time (HH:MM):").grid(row=0, column=2, padx=5)
time_entry = tk.Entry(attendance_frame)
time_entry.grid(row=0, column=3, padx=5)

attendance_var = tk.StringVar(value="Present")
status_menu = ttk.OptionMenu(attendance_frame, attendance_var, "Present", "Present", "Absent")
status_menu.grid(row=0, column=4, padx=5)

tk.Button(attendance_frame, text="Mark Attendance", command=mark_attendance).grid(row=0, column=5, padx=10)
tk.Button(student_tab, text="Delete Student", command=delete_student).pack(pady=5)
tk.Button(student_tab, text="Show Total Attendance", command=show_total_attendance).pack(pady=10)

# --- View Profile Tab ---
profile_tab = ttk.Frame(notebook)
notebook.add(profile_tab, text="View Profile")

tk.Label(profile_tab, text="Enter Roll No:").pack(pady=10)
profile_roll_entry = tk.Entry(profile_tab)
profile_roll_entry.pack()

tk.Button(profile_tab, text="View Profile", command=view_profile_details).pack(pady=10)
profile_result_label = tk.Label(profile_tab, text="", font=("Arial", 12), justify="left")
profile_result_label.pack(pady=10)

update_student_list()
root.mainloop()
