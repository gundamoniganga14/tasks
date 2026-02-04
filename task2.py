import streamlit as st
import pandas as pd
import mysql.connector
from datetime import date

# DB connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ganga@1407_",
        database="school_db"
    )

# Utility functions
def add_student(roll_no, name, class_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (roll_no, name, class) VALUES (%s, %s, %s)",
                   (roll_no, name, class_name))
    conn.commit()
    conn.close()

def mark_attendance(student_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
                   (student_id, date.today(), status))
    conn.commit()
    conn.close()

def add_marks(student_id, subject, marks):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO marks (student_id, subject, marks) VALUES (%s, %s, %s)",
                   (student_id, subject, marks))
    conn.commit()
    conn.close()

def view_attendance(student_id):
    conn = get_connection()
    df = pd.read_sql("SELECT date, status FROM attendance WHERE student_id=%s", conn, params=(student_id,))
    conn.close()
    return df

def calculate_attendance_percentage(student_id):
    conn = get_connection()
    df = pd.read_sql("SELECT status FROM attendance WHERE student_id=%s", conn, params=(student_id,))
    conn.close()
    if df.empty:
        return 0
    total = len(df)
    present = len(df[df["status"]=="Present"])
    return (present/total)*100

def get_marks(student_id):
    conn = get_connection()
    df = pd.read_sql("SELECT subject, marks FROM marks WHERE student_id=%s", conn, params=(student_id,))
    conn.close()
    return df

# Streamlit UI
st.title("📘 Student Attendance & Marks Management")

menu = ["Add Student", "Mark Attendance", "Add Marks", "View Attendance", "Analytics"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Student":
    with st.form("add_student_form"):
        roll_no = st.text_input("Roll No")
        name = st.text_input("Name")
        class_name = st.selectbox("Class", ["Class 1", "Class 2", "Class 3"])
        submitted = st.form_submit_button("Add Student")
        if submitted:
            try:
                add_student(roll_no, name, class_name)
                st.success("Student added successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

elif choice == "Mark Attendance":
    st.subheader("Mark Daily Attendance")
    student_id = st.number_input("Student ID", min_value=1)
    status = st.radio("Status", ["Present", "Absent"])
    if st.button("Submit Attendance"):
        mark_attendance(student_id, status)
        st.success("Attendance marked!")

elif choice == "Add Marks":
    st.subheader("Add Subject-wise Marks")
    student_id = st.number_input("Student ID", min_value=1)
    subject = st.selectbox("Subject", ["Math", "Science", "English", "History"])
    marks = st.number_input("Marks", min_value=0, max_value=100)
    if st.button("Submit Marks"):
        add_marks(student_id, subject, marks)
        st.success("Marks added!")

elif choice == "View Attendance":
    st.subheader("Attendance History")
    student_id = st.number_input("Student ID", min_value=1)
    if st.button("View"):
        df = view_attendance(student_id)
        st.dataframe(df)

elif choice == "Analytics":
    st.subheader("Student Analytics")
    student_id = st.number_input("Student ID", min_value=1)
    if st.button("Show Analytics"):
        attendance_pct = calculate_attendance_percentage(student_id)
        marks_df = get_marks(student_id)

        st.write(f"**Attendance %:** {attendance_pct:.2f}%")
        if not marks_df.empty:
            marks_df["Status"] = marks_df["marks"].apply(lambda x: "Pass" if x>=40 else "Fail")
            st.dataframe(marks_df)
            if "Fail" in marks_df["Status"].values:
                st.error("❌ Student has failed in one or more subjects")
            else:
                st.success("✅ Student has passed all subjects")