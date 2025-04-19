import streamlit as st
import pandas as pd

# File paths for Excel files
product_db_file = 'product_database.xlsx'
orders_file = 'orders.xlsx'

# Ensure product database structure
product_columns = ['Product Code', 'Product Name', 'Grams Used', 'Sale Price']
try:
    product_df = pd.read_excel(product_db_file)
except FileNotFoundError:
    product_df = pd.DataFrame(columns=product_columns)
    product_df.to_excel(product_db_file, index=False)

# Ensure orders file structure
order_columns = [
    'Customer Name', 'Product Code', 'Product Name', 'Filament Color',
    'Order Date', 'Delivery Date', 'Assigned To', 'Cost', 'Profit',
    'Is Printed', 'Is Delivered'
]
try:
    orders_df = pd.read_excel(orders_file)
    # Add missing columns if necessary
    for col in order_columns:
        if col not in orders_df.columns:
            orders_df[col] = None
except FileNotFoundError:
    orders_df = pd.DataFrame(columns=order_columns)
    orders_df.to_excel(orders_file, index=False)

# Streamlit App
st.title("Order Management System")

menu = st.sidebar.selectbox("Menu", ["Add Order", "Add Product", "View Orders", "View Products"])

if menu == "Add Order":
    st.header("Add New Order")

    # Form for adding order
    with st.form("add_order_form"):
        customer_name = st.text_input("Customer Name")
        product_code = st.selectbox("Product Code", product_df['Product Code'].tolist())
        filament_color = st.selectbox("Filament Color", ["Blue", "Pink", "White", "Black"])
        order_date = st.date_input("Order Date")
        delivery_date = st.date_input("Delivery Date")
        assigned_to = st.text_input("Assigned To")
        is_printed = st.checkbox("Is Printed")
        is_delivered = st.checkbox("Is Delivered")
        submit = st.form_submit_button("Add Order")

    if submit:
        # Fetch product details
        product = product_df.loc[product_df['Product Code'] == product_code]
        if product.empty:
            st.error("Error: Product not found. Please add the product first.")
        else:
            product_name = product['Product Name'].values[0]
            grams_used = product['Grams Used'].values[0]
            sale_price = product['Sale Price'].values[0]
            cost = grams_used * filament_color.lower()  # Assumes filament cost logic in dictionary (adjust as needed)
            profit = sale_price - cost

            # Automatically check "Is Printed" if "Is Delivered" is checked
            if is_delivered:
                is_printed = True

            # Add order to DataFrame
            new_order = {
                'Customer Name': customer_name,
                'Product Code': product_code,
                'Product Name': product_name,
                'Filament Color': filament_color,
                'Order Date': order_date,
                'Delivery Date': delivery_date,
                'Assigned To': assigned_to,
                'Cost': cost,
                'Profit': profit,
                'Is Printed': is_printed,
                'Is Delivered': is_delivered
            }
            orders_df = orders_df.append(new_order, ignore_index=True)
            orders_df.to_excel(orders_file, index=False)
            st.success("Order added successfully!")

elif menu == "Add Product":
    st.header("Add New Product")

    # Form for adding product
    with st.form("add_product_form"):
        product_code = st.text_input("Product Code")
        product_name = st.text_input("Product Name")
        grams_used = st.number_input("Grams Used", min_value=0.0)
        sale_price = st.number_input("Sale Price", min_value=0.0)
        submit = st.form_submit_button("Add Product")

    if submit:
        # Prevent duplicate product codes or names
        if product_code in product_df['Product Code'].values or product_name in product_df['Product Name'].values:
            st.error("Error: Product already exists.")
        else:
            new_product = {
                'Product Code': product_code,
                'Product Name': product_name,
                'Grams Used': grams_used,
                'Sale Price': sale_price
            }
            product_df = product_df.append(new_product, ignore_index=True)
            product_df.to_excel(product_db_file, index=False)
            st.success("Product added successfully!")

elif menu == "View Orders":
    st.header("View Orders")
    orders_df = pd.read_excel(orders_file)
    st.dataframe(orders_df)

elif menu == "View Products":
    st.header("View Products")
    product_df = pd.read_excel(product_db_file)
    st.dataframe(product_df)