import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ganga@1407_",
        database="student_db"
    )

# Add student
def add_students(name, age, subject, marks):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, subject, marks) VALUES (%s, %s, %s, %s)",
                   (name, age, subject, marks))
    conn.commit()
    conn.close()

# View students
def view_students():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM students", conn)
    conn.close()
    return df

# Update marks
def update_marks(student_id, marks):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET marks=%s WHERE id=%s", (marks, student_id))
    conn.commit()
    conn.close()

# Delete student
def delete_students(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=%s", (student_id,))
    conn.commit()
    conn.close()

# Streamlit UI
st.title("🎓 Student Performance Dashboard")

menu = ["Add Students", "View Students", "Update Marks", "Delete Students", "Analytics"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Students":
    st.subheader("Add Student Details")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=5, max_value=100)
    subject = st.text_input("Subject")
    marks = st.number_input("Marks", min_value=0, max_value=100)
    if st.button("Add"):
        add_students(name, age, subject, marks)
        st.success("Student added successfully!")

elif choice == "View Students":
    st.subheader("All Students")
    df = view_students()
    df["Status"] = df["marks"].apply(lambda x: "Pass" if x >= 40 else "Fail")
    st.dataframe(df)

elif choice == "Update Marks":
    st.subheader("Update Student Marks")
    student_id = st.number_input("Student ID", min_value=1)
    marks = st.number_input("New Marks", min_value=0, max_value=100)
    if st.button("Update"):
        update_marks(student_id, marks)
        st.success("Marks updated successfully!")

elif choice == "Delete Students":
    st.subheader("Delete Student Record")
    student_id = st.number_input("Student ID", min_value=1)
    if st.button("Delete"):
        delete_students(student_id)
        st.success("Student deleted successfully!")

elif choice == "Analytics":
    st.subheader("Performance Analytics")
    df = view_students()
    if not df.empty:
        df["Status"] = df["marks"].apply(lambda x: "Pass" if x >= 40 else "Fail")

        avg_marks = df["marks"].mean()
        pass_percentage = (df["Status"].value_counts().get("Pass", 0) / len(df)) * 100
        top_scorer = df.loc[df["marks"].idxmax()]

        st.write(f"**Average Marks:** {avg_marks:.2f}")
        st.write(f"**Pass Percentage:** {pass_percentage:.2f}%")
        st.write(f"**Top Scorer:** {top_scorer['name']} ({top_scorer['marks']} marks)")

        # Bar chart: Subject vs Average Marks
        subject_avg = df.groupby("subject")["marks"].mean()
        fig, ax = plt.subplots()
        subject_avg.plot(kind="bar", ax=ax)
        st.pyplot(fig)

        # Pie chart: Pass/Fail ratio
        status_counts = df["Status"].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%")
        st.pyplot(fig2)