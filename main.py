import streamlit as st
import pandas as pd
import os
# File paths for Excel files
product_db_file = 'product_database.xlsx'
orders_file = 'orders.xlsx'
filament_costs_file = 'filament_costs.csv'

# Default filament costs
default_filament_costs = {
    "Blue": 0.10,
    "Pink": 0.12,
    "White": 0.08,
    "Black": 0.11
}

# Load filament costs
if os.path.exists(filament_costs_file):
    # If the file exists, load it
    try:
        filament_costs_df = pd.read_csv(filament_costs_file)
        filament_costs = dict(zip(filament_costs_df['Color'], filament_costs_df['Cost']))
    except Exception as e:
        st.error(f"Error reading {filament_costs_file}: {e}")
        # Handle the case where the file exists but is unreadable
        filament_costs_df = pd.DataFrame(list(default_filament_costs.items()), columns=['Color', 'Cost'])
else:
    # If the file doesn't exist, create it with the required defaults
    filament_costs_df = pd.DataFrame(list(default_filament_costs.items()), columns=['Color', 'Cost'])
    filament_costs_df.to_csv(filament_costs_file, index=False)
    filament_costs = default_filament_costs

# Ensure product database structure
product_columns = ['Product Code', 'Product Name', 'Grams Used', 'Sale Price']
import os  # Add this import to your script

if os.path.exists(product_db_file):
    # If the file exists, load it
    try:
        product_df = pd.read_excel(product_db_file)
    except Exception as e:
        st.error(f"Error reading {product_db_file}: {e}")
        # Handle the case where the file exists but is unreadable
        product_df = pd.DataFrame(columns=product_columns)
else:
    # If the file doesn't exist, create it with the required columns
    product_df = pd.DataFrame(columns=product_columns)
    product_df.to_excel(product_db_file, index=False)
# Ensure orders database structure
order_columns = [
    'Customer Name', 'Product Code', 'Product Name', 'Filament Color',
    'Order Date', 'Delivery Date', 'Assigned To', 'Cost', 'Profit',
    'Is Printed', 'Is Delivered', 'Message'
]
if os.path.exists(orders_file):
    # If the file exists, load it
    try:
        orders_df = pd.read_excel(orders_file)
    except Exception as e:
        st.error(f"Error reading {orders_file}: {e}")
        # Handle the case where the file exists but is unreadable
        orders_df = pd.DataFrame(columns=order_columns)
else:
    # If the file doesn't exist, create it with the required columns
    orders_df = pd.DataFrame(columns=order_columns)
    orders_df.to_excel(orders_file, index=False)
# Streamlit App
st.title("Order Management System")

menu = st.sidebar.selectbox("Menu", ["Add Order", "Add Product", "View Orders", "View Products", "Update Order", "Update Product", "Update Filament Costs"])

if menu == "Add Order":
    st.header("Add New Order")
    
    # Declare global orders_df
    global orders_df

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
            return  # Exit early to prevent further processing

        # Retrieve product details
        product_name = product['Product Name'].values[0]
        grams_used = product['Grams Used'].values[0]
        sale_price = product['Sale Price'].values[0]

        # Retrieve filament cost per gram (default to 0.10 if color is not found)
        filament_cost_per_gram = filament_costs.get(filament_color, 0.10)

        # Ensure all values are numeric
        try:
            grams_used = float(grams_used)
            filament_cost_per_gram = float(filament_cost_per_gram)
            sale_price = float(sale_price)
        except ValueError:
            st.error("Error: Invalid numeric values for calculations.")
            return

        # Calculate cost and profit
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
        new_order_df = pd.DataFrame([new_order])  # Create DataFrame from the new order dictionary
        orders_df = pd.concat([orders_df, new_order_df], ignore_index=True)  # Concatenate new order to existing DataFrame
        orders_df.to_excel(orders_file, index=False)  # Save the updated DataFrame to the Excel file
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
            new_product_df = pd.DataFrame([new_product])  # Create a DataFrame from the new product dictionary
            product_df = pd.concat([product_df, new_product_df], ignore_index=True)  # Concatenate to the existing DataFrame
            product_df.to_excel(product_db_file, index=False)  # Save the updated DataFrame to the Excel file
            st.success("Product added successfully!")

