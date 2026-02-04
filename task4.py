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
        database="shop_db"
    )

# Add product
def add_product(name, price, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)", (name, price, stock))
    conn.commit()
    conn.close()

# View products
def view_products():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    return df

# Update stock
def update_stock(product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = stock - %s WHERE id=%s", (quantity, product_id))
    conn.commit()
    conn.close()

# Create bill
def create_bill(cart):
    conn = get_connection()
    cursor = conn.cursor()
    total = sum(item['price'] * item['quantity'] for item in cart)
    cursor.execute("INSERT INTO bills (bill_date, total_amount) VALUES (%s, %s)", (date.today(), total))
    bill_id = cursor.lastrowid
    for item in cart:
        cursor.execute("INSERT INTO bill_items (bill_id, product_id, quantity) VALUES (%s, %s, %s)",
                       (bill_id, item['id'], item['quantity']))
        update_stock(item['id'], item['quantity'])
    conn.commit()
    conn.close()
    return bill_id, total

# Daily sales summary
def daily_sales():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM bills WHERE bill_date=%s", conn, params=(date.today(),))
    conn.close()
    return df

# Streamlit UI
st.title("🛒 Shop Inventory & Billing System")
menu = ["Add Product", "View Products", "Billing", "Daily Sales"]
choice = st.sidebar.selectbox("Menu", menu)

if "cart" not in st.session_state:
    st.session_state.cart = []

if choice == "Add Product":
    st.subheader("Add New Product")
    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    stock = st.number_input("Stock", min_value=0)
    if st.button("Add"):
        add_product(name, price, stock)
        st.success("Product added successfully!")

elif choice == "View Products":
    st.subheader("Product List")
    df = view_products()
    st.dataframe(df)

elif choice == "Billing":
    st.subheader("Generate Bill")
    df = view_products()
    product_id = st.selectbox("Select Product", df["id"])
    quantity = st.number_input("Quantity", min_value=1)
    product = df[df["id"] == product_id].iloc[0]

    if st.button("Add to Cart"):
        if quantity <= product["stock"]:
            st.session_state.cart.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            })
            st.success(f"Added {quantity} x {product['name']} to cart")
        else:
            st.error("Not enough stock!")

    if st.session_state.cart:
        st.write("### Cart")
        cart_df = pd.DataFrame(st.session_state.cart)
        cart_df["Total"] = cart_df["price"] * cart_df["quantity"]
        st.dataframe(cart_df)

        bill_id, total = None, None
        if st.button("Generate Bill"):
            bill_id, total = create_bill(st.session_state.cart)
            st.success(f"Bill generated! Bill ID: {bill_id}")
            st.metric("Total Amount", f"{total:.2f}")
            # Download bill
            bill_text = cart_df.to_csv(index=False)
            st.download_button("Download Bill", bill_text, file_name=f"bill_{bill_id}.csv")

        # Clear cart after billing
        st.session_state.cart = []

elif choice == "Daily Sales":
    st.subheader("Daily Sales Summary")
    df = daily_sales()
    if not df.empty:
        st.dataframe(df)
        st.metric("Total Sales", f"{df['total_amount'].sum():.2f}")
    else:
        st.info("No sales today yet.")

