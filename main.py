import streamlit as st
import pandas as pd

# File paths for Excel files
product_db_file = 'product_database.xlsx'
orders_file = 'orders.xlsx'
filament_costs_file = 'filament_costs.csv'

# Default filament costs (if the file doesn't exist)
default_filament_costs = {
    "Blue": 0.10,
    "Pink": 0.12,
    "White": 0.08,
    "Black": 0.11
}

# Load filament costs
try:
    filament_costs_df = pd.read_csv(filament_costs_file)
    filament_costs = dict(zip(filament_costs_df['Color'], filament_costs_df['Cost']))
except FileNotFoundError:
    # Create default filament costs file
    filament_costs_df = pd.DataFrame(list(default_filament_costs.items()), columns=['Color', 'Cost'])
    filament_costs_df.to_csv(filament_costs_file, index=False)
    filament_costs = default_filament_costs

# Ensure product database structure
product_columns = ['Product Code', 'Product Name', 'Grams Used', 'Sale Price']
try:
    product_df = pd.read_excel(product_db_file)
except FileNotFoundError:
    product_df = pd.DataFrame(columns=product_columns)
    product_df.to_excel(product_db_file, index=False)

# Ensure orders database structure
order_columns = [
    'Customer Name', 'Product Code', 'Product Name', 'Filament Color',
    'Order Date', 'Delivery Date', 'Assigned To', 'Cost', 'Profit',
    'Is Printed', 'Is Delivered', 'Message'
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

menu = st.sidebar.selectbox("Menu", ["Add Order", "Add Product", "View Orders", "View Products", "Update Order", "Update Filament Costs"])

if menu == "Add Order":
    st.header("Add New Order")
    
    # Form for adding order
    with st.form("add_order_form"):
        customer_name = st.text_input("Customer Name")
        product_code = st.selectbox("Product Code", product_df['Product Code'].tolist())
        filament_color = st.selectbox("Filament Color", list(filament_costs.keys()))
        order_date = st.date_input("Order Date")
        delivery_date = st.date_input("Delivery Date")
        assigned_to = st.text_input("Assigned To")
        message = st.text_area("Message (optional)")
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
            filament_cost_per_gram = filament_costs.get(filament_color, 0.10)
            cost = grams_used * filament_cost_per_gram
            profit = sale_price - cost

            # Automatically check "Is Printed" if "Is Delivered" is checked
            if is_delivered:
                is_printed = True

            # Convert boolean values to "Y" or "N"
            is_printed = "Y" if is_printed else "N"
            is_delivered = "Y" if is_delivered else "N"

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
                'Is Delivered': is_delivered,
                'Message': message
            }
            orders_df = orders_df.append(new_order, ignore_index=True)
            orders_df.to_excel(orders_file, index=False)
            st.success("Order added successfully!")

elif menu == "Add Product":
    st.header("Add New Product")
    
    # Form for adding a new product
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
            # Add product to the product database
            new_product = {
                'Product Code': product_code,
                'Product Name': product_name,
                'Grams Used': grams_used,
                'Sale Price': sale_price
            }
            product_df = product_df.append(new_product, ignore_index=True)
            product_df.to_excel(product_db_file, index=False)
            st.success("Product added successfully!")

elif menu == "Update Order":
    st.header("Update Existing Order")

    # Search for an order
    search_by = st.radio("Search by", ["Product Code", "Customer Name"])
    search_value = st.text_input(f"Enter {search_by}")

    if st.button("Search"):
        # Filter the orders based on the search criteria
        if search_by == "Product Code":
            filtered_orders = orders_df.loc[orders_df['Product Code'] == search_value]
        else:
            filtered_orders = orders_df.loc[orders_df['Customer Name'] == search_value]
        
        if filtered_orders.empty:
            st.error("No orders found matching the search criteria.")
        else:
            st.write(f"Found {len(filtered_orders)} matching orders:")
            st.dataframe(filtered_orders)  # Display all matching orders
            
            # Add a dropdown to select an order
            order_index = st.selectbox(
                "Select an order to edit",
                options=filtered_orders.index,
                format_func=lambda i: f"{filtered_orders.loc[i, 'Customer Name']} - {filtered_orders.loc[i, 'Product Code']}"
            )

            # Load the selected order into an editable form
            order_to_update = orders_df.loc[order_index]
            with st.form("update_order_form"):
                st.write("Update the order details below:")
                customer_name = st.text_input("Customer Name", value=order_to_update["Customer Name"])
                product_code = st.text_input("Product Code", value=order_to_update["Product Code"], disabled=True)
                filament_color = st.text_input("Filament Color", value=order_to_update["Filament Color"])
                order_date = st.date_input("Order Date", value=pd.to_datetime(order_to_update["Order Date"]))
                delivery_date = st.date_input("Delivery Date", value=pd.to_datetime(order_to_update["Delivery Date"]))
                assigned_to = st.text_input("Assigned To", value=order_to_update["Assigned To"])
                message = st.text_area("Message", value=order_to_update["Message"])
                is_printed = st.checkbox("Is Printed", value=order_to_update["Is Printed"] == "Y")
                is_delivered = st.checkbox("Is Delivered", value=order_to_update["Is Delivered"] == "Y")
                update = st.form_submit_button("Update Order")

            if update:
                # Convert boolean values to "Y" or "N"
                is_printed = "Y" if is_printed else "N"
                is_delivered = "Y" if is_delivered else "N"

                # Update the DataFrame
                orders_df.at[order_index, "Customer Name"] = customer_name
                orders_df.at[order_index, "Filament Color"] = filament_color
                orders_df.at[order_index, "Order Date"] = order_date
                orders_df.at[order_index, "Delivery Date"] = delivery_date
                orders_df.at[order_index, "Assigned To"] = assigned_to
                orders_df.at[order_index, "Is Printed"] = is_printed
                orders_df.at[order_index, "Is Delivered"] = is_delivered
                orders_df.at[order_index, "Message"] = message

                # Save the updated orders to Excel
                orders_df.to_excel(orders_file, index=False)
                st.success("Order updated successfully!")

elif menu == "Update Filament Costs":
    st.header("Update Filament Costs")

    # Display current filament costs
    st.subheader("Current Filament Costs")
    filament_costs_df = pd.DataFrame(list(filament_costs.items()), columns=['Color', 'Cost'])
    st
