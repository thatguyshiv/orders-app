import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd

# File paths for Excel files
product_db_file = 'product_database.xlsx'
orders_file = 'orders.xlsx'

# Predefined cost per gram for each filament color
filament_costs = {
    "Blue": 0.10,
    "Pink": 0.12,
    "White": 0.08,
    "Black": 0.11
}

# Ensure the orders DataFrame has the correct structure
order_columns = [
    'Customer Name', 'Product Code', 'Product Name', 'Filament Color',
    'Order Date', 'Delivery Date', 'Assigned To', 'Cost', 'Profit',
    'Is Printed', 'Is Delivered'
]

# Load product database
try:
    product_df = pd.read_excel(product_db_file)
except FileNotFoundError:
    product_df = pd.DataFrame(columns=['Product Code', 'Product Name', 'Grams Used', 'Sale Price'])

# Load orders and ensure correct columns
try:
    orders_df = pd.read_excel(orders_file)
    # Add missing columns if necessary
    for col in order_columns:
        if col not in orders_df.columns:
            orders_df[col] = None
except FileNotFoundError:
    orders_df = pd.DataFrame(columns=order_columns)


# Function to save a new product
def save_product(product_code, product_name, grams_used, sale_price):
    if product_code in product_df['Product Code'].values or product_name in product_df['Product Name'].values:
        result_label.config(
            text=f"Error: Product '{product_name}' or Code '{product_code}' already exists in the database.")
        return

    product_df.loc[len(product_df)] = [product_code, product_name, grams_used, sale_price]
    product_df.to_excel(product_db_file, index=False)
    result_label.config(text=f"Product '{product_name}' added successfully!")


# Function to handle adding a new product when not found
def add_new_product(product_code):
    add_product_window = tk.Toplevel(root)
    add_product_window.title("Add New Product")

    ttk.Label(add_product_window, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
    product_name_entry = ttk.Entry(add_product_window, width=25)
    product_name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(add_product_window, text="Grams Used").grid(row=1, column=0, padx=5, pady=5)
    grams_entry = ttk.Entry(add_product_window, width=25)
    grams_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(add_product_window, text="Sale Price").grid(row=2, column=0, padx=5, pady=5)
    sale_price_entry = ttk.Entry(add_product_window, width=25)
    sale_price_entry.grid(row=2, column=1, padx=5, pady=5)

    def save_and_close():
        product_name = product_name_entry.get()
        grams_used = float(grams_entry.get())
        sale_price = float(sale_price_entry.get())
        save_product(product_code, product_name, grams_used, sale_price)
        add_product_window.destroy()

    ttk.Button(add_product_window, text="Save", command=save_and_close).grid(row=3, columnspan=2, pady=10)


# Function to update "Is Printed" when "Is Delivered" is checked
def on_delivered_checked():
    if delivered_var.get():  # If "Is Delivered" is checked
        printed_var.set(True)  # Automatically check "Is Printed"


# Function to add a new order
def add_order():
    product_code = product_code_entry.get()
    product = product_df.loc[product_df['Product Code'] == product_code]

    if product.empty:
        result_label.config(text="Product not found. Please add it to the system.")
        add_new_product(product_code)
        return

    product_name = product['Product Name'].values[0]
    grams_used = product['Grams Used'].values[0]
    sale_price = product['Sale Price'].values[0]
    filament_color = color_combobox.get()
    order_date = order_date_entry.get_date()
    delivery_date = delivery_date_entry.get_date()
    assigned_to = printer_entry.get()

    filament_cost_per_gram = filament_costs.get(filament_color, 0.10)
    cost = filament_cost_per_gram * grams_used
    profit = sale_price - cost

    is_printed = printed_var.get()
    is_delivered = delivered_var.get()

    orders_df.loc[len(orders_df)] = [
        customer_name_entry.get(), product_code, product_name, filament_color,
        order_date, delivery_date, assigned_to, cost, profit,
        is_printed, is_delivered
    ]
    orders_df.to_excel(orders_file, index=False)

    result_label.config(text="Order added successfully.")
    reset_form()


# Function to reset the form fields
def reset_form():
    for entry in entry_frame.winfo_children():
        if isinstance(entry, ttk.Entry):
            entry.delete(0, tk.END)
    color_combobox.set('')
    printed_var.set(False)
    delivered_var.set(False)


# Tkinter GUI setup
root = tk.Tk()
root.title("Order Management System")

entry_frame = ttk.LabelFrame(root, text="New Order")
entry_frame.pack(fill="x", padx=10, pady=5)

fields = ["Customer Name", "Product Code", "Printer"]
entries = {}

for idx, field in enumerate(fields):
    label = ttk.Label(entry_frame, text=field)
    label.grid(row=idx, column=0, padx=5, pady=5)
    entry = ttk.Entry(entry_frame, width=25)
    entry.grid(row=idx, column=1, padx=5, pady=5)
    entries[field] = entry

customer_name_entry = entries["Customer Name"]
product_code_entry = entries["Product Code"]
printer_entry = entries["Printer"]

color_label = ttk.Label(entry_frame, text="Filament Color")
color_label.grid(row=len(fields), column=0, padx=5, pady=5)
color_combobox = ttk.Combobox(entry_frame, values=["Blue", "Pink", "White", "Black"], state="readonly", width=23)
color_combobox.grid(row=len(fields), column=1, padx=5, pady=5)

order_date_label = ttk.Label(entry_frame, text="Order Date")
order_date_label.grid(row=len(fields) + 1, column=0, padx=5, pady=5)
order_date_entry = DateEntry(entry_frame, width=23, background="darkblue", foreground="white",
                             date_pattern="yyyy-mm-dd")
order_date_entry.grid(row=len(fields) + 1, column=1, padx=5, pady=5)

delivery_date_label = ttk.Label(entry_frame, text="Delivery Date")
delivery_date_label.grid(row=len(fields) + 2, column=0, padx=5, pady=5)
delivery_date_entry = DateEntry(entry_frame, width=23, background="darkblue", foreground="white",
                                date_pattern="yyyy-mm-dd")
delivery_date_entry.grid(row=len(fields) + 2, column=1, padx=5, pady=5)

printed_var = tk.BooleanVar(value=False)
delivered_var = tk.BooleanVar(value=False)

printed_checkbox = ttk.Checkbutton(entry_frame, text="Is Printed", variable=printed_var)
printed_checkbox.grid(row=len(fields) + 3, column=0, padx=5, pady=5)

delivered_checkbox = ttk.Checkbutton(entry_frame, text="Is Delivered", variable=delivered_var,
                                     command=on_delivered_checked)
delivered_checkbox.grid(row=len(fields) + 3, column=1, padx=5, pady=5)

add_order_button = ttk.Button(entry_frame, text="Add Order", command=add_order)
add_order_button.grid(row=len(fields) + 4, columnspan=2, pady=10)

result_label = ttk.Label(root, text="")
result_label.pack(pady=5)

root.mainloop()