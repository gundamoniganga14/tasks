import streamlit as st
import pandas as pd
import mysql.connector

# DB connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ganga@1407_",
        database="complaint_db"
    )

# Add complaint
def add_complaint(name, email, category, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (name, email, category, description) VALUES (%s, %s, %s, %s)",
        (name, email, category, description)
    )
    conn.commit()
    complaint_id = cursor.lastrowid
    conn.close()
    return complaint_id

# View complaints
def view_complaints():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM complaints", conn)
    conn.close()
    return df

# Update status
def update_status(complaint_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status=%s WHERE id=%s", (status, complaint_id))
    conn.commit()
    conn.close()

# Search complaint
def search_complaint(complaint_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM complaints WHERE id=%s", conn, params=(complaint_id,))
    conn.close()
    return df

# Streamlit UI
st.title("📝 Complaint Registration System")

menu = ["Submit Complaint", "Admin Panel"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Submit Complaint":
    st.subheader("Submit a Complaint")
    with st.form("complaint_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        category = st.selectbox("Category", ["Service", "Billing", "Technical", "Other"])
        description = st.text_area("Complaint Description")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if not name or not email or not description:
                st.error("All fields are required!")
            else:
                complaint_id = add_complaint(name, email, category, description)
                st.success(f"Complaint submitted successfully! Your Complaint ID is {complaint_id}")

elif choice == "Admin Panel":
    st.subheader("Admin Panel")
    admin_menu = st.sidebar.radio("Admin Options", ["View All Complaints", "Update Status", "Search Complaint"])

    if admin_menu == "View All Complaints":
        df = view_complaints()
        for _, row in df.iterrows():
            with st.expander(f"Complaint ID: {row['id']} | Status: {row['status']}"):
                st.write(f"**Name:** {row['name']}")
                st.write(f"**Email:** {row['email']}")
                st.write(f"**Category:** {row['category']}")
                st.write(f"**Description:** {row['description']}")
                st.write(f"**Created At:** {row['created_at']}")

    elif admin_menu == "Update Status":
        complaint_id = st.number_input("Complaint ID", min_value=1)
        status = st.selectbox("New Status", ["Open", "In Progress", "Closed"])
        if st.button("Update"):
            update_status(complaint_id, status)
            st.success("Complaint status updated!")

    elif admin_menu == "Search Complaint":
        complaint_id = st.number_input("Complaint ID", min_value=1)
        if st.button("Search"):
            df = search_complaint(complaint_id)
            if df.empty:
                st.error("Complaint not found!")
            else:
                row = df.iloc[0]
                with st.expander(f"Complaint ID: {row['id']} | Status: {row['status']}"):
                    st.write(f"**Name:** {row['name']}")
                    st.write(f"**Email:** {row['email']}")
                    st.write(f"**Category:** {row['category']}")
                    st.write(f"**Description:** {row['description']}")
                    st.write(f"**Created At:** {row['created_at']}")