"""
Sales Module with GST Support (India) - Multi-item orders
Save as: sales_module.py
NOTE: This is Part 1 - Customers and Sales Orders
See Part 2 for Invoices and Reports
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class SalesModule:
    def __init__(self, notebook, db, app):
        self.notebook = notebook
        self.db = db
        self.app = app
        self.create_customers_tab()
        self.create_sales_order_tab()
        self.create_invoices_tab()
        self.create_sales_reports_tab()
    
    def refresh_all(self):
        self.refresh_customers()
        self.refresh_sales_orders()
        self.refresh_invoices()
        self.refresh_sales_reports()
    
    def calculate_gst_price(self, rate, gst_percent):
        """Calculate final price from rate and GST"""
        gst_amount = (rate * gst_percent) / 100
        final_price = rate + gst_amount
        return gst_amount, final_price
    
    # ==================== CUSTOMERS TAB ====================
    
    def create_customers_tab(self):
        cust_frame = ttk.Frame(self.notebook)
        self.notebook.add(cust_frame, text="👥 Customers")
        top_btn_frame = ttk.Frame(cust_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Add", command=self.add_customer).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit", command=self.edit_customer).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete", command=self.delete_customer).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_customers).pack(side='right', padx=3)
        columns = ("ID", "Name", "Contact", "Phone", "Email", "GSTIN", "Credit Limit", "Terms")
        self.cust_tree = ttk.Treeview(cust_frame, columns=columns, show='headings', height=25)
        widths = [40, 130, 110, 90, 140, 140, 90, 100]
        for i, col in enumerate(columns):
            self.cust_tree.heading(col, text=col)
            self.cust_tree.column(col, width=widths[i])
        self.cust_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(cust_frame, orient='vertical', command=self.cust_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.cust_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_customers()
    
    def refresh_customers(self):
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        self.db.execute("SELECT customer_id, name, contact_person, phone, email, gstin, credit_limit, payment_terms FROM Customers")
        for row in self.db.fetchall():
            display_row = list(row[:6]) + [f"₹{row[6]:.2f}" if row[6] else "₹0.00"] + [row[7]]
            self.cust_tree.insert('', 'end', values=display_row)
    
    def add_customer(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Customer")
        dialog.geometry("500x450")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = [("Customer Name:*", "name"), ("Contact Person:", "contact"), ("Phone:", "phone"),
            ("Email:", "email"), ("Address:", "address"), ("GSTIN:", "gstin"), 
            ("Credit Limit (₹):", "credit"), ("Payment Terms:", "terms")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=35)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[key] = entry
        
        def save():
            try:
                if not entries["name"].get().strip():
                    messagebox.showerror("Error", "Customer name required")
                    return
                credit = 0
                if entries["credit"].get().strip():
                    try:
                        credit = float(entries["credit"].get())
                        if credit < 0:
                            messagebox.showerror("Error", "Credit limit cannot be negative")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Invalid credit limit")
                        return
                self.db.execute("INSERT INTO Customers (name, contact_person, phone, email, address, gstin, credit_limit, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (entries["name"].get().strip(), entries["contact"].get(), entries["phone"].get(),
                     entries["email"].get(), entries["address"].get(), entries["gstin"].get(), credit, entries["terms"].get()))
                self.db.commit()
                messagebox.showinfo("Success", "Customer added!")
                dialog.destroy()
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_customer(self):
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a customer")
            return
        customer_id = self.cust_tree.item(selected[0])['values'][0]
        self.db.execute("SELECT name, contact_person, phone, email, address, gstin, credit_limit, payment_terms FROM Customers WHERE customer_id = ?", (customer_id,))
        data = self.db.fetchone()
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Customer")
        dialog.geometry("500x450")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = ["Name:", "Contact:", "Phone:", "Email:", "Address:", "GSTIN:", "Credit (₹):", "Terms:"]
        entries = []
        for i, (field, value) in enumerate(zip(fields, data)):
            ttk.Label(dialog, text=field).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=35)
            entry.insert(0, value or "")
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries.append(entry)
        
        def update():
            try:
                if not entries[0].get().strip():
                    messagebox.showerror("Error", "Name required")
                    return
                credit = float(entries[6].get()) if entries[6].get() else 0
                if credit < 0:
                    messagebox.showerror("Error", "Credit cannot be negative")
                    return
                self.db.execute("UPDATE Customers SET name=?, contact_person=?, phone=?, email=?, address=?, gstin=?, credit_limit=?, payment_terms=? WHERE customer_id=?",
                    (entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(), entries[4].get(), entries[5].get(), credit, entries[7].get(), customer_id))
                self.db.commit()
                messagebox.showinfo("Success", "Updated!")
                dialog.destroy()
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_customer(self):
        selected = self.cust_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a customer")
            return
        customer_id, name = self.cust_tree.item(selected[0])['values'][0], self.cust_tree.item(selected[0])['values'][1]
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE customer_id = ?", (customer_id,))
        so_count = self.db.fetchone()[0]
        self.db.execute("SELECT COUNT(*) FROM Invoices WHERE customer_id = ?", (customer_id,))
        inv_count = self.db.fetchone()[0]
        if so_count > 0 or inv_count > 0:
            msg = f"Cannot delete '{name}'\n\nReferenced in:\n"
            if so_count > 0: msg += f"- {so_count} Sales Order(s)\n"
            if inv_count > 0: msg += f"- {inv_count} Invoice(s)\n"
            msg += "\nData integrity protected."
            messagebox.showerror("Cannot Delete", msg)
            return
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            try:
                self.db.execute("DELETE FROM Customers WHERE customer_id = ?", (customer_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Deleted!")
                self.refresh_customers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    # ==================== SALES ORDERS TAB ====================
    
    def create_sales_order_tab(self):
        so_frame = ttk.Frame(self.notebook)
        self.notebook.add(so_frame, text="🛍️ Sales Orders")
        top_btn_frame = ttk.Frame(so_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Create SO", command=self.create_sales_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_so_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete SO", command=self.delete_sales_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="📄 Generate Invoice", command=self.generate_invoice_from_so).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_sales_orders).pack(side='right', padx=3)
        columns = ("SO#", "Customer", "Order Date", "Delivery", "Status", "Subtotal", "GST", "Total", "Items")
        self.so_tree = ttk.Treeview(so_frame, columns=columns, show='headings', height=25)
        widths = [50, 130, 90, 90, 80, 80, 70, 90, 50]
        for i, col in enumerate(columns):
            self.so_tree.heading(col, text=col)
            self.so_tree.column(col, width=widths[i])
        self.so_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(so_frame, orient='vertical', command=self.so_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.so_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_sales_orders()
    
    def refresh_sales_orders(self):
        for item in self.so_tree.get_children():
            self.so_tree.delete(item)
        self.db.execute('''SELECT so.so_number, c.name, so.order_date, so.delivery_date, so.status, 
            so.subtotal, so.total_gst, so.total_amount,
            (SELECT COUNT(*) FROM Sales_Order_Items WHERE so_number = so.so_number) as item_count
            FROM Sales_Orders so JOIN Customers c ON so.customer_id = c.customer_id ORDER BY so.so_number''')
        for row in self.db.fetchall():
            display_row = (row[0], row[1], row[2], row[3], row[4], 
                          f"₹{row[5]:.2f}", f"₹{row[6]:.2f}", f"₹{row[7]:.2f}", row[8])
            self.so_tree.insert('', 'end', values=display_row)
    
    def create_sales_order(self):
        self.db.execute("SELECT COUNT(*) FROM Customers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add customers first")
            return
        self.db.execute("SELECT COUNT(*) FROM Items WHERE item_id IN (SELECT item_id FROM Inventory WHERE quantity_on_hand > 0)")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "No items in stock!")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create Sales Order - Multi-Item (with GST)")
        dialog.geometry("950x750")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Customer
        ttk.Label(dialog, text="Customer:*", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.db.execute("SELECT customer_id, name, gstin FROM Customers ORDER BY name")
        customers = self.db.fetchall()
        customer_dict = {f"{c[1]} (GSTIN: {c[2] or 'N/A'})": c[0] for c in customers}
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(dialog, textvariable=customer_var, values=list(customer_dict.keys()), width=50, state='readonly')
        customer_combo.grid(row=0, column=1, padx=10, pady=10, columnspan=3)
        
        # Delivery Date
        ttk.Label(dialog, text="Delivery Date (YYYY-MM-DD):*", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        delivery_entry = ttk.Entry(dialog, width=52)
        delivery_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
        delivery_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=3)
        
        # Item Selection
        ttk.Label(dialog, text="Add Items:", font=('Arial', 11, 'bold')).grid(row=2, column=0, padx=10, pady=(20, 10), sticky='w', columnspan=4)
        item_frame = ttk.LabelFrame(dialog, text="Item Selection", padding=10)
        item_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='ew')
        
        ttk.Label(item_frame, text="Item:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.db.execute('''SELECT i.item_id, i.name, i.selling_rate, i.selling_gst_percent, i.selling_price, inv.quantity_on_hand
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE inv.quantity_on_hand > 0 ORDER BY i.name''')
        items = self.db.fetchall()
        item_dict = {f"{i[1]} (Rate: ₹{i[2]:.2f} + {i[3]:.1f}% GST = ₹{i[4]:.2f}) [Stock: {i[5]}]": (i[0], i[2], i[3], i[5]) for i in items}
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(item_frame, textvariable=item_var, values=list(item_dict.keys()), width=60, state='readonly')
        item_combo.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        ttk.Label(item_frame, text="Qty:").grid(row=0, column=3, padx=5, pady=5)
        qty_entry = ttk.Entry(item_frame, width=10)
        qty_entry.grid(row=0, column=4, padx=5, pady=5)
        
        stock_label = ttk.Label(item_frame, text="", foreground="blue", font=('Arial', 9))
        stock_label.grid(row=1, column=0, columnspan=7, pady=5)
        
        selected_items = []
        
        def on_item_select(event):
            if item_var.get():
                _, _, _, stock = item_dict[item_var.get()]
                stock_label.config(text=f"Available: {stock} units")
        
        item_combo.bind('<<ComboboxSelected>>', on_item_select)
        
        def add_item():
            if not item_var.get():
                messagebox.showwarning("Warning", "Select an item")
                return
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showerror("Error", "Quantity must be positive")
                    return
                item_id, rate, gst_percent, stock = item_dict[item_var.get()]
                if qty > stock:
                    messagebox.showerror("Error", f"Insufficient stock! Available: {stock}")
                    return
                item_name = item_var.get().split(' (Rate:')[0]
                
                for existing in selected_items:
                    if existing[0] == item_id:
                        messagebox.showwarning("Warning", "Item already added")
                        return
                
                gst_amt, total = self.calculate_gst_price(rate * qty, gst_percent)
                selected_items.append((item_id, item_name, qty, rate, gst_percent, gst_amt, total, stock))
                items_tree.insert('', 'end', values=(item_name, qty, f"₹{rate:.2f}", f"{gst_percent:.1f}%", f"₹{gst_amt:.2f}", f"₹{total:.2f}"))
                update_total()
                item_var.set('')
                qty_entry.delete(0, tk.END)
                stock_label.config(text="")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity")
        
        def remove_item():
            selected = items_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select item to remove")
                return
            idx = items_tree.index(selected[0])
            selected_items.pop(idx)
            items_tree.delete(selected[0])
            update_total()
        
        def update_total():
            subtotal = sum(item[3] * item[2] for item in selected_items)
            total_gst = sum(item[5] for item in selected_items)
            total = sum(item[6] for item in selected_items)
            total_label.config(text=f"Subtotal: ₹{subtotal:.2f}  |  GST: ₹{total_gst:.2f}  |  Total: ₹{total:.2f}")
        
        ttk.Button(item_frame, text="➕ Add", command=add_item).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(item_frame, text="➖ Remove", command=remove_item).grid(row=0, column=6, padx=5, pady=5)
        
        # Items List
        list_frame = ttk.LabelFrame(dialog, text="Items in Order", padding=10)
        list_frame.grid(row=4, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')
        columns = ("Item", "Qty", "Rate", "GST%", "GST Amt", "Total")
        items_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        col_widths = [300, 60, 80, 60, 80, 100]
        for i, col in enumerate(columns):
            items_tree.heading(col, text=col)
            items_tree.column(col, width=col_widths[i])
        items_tree.pack(fill='both', expand=True)
        
        total_label = ttk.Label(dialog, text="Subtotal: ₹0.00  |  GST: ₹0.00  |  Total: ₹0.00", font=('Arial', 11, 'bold'), foreground='blue')
        total_label.grid(row=5, column=0, columnspan=4, pady=10)
        
        def save_so():
            try:
                if not customer_var.get():
                    messagebox.showerror("Error", "Select a customer")
                    return
                if not delivery_entry.get().strip():
                    messagebox.showerror("Error", "Enter delivery date")
                    return
                if not selected_items:
                    messagebox.showerror("Error", "Add at least one item")
                    return
                
                customer_id = customer_dict[customer_var.get()]
                
                # Verify stock again
                for item_id, name, qty, rate, gst_percent, gst_amt, total, original_stock in selected_items:
                    self.db.execute("SELECT quantity_on_hand FROM Inventory WHERE item_id = ?", (item_id,))
                    current_stock = self.db.fetchone()[0]
                    if qty > current_stock:
                        messagebox.showerror("Error", f"Stock changed! {name} now has only {current_stock} units")
                        return
                
                subtotal = sum(item[3] * item[2] for item in selected_items)
                total_gst = sum(item[5] for item in selected_items)
                total_amount = sum(item[6] for item in selected_items)
                
                # Create SO
                self.db.execute("INSERT INTO Sales_Orders (customer_id, order_date, delivery_date, status, subtotal, total_gst, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (customer_id, datetime.now().date(), delivery_entry.get(), "Completed", subtotal, total_gst, total_amount))
                so_number = self.db.lastrowid()
                
                # Add items and reduce inventory
                for item_id, name, qty, rate, gst_percent, gst_amt, total, stock in selected_items:
                    self.db.execute("INSERT INTO Sales_Order_Items (so_number, item_id, quantity, rate, gst_percent, gst_amount, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (so_number, item_id, qty, rate, gst_percent, gst_amt, total))
                    self.db.execute("UPDATE Inventory SET quantity_on_hand = quantity_on_hand - ?, last_updated = ? WHERE item_id = ?",
                        (qty, datetime.now(), item_id))
                
                self.db.commit()
                messagebox.showinfo("Success", f"SO #{so_number} created!\n\nItems: {len(selected_items)}\nSubtotal: ₹{subtotal:.2f}\nGST: ₹{total_gst:.2f}\nTotal: ₹{total_amount:.2f}\n\nInventory updated.")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=20)
        ttk.Button(btn_frame, text="✅ Create Sales Order", command=save_so, width=30).pack()
    
    def delete_sales_order(self):
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        values = self.so_tree.item(selected[0])['values']
        so_number = values[0]
        
        self.db.execute("SELECT COUNT(*) FROM Invoices WHERE so_number = ?", (so_number,))
        inv_count = self.db.fetchone()[0]
        if inv_count > 0:
            messagebox.showerror("Cannot Delete", f"SO #{so_number} has {inv_count} invoice(s).\nData integrity protected.")
            return
        
        if messagebox.askyesno("Confirm", f"Delete SO #{so_number}?\n\nNote: Inventory will NOT be restored."):
            try:
                self.db.execute("DELETE FROM Sales_Order_Items WHERE so_number = ?", (so_number,))
                self.db.execute("DELETE FROM Sales_Orders WHERE so_number = ?", (so_number,))
                self.db.commit()
                messagebox.showinfo("Success", f"SO #{so_number} deleted!")
                self.refresh_sales_orders()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def view_so_details(self):
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        values = self.so_tree.item(selected[0])['values']
        so_number = values[0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"SO #{so_number} Details")
        dialog.geometry("1000x600")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        self.db.execute('''SELECT so.so_number, c.name, c.gstin, so.order_date, so.delivery_date, 
            so.status, so.subtotal, so.total_gst, so.total_amount
            FROM Sales_Orders so JOIN Customers c ON so.customer_id = c.customer_id WHERE so.so_number = ?''', (so_number,))
        so_info = self.db.fetchone()
        
        info_frame = ttk.LabelFrame(dialog, text="Order Information", padding=15)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        labels = [
            f"SO Number: {so_info[0]}",
            f"Customer: {so_info[1]}",
            f"GSTIN: {so_info[2] or 'N/A'}",
            f"Order Date: {so_info[3]}",
            f"Delivery Date: {so_info[4]}",
            f"Status: {so_info[5]}"
        ]
        
        for i, text in enumerate(labels):
            ttk.Label(info_frame, text=text, font=('Arial', 10)).grid(row=i//2, column=i%2, sticky='w', padx=20, pady=5)
        
        # Amount summary
        summary_frame = ttk.LabelFrame(dialog, text="Amount Summary", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(summary_frame, text=f"Subtotal (Before GST):", font=('Arial', 10)).grid(row=0, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{so_info[6]:.2f}", font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Label(summary_frame, text=f"Total GST:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{so_info[7]:.2f}", font=('Arial', 10, 'bold'), foreground='blue').grid(row=1, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Separator(summary_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(summary_frame, text=f"Total Amount:", font=('Arial', 11, 'bold')).grid(row=3, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{so_info[8]:.2f}", font=('Arial', 11, 'bold'), foreground='green').grid(row=3, column=1, sticky='e', padx=10, pady=3)
        
        # Items
        items_frame = ttk.LabelFrame(dialog, text="Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Qty", "Rate", "GST%", "GST Amount", "Total Price")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        col_widths = [300, 70, 100, 80, 120, 120]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=col_widths[i])
        tree.pack(fill='both', expand=True)
        
        self.db.execute('''SELECT i.name, soi.quantity, soi.rate, soi.gst_percent, soi.gst_amount, soi.total_price
            FROM Sales_Order_Items soi JOIN Items i ON soi.item_id = i.item_id WHERE soi.so_number = ?''', (so_number,))
        for row in self.db.fetchall():
            tree.insert('', 'end', values=(row[0], row[1], f"₹{row[2]:.2f}", f"{row[3]:.1f}%", f"₹{row[4]:.2f}", f"₹{row[5]:.2f}"))
    
    def generate_invoice_from_so(self):
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        values = self.so_tree.item(selected[0])['values']
        so_number = values[0]
        
        self.db.execute("SELECT invoice_id FROM Invoices WHERE so_number = ?", (so_number,))
        existing = self.db.fetchone()
        if existing:
            messagebox.showinfo("Info", f"Invoice #{existing[0]} already exists")
            return
        
        self.db.execute("SELECT customer_id, subtotal, total_gst, total_amount FROM Sales_Orders WHERE so_number = ?", (so_number,))
        customer_id, subtotal, total_gst, total_amount = self.db.fetchone()
        invoice_date = datetime.now().date()
        due_date = (datetime.now() + timedelta(days=30)).date()
        
        self.db.execute("INSERT INTO Invoices (so_number, customer_id, invoice_date, due_date, subtotal, total_gst, total_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (so_number, customer_id, invoice_date, due_date, subtotal, total_gst, total_amount, "Unpaid"))
        invoice_id = self.db.lastrowid()
        self.db.commit()
        
        messagebox.showinfo("Success", f"Invoice #{invoice_id} generated!\n\nSubtotal: ₹{subtotal:.2f}\nGST: ₹{total_gst:.2f}\nTotal: ₹{total_amount:.2f}\n\nDue Date: {due_date}")
        self.refresh_invoices()
        self.refresh_sales_reports()
    
    # ==================== INVOICES TAB ====================
    
    def create_invoices_tab(self):
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="📄 Invoices")
        top_btn_frame = ttk.Frame(inv_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="💰 Mark Paid", command=self.mark_invoice_paid).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_invoice_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete Invoice", command=self.delete_invoice).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_invoices).pack(side='right', padx=3)
        columns = ("Invoice#", "SO#", "Customer", "Invoice Date", "Due Date", "Subtotal", "GST", "Total", "Status")
        self.invoice_tree = ttk.Treeview(inv_frame, columns=columns, show='headings', height=25)
        widths = [60, 50, 130, 90, 90, 80, 70, 90, 70]
        for i, col in enumerate(columns):
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=widths[i])
        self.invoice_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(inv_frame, orient='vertical', command=self.invoice_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_invoices()
    
    def refresh_invoices(self):
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        self.db.execute('''SELECT inv.invoice_id, inv.so_number, c.name, inv.invoice_date, inv.due_date, 
            inv.subtotal, inv.total_gst, inv.total_amount, inv.status
            FROM Invoices inv JOIN Customers c ON inv.customer_id = c.customer_id ORDER BY inv.invoice_id DESC''')
        for row in self.db.fetchall():
            display_row = (row[0], row[1], row[2], row[3], row[4], 
                          f"₹{row[5]:.2f}", f"₹{row[6]:.2f}", f"₹{row[7]:.2f}", row[8])
            tag = 'unpaid' if row[8] == 'Unpaid' else 'paid'
            self.invoice_tree.insert('', 'end', values=display_row, tags=(tag,))
        self.invoice_tree.tag_configure('unpaid', background='#ffe6e6')
        self.invoice_tree.tag_configure('paid', background='#e6ffe6')
    
    def mark_invoice_paid(self):
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice")
            return
        invoice_id = self.invoice_tree.item(selected[0])['values'][0]
        self.db.execute("UPDATE Invoices SET status = 'Paid' WHERE invoice_id = ?", (invoice_id,))
        self.db.commit()
        messagebox.showinfo("Success", f"Invoice #{invoice_id} marked as Paid!")
        self.refresh_invoices()
        self.refresh_sales_reports()
    
    def view_invoice_details(self):
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice")
            return
        invoice_values = self.invoice_tree.item(selected[0])['values']
        msg = f"Invoice Details\n\n"
        msg += f"Invoice #: {invoice_values[0]}\n"
        msg += f"Sales Order #: {invoice_values[1]}\n"
        msg += f"Customer: {invoice_values[2]}\n"
        msg += f"Invoice Date: {invoice_values[3]}\n"
        msg += f"Due Date: {invoice_values[4]}\n"
        msg += f"Subtotal: {invoice_values[5]}\n"
        msg += f"GST: {invoice_values[6]}\n"
        msg += f"Total Amount: {invoice_values[7]}\n"
        msg += f"Status: {invoice_values[8]}\n"
        messagebox.showinfo("Invoice Details", msg)
    
    def delete_invoice(self):
        selected = self.invoice_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice")
            return
        invoice_id = self.invoice_tree.item(selected[0])['values'][0]
        status = self.invoice_tree.item(selected[0])['values'][8]
        
        if status == "Paid":
            if not messagebox.askyesno("Warning", f"Invoice #{invoice_id} is marked as PAID.\n\nAre you sure you want to delete it?"):
                return
        
        if messagebox.askyesno("Confirm Delete", f"Delete Invoice #{invoice_id}?\n\nThis action cannot be undone."):
            try:
                self.db.execute("DELETE FROM Invoices WHERE invoice_id = ?", (invoice_id,))
                self.db.commit()
                messagebox.showinfo("Success", f"Invoice #{invoice_id} deleted!")
                self.refresh_invoices()
                self.refresh_sales_reports()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
    
    # ==================== SALES REPORTS TAB ====================
    
    def create_sales_reports_tab(self):
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📊 Sales Reports")
        
        # Summary frame
        summary_frame = ttk.LabelFrame(report_frame, text="Sales Summary", padding=20)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        self.total_sales_label = ttk.Label(summary_frame, text="Total Sales: ₹0.00", font=('Arial', 12, 'bold'))
        self.total_sales_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        self.total_gst_label = ttk.Label(summary_frame, text="Total GST Collected: ₹0.00", font=('Arial', 12))
        self.total_gst_label.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        
        self.total_orders_label = ttk.Label(summary_frame, text="Total Orders: 0", font=('Arial', 12))
        self.total_orders_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        
        self.completed_orders_label = ttk.Label(summary_frame, text="Completed: 0", font=('Arial', 12))
        self.completed_orders_label.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        self.unpaid_invoices_label = ttk.Label(summary_frame, text="Unpaid Invoices: 0 (₹0.00)", font=('Arial', 12))
        self.unpaid_invoices_label.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky='w')
        
        self.paid_invoices_label = ttk.Label(summary_frame, text="Paid Invoices: 0 (₹0.00)", font=('Arial', 12))
        self.paid_invoices_label.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky='w')
        
        ttk.Button(summary_frame, text="🔄 Refresh Reports", command=self.refresh_sales_reports).grid(row=4, column=0, columnspan=2, pady=15)
        
        # Top selling items frame
        items_frame = ttk.LabelFrame(report_frame, text="Top Selling Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Quantity Sold", "Revenue")
        self.top_items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.top_items_tree.heading(col, text=col)
            self.top_items_tree.column(col, width=250)
        
        self.top_items_tree.pack(fill='both', expand=True)
        
        self.refresh_sales_reports()
    
    def refresh_sales_reports(self):
        # Total sales amount
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0), COALESCE(SUM(total_gst), 0) FROM Sales_Orders")
        total_sales, total_gst = self.db.fetchone()
        self.total_sales_label.config(text=f"Total Sales: ₹{total_sales:.2f}")
        self.total_gst_label.config(text=f"Total GST Collected: ₹{total_gst:.2f}")
        
        # Total orders count
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders")
        total_orders = self.db.fetchone()[0]
        self.total_orders_label.config(text=f"Total Orders: {total_orders}")
        
        # Completed orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Completed'")
        completed = self.db.fetchone()[0]
        self.completed_orders_label.config(text=f"Completed: {completed}")
        
        # Unpaid invoices
        self.db.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM Invoices WHERE status = 'Unpaid'")
        unpaid_count, unpaid_amount = self.db.fetchone()
        self.unpaid_invoices_label.config(text=f"Unpaid Invoices: {unpaid_count} (₹{unpaid_amount:.2f})")
        
        # Paid invoices
        self.db.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM Invoices WHERE status = 'Paid'")
        paid_count, paid_amount = self.db.fetchone()
        self.paid_invoices_label.config(text=f"Paid Invoices: {paid_count} (₹{paid_amount:.2f})")
        
        # Top selling items
        for item in self.top_items_tree.get_children():
            self.top_items_tree.delete(item)
        
        self.db.execute('''
            SELECT i.name, SUM(soi.quantity) as total_qty, SUM(soi.total_price) as total_revenue
            FROM Sales_Order_Items soi
            JOIN Items i ON soi.item_id = i.item_id
            GROUP BY i.item_id, i.name
            ORDER BY total_qty DESC
            LIMIT 10
        ''')
        
        for row in self.db.fetchall():
            self.top_items_tree.insert('', 'end', values=(row[0], row[1], f"₹{row[2]:.2f}"))
