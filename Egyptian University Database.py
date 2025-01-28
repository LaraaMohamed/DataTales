import sqlite3
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

# Database connection
def connect_db():
    return sqlite3.connect("university.db", check_same_thread=False)

# Create tables if not exists
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Professor (
            prof_id INTEGER PRIMARY KEY AUTOINCREMENT,
            f_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE,
            phonenumber TEXT
        );

        CREATE TABLE IF NOT EXISTS Department (
            dep_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dep_name TEXT NOT NULL UNIQUE,
            head_id INTEGER NOT NULL,
            FOREIGN KEY(head_id) REFERENCES Professor(prof_id)
        );

        CREATE TABLE IF NOT EXISTS Student (
            std_id INTEGER PRIMARY KEY AUTOINCREMENT,
            f_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT,
            date_of_birth TEXT NOT NULL,
            email TEXT UNIQUE,
            total_credit_hours INTEGER NOT NULL CHECK(total_credit_hours >= 0),
            status TEXT CHECK(status IN ('active','graduate','suspended')),
            ssn TEXT UNIQUE NOT NULL,
            dep_id INTEGER,
            FOREIGN KEY(dep_id) REFERENCES Department(dep_id)
        );

        CREATE TABLE IF NOT EXISTS Course (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            credit_hours INTEGER NOT NULL CHECK(credit_hours IN (2, 3)),
            course_code TEXT NOT NULL UNIQUE,
            dep_id INTEGER,
            FOREIGN KEY(dep_id) REFERENCES Department(dep_id)
        );

        CREATE TABLE IF NOT EXISTS Register_in (
            std_id INTEGER,
            course_id INTEGER,
            grade TEXT DEFAULT 'NA' CHECK(grade IN ('A','A-','B+','B', 'B-','C+','C','C-','D+','D','D-','F','NA')),
            completed INTEGER DEFAULT 0 CHECK(completed IN (0, 1)),
            year INTEGER CHECK(year >= 2015),
            season TEXT CHECK(season IN ('fall','summer','spring')),
            PRIMARY KEY (std_id, course_id, year, season),
            FOREIGN KEY (std_id) REFERENCES Student(std_id),
            FOREIGN KEY (course_id) REFERENCES Course(course_id)
        );

        CREATE TABLE IF NOT EXISTS Prerequisite (
            course_id INTEGER,
            prerequisite_id INTEGER,
            PRIMARY KEY (course_id, prerequisite_id),
            FOREIGN KEY(course_id) REFERENCES Course(course_id),
            FOREIGN KEY(prerequisite_id) REFERENCES Course(course_id),
            CHECK(prerequisite_id != course_id)
        );

        CREATE TABLE IF NOT EXISTS Works_in (
            prof_id INTEGER,
            dep_id INTEGER,
            PRIMARY KEY (prof_id, dep_id),
            FOREIGN KEY (prof_id) REFERENCES Professor(prof_id),
            FOREIGN KEY (dep_id) REFERENCES Department(dep_id)
        );

        CREATE TABLE IF NOT EXISTS Teaching (
            prof_id INTEGER,
            course_id INTEGER,
            PRIMARY KEY (prof_id, course_id),
            FOREIGN KEY (prof_id) REFERENCES Professor(prof_id),
            FOREIGN KEY (course_id) REFERENCES Course(course_id)
        );

        CREATE TABLE IF NOT EXISTS Student_phoneNumber (
            std_id INTEGER,
            phone_number TEXT,
            PRIMARY KEY (std_id, phone_number),
            FOREIGN KEY (std_id) REFERENCES Student(std_id)
        );

        CREATE TABLE IF NOT EXISTS Department_contact_details (
            contact_details INTEGER,
            dep_id INTEGER,
            PRIMARY KEY (contact_details, dep_id),
            FOREIGN KEY (dep_id) REFERENCES Department(dep_id)
        );
        ''')
        conn.commit()
    except Exception as e:
        messagebox.showerror("Error", f"Error creating tables: {str(e)}")
    finally:
        conn.close()

# Dynamic GUI logic
def main():
    current_table = None

    # Table schema definitions
    table_schemas = {
        "Department": [("dep_id", "INT"), ("dep_name", "TEXT"), ("head_id", "INT")],
        "Professor": [("prof_id", "INT"), ("f_name", "TEXT"), ("last_name", "TEXT"), ("email", "TEXT"), ("phonenumber", "TEXT")],
        "Student": [("std_id", "INT"), ("f_name", "TEXT"), ("last_name", "TEXT"), ("address", "TEXT"), ("date_of_birth", "TEXT"), ("email", "TEXT"), ("total_credit_hours", "INT"), ("status", "TEXT"), ("ssn", "TEXT"), ("dep_id", "INT")],
        "Course": [("course_id", "INT"), ("title", "TEXT"), ("credit_hours", "INT"), ("course_code", "TEXT"), ("dep_id", "INT")]
    }

    def select_table(table_name):
        nonlocal current_table
        current_table = table_name
        label_table.config(text=f"Current Table: {current_table}")

        # Clear old fields
        for widget in fields_frame.winfo_children():
            widget.destroy()

        # Create new input fields based on the selected table schema
        for idx, (col_name, col_type) in enumerate(table_schemas[table_name]):
            Label(fields_frame, text=col_name, font=("Arial", 12), bg="#E3F2FD").grid(row=idx, column=0, padx=10, pady=5)
            Entry(fields_frame, font=("Arial", 12), bg="#FFFFFF").grid(row=idx, column=1, padx=10, pady=5)

        view_records()

    def add_record():
        try:
            inputs = [entry.get() for entry in fields_frame.winfo_children() if isinstance(entry, Entry)]
            placeholders = ", ".join("?" for _ in inputs)
            query = f"INSERT INTO {current_table} VALUES ({placeholders})"

            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(query, inputs)
            messagebox.showinfo("Success", "Record added successfully!")
            view_records()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                messagebox.showerror("Error", "Database is locked. Please try again later.")
            else:
                messagebox.showerror("Error", f"Error adding record: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding record: {str(e)}")

    def view_records():
        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {current_table}")
                records = cursor.fetchall()

            listbox.delete(0, END)
            for record in records:
                listbox.insert(END, record)
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                messagebox.showerror("Error", "Database is locked. Please try again later.")
            else:
                messagebox.showerror("Error", f"Error viewing records: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error viewing records: {str(e)}")

    # Main window setup
    root = Tk()
    root.title("Egyptian University Database")
    root.geometry("800x600")
    root.config(bg="#E3F2FD")

    # Header
    header_frame = Frame(root, bg="#0D47A1", pady=10)
    header_frame.pack(fill=X)
    Label(header_frame, text="Egyptian University Database", font=("Arial", 18, "bold"), bg="#0D47A1", fg="white").pack()

    # Table Selection
    select_frame = Frame(root, pady=20, bg="#E3F2FD")
    select_frame.pack(fill=X)
    Label(select_frame, text="Select Table:", font=("Arial", 14), bg="#E3F2FD").grid(row=0, column=0, padx=10)
    for idx, table_name in enumerate(table_schemas.keys()):
        Button(select_frame, text=table_name, width=15, bg="#1976D2", fg="white", font=("Arial", 12),
               command=lambda t=table_name: select_table(t)).grid(row=0, column=idx + 1, padx=10)

    # Current Table Label
    label_table = Label(root, text="Current Table: None", font=("Arial", 16), pady=10, bg="#E3F2FD")
    label_table.pack()

    # Fields
    fields_frame = Frame(root, pady=10, bg="#E3F2FD")
    fields_frame.pack()

    # Action Buttons
    action_frame = Frame(root, pady=10, bg="#E3F2FD")
    action_frame.pack()
    Button(action_frame, text="View Records", width=15, bg="#1976D2", fg="white", font=("Arial", 12), command=view_records).grid(row=0, column=0, padx=10)
    Button(action_frame, text="Add Record", width=15, bg="#1976D2", fg="white", font=("Arial", 12), command=add_record).grid(row=0, column=1, padx=10)

    # Records Listbox
    listbox = Listbox(root, width=100, height=10, font=("Arial", 12), bg="#FFFFFF")
    listbox.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_tables()
    main()