elif menu == "View Orders":
    st.header("View Orders")
    
    try:
        orders_df = pd.read_excel(orders_file)
        st.subheader("Order Details")
        st.dataframe(orders_df)  # Display orders in a table format
    except FileNotFoundError:
        st.error("The orders file is missing. Please add orders to create the file.")

elif menu == "View Products":
    st.header("View Products")
    
    try:
        product_df = pd.read_excel(product_db_file)
        st.subheader("Product Details")
        st.dataframe(product_df)  # Display products in a table format
    except FileNotFoundError:
        st.error("The product database file is missing. Please add products to create the file.")

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

elif menu == "Update Product":
    st.header("Update Existing Product")
    
    # Search for a product
    search_by = st.radio("Search by", ["Product Code", "Product Name"])
    search_value = st.text_input(f"Enter {search_by}")
    
    if st.button("Search"):
        # Filter the products based on the search criteria
        if search_by == "Product Code":
            filtered_products = product_df.loc[product_df['Product Code'] == search_value]
        else:
            filtered_products = product_df.loc[product_df['Product Name'] == search_value]
        
        if filtered_products.empty:
            st.error("No products found matching the search criteria.")
        else:
            st.write(f"Found {len(filtered_products)} matching products:")
            st.dataframe(filtered_products)  # Display all matching products
            
            # Add a dropdown to select a product
            product_index = st.selectbox(
                "Select a product to edit",
                options=filtered_products.index,
                format_func=lambda i: f"{filtered_products.loc[i, 'Product Name']} - {filtered_products.loc[i, 'Product Code']}"
            )
            
            # Load the selected product into an editable form
            product_to_update = product_df.loc[product_index]
            with st.form("update_product_form"):
                st.write("Update the product details below:")
                product_code = st.text_input("Product Code", value=product_to_update["Product Code"], disabled=True)
                product_name = st.text_input("Product Name", value=product_to_update["Product Name"])
                grams_used = st.number_input(
                    "Grams Used",
                    value=float(product_to_update["Grams Used"]),  # Ensure consistency
                    min_value=0.0
                )
                sale_price = st.number_input(
                    "Sale Price",
                    value=float(product_to_update["Sale Price"]),  # Ensure consistency
                    min_value=0.0
                )
                update = st.form_submit_button("Update Product")
            
            if update:
                # Update the DataFrame
                product_df.at[product_index, "Product Name"] = product_name
                product_df.at[product_index, "Grams Used"] = grams_used
                product_df.at[product_index, "Sale Price"] = sale_price

                # Save the updated products to Excel
                product_df.to_excel(product_db_file, index=False)
                st.success("Product updated successfully!")
elif menu == "Update Filament Costs":
    st.header("Update Filament Costs")

    # Display current filament costs
    st.subheader("Current Filament Costs")
    filament_costs_df = pd.DataFrame(list(filament_costs.items()), columns=['Color', 'Cost'])
    st.table(filament_costs_df)

    # Form for updating existing costs
    st.subheader("Update Existing Color Cost")
    with st.form("update_cost_form"):
        color_to_update = st.selectbox("Select a Color", list(filament_costs.keys()))
        new_cost = st.number_input(f"New Cost for {color_to_update}", min_value=0.0)
        update_cost = st.form_submit_button("Update Cost")
    
    if update_cost:
        if color_to_update:
            # Update the cost in the filament costs dictionary
            filament_costs[color_to_update] = new_cost
            # Save updated costs to file
            filament_costs_df = pd.DataFrame(list(filament_costs.items()), columns=['Color', 'Cost'])
            filament_costs_df.to_csv(filament_costs_file, index=False)
            st.success(f"The cost for {color_to_update} has been updated to {new_cost:.2f}!")

    # Form for adding a new color
    st.subheader("Add New Filament Color")
    with st.form("add_color_form"):
        new_color = st.text_input("New Color Name")
        new_color_cost = st.number_input(f"Cost for {new_color}", min_value=0.0)
        add_color = st.form_submit_button("Add New Color")

    if add_color:
        if new_color in filament_costs:
            st.error(f"The color {new_color} already exists.")
        else:
            # Add the new color and its cost
            filament_costs[new_color] = new_color_cost
            # Save updated costs to file
            filament_costs_df = pd.DataFrame(list(filament_costs.items()), columns=['Color', 'Cost'])
            filament_costs_df.to_csv(filament_costs_file, index=False)
            st.success(f"The new color {new_color} has been added with a cost of {new_color_cost:.2f}.")

