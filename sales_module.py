"""
Sales Module with GST Support (India)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class SalesModule:
    def __init__(self, notebook, db, app):
        self.notebook = notebook
        self.db = db
        self.app = app
        self.show_completed_sos = False
        self.create_customers_tab()
        self.create_sales_order_tab()
        self.create_delivery_tab()
        self.create_invoices_tab()
        self.create_gst_summary_tab()
        self.create_sales_reports_tab()
    
    def refresh_all(self):
        self.refresh_customers()
        self.refresh_sales_orders()
        self.refresh_delivery_history()
        self.refresh_invoices()
        self.refresh_gst_summary()
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
        dialog.geometry("445x400")
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
        dialog.geometry("445x400")
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
        self.notebook.add(so_frame, text="🛒 Sales Orders")
        top_btn_frame = ttk.Frame(so_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Create SO", command=self.create_sales_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_so_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit SO", command=self.edit_sales_order).pack(side='left', padx=3)  # NEW
        ttk.Button(top_btn_frame, text="🗑️ Delete SO", command=self.delete_sales_order).pack(side='left', padx=3)
        self.toggle_completed_so_btn = ttk.Button(top_btn_frame, text="👁️ Show Completed", command=self.toggle_completed_sales_orders)
        self.toggle_completed_so_btn.pack(side='left', padx=3)
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
    
    def toggle_completed_sales_orders(self):
        """Toggle between showing and hiding completed orders"""
        self.show_completed_sos = not self.show_completed_sos
        if self.show_completed_sos:
            self.toggle_completed_so_btn.config(text="🚫 Hide Completed")
        else:
            self.toggle_completed_so_btn.config(text="👁️ Show Completed")
        self.refresh_sales_orders()
    
    def refresh_sales_orders(self):
        for item in self.so_tree.get_children():
            self.so_tree.delete(item)
        
        # FIXED: Now properly filters completed orders
        if self.show_completed_sos:
            query = '''SELECT so.so_number, c.name, so.order_date, so.delivery_date, so.status, 
                so.subtotal, so.total_gst, so.total_amount,
                (SELECT COUNT(*) FROM Sales_Order_Items WHERE so_number = so.so_number) as item_count
                FROM Sales_Orders so JOIN Customers c ON so.customer_id = c.customer_id 
                ORDER BY so.so_number DESC'''
        else:
            query = '''SELECT so.so_number, c.name, so.order_date, so.delivery_date, so.status, 
                so.subtotal, so.total_gst, so.total_amount,
                (SELECT COUNT(*) FROM Sales_Order_Items WHERE so_number = so.so_number) as item_count
                FROM Sales_Orders so JOIN Customers c ON so.customer_id = c.customer_id 
                WHERE so.status != 'Delivered'
                ORDER BY so.so_number DESC'''
        
        self.db.execute(query)
        for row in self.db.fetchall():
            display_row = (row[0], row[1], row[2], row[3], row[4], 
                          f"₹{row[5]:.2f}", f"₹{row[6]:.2f}", f"₹{row[7]:.2f}", row[8])
            if row[4] == "Delivered":
                self.so_tree.insert('', 'end', values=display_row, tags=('completed',))
            else:
                self.so_tree.insert('', 'end', values=display_row)
        
        self.so_tree.tag_configure('completed', background='#e8e8e8', foreground='#666666')
    
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
                
                # CHANGED: Set status to "Pending" instead of "Completed"
                self.db.execute("INSERT INTO Sales_Orders (customer_id, order_date, delivery_date, status, subtotal, total_gst, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (customer_id, datetime.now().date(), delivery_entry.get(), "Pending", subtotal, total_gst, total_amount))
                so_number = self.db.lastrowid()
                
                # Add items - DON'T reduce inventory yet (wait for delivery)
                for item_id, name, qty, rate, gst_percent, gst_amt, total, stock in selected_items:
                    self.db.execute("INSERT INTO Sales_Order_Items (so_number, item_id, quantity, rate, gst_percent, gst_amount, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (so_number, item_id, qty, rate, gst_percent, gst_amt, total))
                
                self.db.commit()
                messagebox.showinfo("Success", f"SO #{so_number} created!\n\nItems: {len(selected_items)}\nSubtotal: ₹{subtotal:.2f}\nGST: ₹{total_gst:.2f}\nTotal: ₹{total_amount:.2f}\n\nStatus: Pending\nInventory will be reduced upon delivery.")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=20)
        ttk.Button(btn_frame, text="✅ Create Sales Order", command=save_so, width=30).pack()
    
    def edit_sales_order(self):
        """NEW: Edit a sales order before it's delivered"""
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        
        values = self.so_tree.item(selected[0])['values']
        so_number = values[0]
        status = values[4]
        
        # Only allow editing if not yet delivered
        if status in ["Delivered", "Partially Delivered"]:
            messagebox.showerror("Cannot Edit", "Cannot edit orders that have been delivered")
            return
        
        # Get SO details
        self.db.execute('''SELECT so.customer_id, c.name, so.delivery_date, so.subtotal, so.total_gst, so.total_amount
            FROM Sales_Orders so JOIN Customers c ON so.customer_id = c.customer_id WHERE so.so_number = ?''', (so_number,))
        so_data = self.db.fetchone()
        
        # Get items
        self.db.execute('''SELECT soi.item_id, i.name, soi.quantity, soi.rate, soi.gst_percent
            FROM Sales_Order_Items soi JOIN Items i ON soi.item_id = i.item_id WHERE soi.so_number = ?''', (so_number,))
        items_data = self.db.fetchall()
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Edit Sales Order #{so_number}")
        dialog.geometry("900x700")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        info_frame = ttk.LabelFrame(dialog, text="Order Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"SO #: {so_number} | Customer: {so_data[1]}", font=('Arial', 11, 'bold')).pack()
        
        ttk.Label(info_frame, text="Delivery Date:").pack(side='left', padx=10)
        delivery_entry = ttk.Entry(info_frame, width=20)
        delivery_entry.insert(0, so_data[2])
        delivery_entry.pack(side='left', padx=10)
        
        # Items list with edit capability
        items_frame = ttk.LabelFrame(dialog, text="Items (Double-click to edit quantity)", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Quantity", "Rate", "GST%", "Total")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=12)
        col_widths = [300, 100, 100, 80, 120]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=col_widths[i])
        tree.pack(fill='both', expand=True)
        # Load existing items
        item_data = {}  # {tree_id: (item_id, old_qty, rate, gst_percent)}
        for item_id, name, qty, rate, gst_percent in items_data:
            gst_amt, total = self.calculate_gst_price(rate * qty, gst_percent)
            tree_id = tree.insert("", "end", values=(name, qty, f"₹{rate:.2f}", f"{gst_percent:.1f}%", f"₹{total:.2f}"))
            item_data[tree_id] = (item_id, qty, rate, gst_percent)
        
        # Summary
        summary_label = ttk.Label(dialog, text="", font=('Arial', 10, 'bold'), foreground='blue')
        summary_label.pack(pady=5)
        
        def update_summary():
            subtotal = 0
            total_gst = 0
            total_amount = 0
            for tree_id in tree.get_children():
                qty = int(tree.item(tree_id)["values"][1])
                item_id, old_qty, rate, gst_percent = item_data[tree_id]
                gst_amt, item_total = self.calculate_gst_price(rate * qty, gst_percent)
                subtotal += rate * qty
                total_gst += gst_amt
                total_amount += item_total
            summary_label.config(text=f"Subtotal: ₹{subtotal:.2f} | GST: ₹{total_gst:.2f} | Total: ₹{total_amount:.2f}")
        
        update_summary()
        
        # Edit quantity on double-click
        current_entry = None
        
        def edit_qty(event):
            nonlocal current_entry
            if current_entry:
                try:
                    current_entry.destroy()
                except:
                    pass
                current_entry = None
            
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            
            row_id = tree.identify_row(event.y)
            col_id = tree.identify_column(event.x)
            
            if not row_id or col_id != "#2":  # Only quantity column
                return
            
            try:
                x, y, width, height = tree.bbox(row_id, col_id)
            except:
                return
            
            current_value = tree.item(row_id)["values"][1]
            
            entry = ttk.Entry(tree, font=('Arial', 10))
            entry.insert(0, str(current_value))
            entry.select_range(0, tk.END)
            entry.place(x=x, y=y, width=width, height=height)
            entry.focus()
            current_entry = entry
            
            def save_edit(event=None):
                nonlocal current_entry
                try:
                    new_qty = int(entry.get())
                    if new_qty <= 0:
                        messagebox.showerror("Error", "Quantity must be positive")
                        return
                    
                    # Check stock
                    item_id, old_qty, rate, gst_percent = item_data[row_id]
                    self.db.execute("SELECT quantity_on_hand FROM Inventory WHERE item_id = ?", (item_id,))
                    stock = self.db.fetchone()[0]
                    if new_qty > stock:
                        messagebox.showerror("Error", f"Insufficient stock! Available: {stock}")
                        return
                    
                    gst_amt, total = self.calculate_gst_price(rate * new_qty, gst_percent)
                    values = list(tree.item(row_id)["values"])
                    values[1] = new_qty
                    values[4] = f"₹{total:.2f}"
                    tree.item(row_id, values=values)
                    item_data[row_id] = (item_id, new_qty, rate, gst_percent)
                    update_summary()
                except ValueError:
                    messagebox.showerror("Error", "Enter valid quantity")
                finally:
                    entry.destroy()
                    current_entry = None
            
            def cancel_edit(event):
                nonlocal current_entry
                entry.destroy()
                current_entry = None
            
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", save_edit)
            entry.bind("<Escape>", cancel_edit)
        
        tree.bind("<Double-1>", edit_qty)
        
        def save_changes():
            try:
                # Update delivery date
                self.db.execute("UPDATE Sales_Orders SET delivery_date = ? WHERE so_number = ?",
                    (delivery_entry.get(), so_number))
                
                # Update items and recalculate totals
                self.db.execute("DELETE FROM Sales_Order_Items WHERE so_number = ?", (so_number,))
                
                subtotal = 0
                total_gst = 0
                total_amount = 0
                
                for tree_id in tree.get_children():
                    item_id, qty, rate, gst_percent = item_data[tree_id]
                    gst_amt, item_total = self.calculate_gst_price(rate * qty, gst_percent)
                    
                    self.db.execute("""INSERT INTO Sales_Order_Items 
                        (so_number, item_id, quantity, rate, gst_percent, gst_amount, total_price) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (so_number, item_id, qty, rate, gst_percent, gst_amt, item_total))
                    
                    subtotal += rate * qty
                    total_gst += gst_amt
                    total_amount += item_total
                
                # Update order totals
                self.db.execute("""UPDATE Sales_Orders 
                    SET subtotal = ?, total_gst = ?, total_amount = ? 
                    WHERE so_number = ?""",
                    (subtotal, total_gst, total_amount, so_number))
                
                self.db.commit()
                messagebox.showinfo("Success", f"SO #{so_number} updated!")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="💾 Save Changes", command=save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def delete_sales_order(self):
        """Delete a sales order"""
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a sales order")
            return
        
        values = self.so_tree.item(selected[0])['values']
        so_number = values[0]
        status = values[4]
        
        # Check if order has been delivered
        if status in ["Delivered", "Partially Delivered"]:
            messagebox.showerror("Cannot Delete", 
                f"SO #{so_number} has been delivered.\nData integrity protected.")
            return
        
        # Check if invoices exist
        self.db.execute("SELECT COUNT(*) FROM Invoices WHERE so_number = ?", (so_number,))
        inv_count = self.db.fetchone()[0]
        if inv_count > 0:
            messagebox.showerror("Cannot Delete", 
                f"SO #{so_number} has {inv_count} invoice(s).\nData integrity protected.")
            return
        
        if messagebox.askyesno("Confirm", f"Delete SO #{so_number} and all items?"):
            try:
                self.db.execute("DELETE FROM Sales_Order_Items WHERE so_number = ?", (so_number,))
                self.db.execute("DELETE FROM Sales_Orders WHERE so_number = ?", (so_number,))
                self.db.commit()
                messagebox.showinfo("Success", f"SO #{so_number} deleted!")
                self.refresh_sales_orders()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def view_so_details(self):
        """View sales order details"""
        selected = self.so_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a SO")
            return
        
        values = self.so_tree.item(selected[0])['values']
        so_number = values[0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"SO #{so_number} Details")
        dialog.geometry("1000x600")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Get SO info
        self.db.execute('''SELECT so.so_number, c.name, c.gstin, so.order_date, so.delivery_date, 
            so.status, so.subtotal, so.total_gst, so.total_amount
            FROM Sales_Orders so JOIN Customers c ON so.customer_id = c.customer_id 
            WHERE so.so_number = ?''', (so_number,))
        so_info = self.db.fetchone()
        
        # Info frame
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
            ttk.Label(info_frame, text=text, font=('Arial', 10)).grid(
                row=i//2, column=i%2, sticky='w', padx=20, pady=5)
        
        # Amount summary
        summary_frame = ttk.LabelFrame(dialog, text="Amount Summary", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(summary_frame, text="Subtotal (Before GST):", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{so_info[6]:.2f}", font=('Arial', 10, 'bold')).grid(
            row=0, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Label(summary_frame, text="Total GST:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{so_info[7]:.2f}", font=('Arial', 10, 'bold'), 
            foreground='blue').grid(row=1, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Separator(summary_frame, orient='horizontal').grid(
            row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Total Amount:", font=('Arial', 11, 'bold')).grid(
            row=3, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{so_info[8]:.2f}", font=('Arial', 11, 'bold'), 
            foreground='green').grid(row=3, column=1, sticky='e', padx=10, pady=3)
        
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
        
        self.db.execute('''SELECT i.name, soi.quantity, soi.rate, soi.gst_percent, 
            soi.gst_amount, soi.total_price
            FROM Sales_Order_Items soi JOIN Items i ON soi.item_id = i.item_id 
            WHERE soi.so_number = ?''', (so_number,))
        
        for row in self.db.fetchall():
            tree.insert('', 'end', values=(row[0], row[1], f"₹{row[2]:.2f}", 
                f"{row[3]:.1f}%", f"₹{row[4]:.2f}", f"₹{row[5]:.2f}"))
    
    # ==================== DELIVERY TAB ====================
    
    def create_delivery_tab(self):
        """Create delivery/dispatch tab"""
        del_frame = ttk.Frame(self.notebook)
        self.notebook.add(del_frame, text="🚚 Delivery")
        
        top_frame = ttk.Frame(del_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        ttk.Button(top_frame, text="➕ New Delivery", command=self.new_delivery).pack(side = 'left',padx = 2)
        ttk.Button(top_frame, text="✏️ Edit Delivery", command=self.edit_delivery).pack(side='left',padx = 2)
        
        history_frame = ttk.LabelFrame(del_frame, text="Delivery History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("SO#", "Customer", "Delivery Date", "Items", "Total Qty", "Status")
        self.delivery_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=20)
        
        widths = [60, 150, 120, 60, 100, 100]
        for i, col in enumerate(columns):
            self.delivery_tree.heading(col, text=col)
            self.delivery_tree.column(col, width=widths[i])
        
        self.delivery_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.delivery_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.delivery_tree.configure(yscrollcommand=scrollbar.set)
        
        self.delivery_tree.bind('<Double-1>', lambda e: self.view_delivery_details())
        
        self.refresh_delivery_history()
    
    def refresh_delivery_history(self):
        """Refresh delivery history"""
        for item in self.delivery_tree.get_children():
            self.delivery_tree.delete(item)
        
        # Get delivered/partially delivered orders
        self.db.execute('''
            SELECT so.so_number, c.name, so.delivery_date, 
                COUNT(DISTINCT soi.item_id) as item_count,
                SUM(soi.quantity) as total_qty,
                so.status
            FROM Sales_Orders so
            JOIN Customers c ON so.customer_id = c.customer_id
            JOIN Sales_Order_Items soi ON so.so_number = soi.so_number
            WHERE so.status IN ('Delivered', 'Partially Delivered')
            GROUP BY so.so_number
            ORDER BY so.so_number DESC
        ''')
        
        for row in self.db.fetchall():
            self.delivery_tree.insert('', 'end', values=row)
    
    def new_delivery(self):
        """Record a new delivery"""
        # Get pending sales orders
        self.db.execute('''SELECT so_number, order_date FROM Sales_Orders 
            WHERE status = 'Pending' ORDER BY so_number DESC''')
        pending_orders = self.db.fetchall()
        
        if not pending_orders:
            messagebox.showinfo("Info", "No pending orders to deliver")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Record Delivery")
        dialog.geometry("1000x700")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Select SO
        header_frame = ttk.LabelFrame(dialog, text="Select Sales Order", padding=10)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Sales Order:").pack(side='left', padx=10)
        
        so_dict = {f"SO #{so[0]} - {so[1]}": so[0] for so in pending_orders}
        so_var = tk.StringVar()
        so_combo = ttk.Combobox(header_frame, textvariable=so_var, 
            values=list(so_dict.keys()), width=40, state='readonly')
        so_combo.pack(side='left', padx=10)
        
        # Items frame
        items_frame = ttk.LabelFrame(dialog, text="Items to Deliver", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Ordered", "Deliver", "Stock")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        col_widths = [300, 100, 100, 100]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=col_widths[i])
        tree.pack(fill='both', expand=True)
        
        item_data = {}  # {tree_id: (item_id, ordered_qty, stock)}
        
        def load_so_items(event):
            """Load items when SO is selected"""
            if not so_var.get():
                return
            
            for item in tree.get_children():
                tree.delete(item)
            item_data.clear()
            
            so_number = so_dict[so_var.get()]
            
            self.db.execute('''
                SELECT soi.item_id, i.name, soi.quantity, inv.quantity_on_hand
                FROM Sales_Order_Items soi
                JOIN Items i ON soi.item_id = i.item_id
                JOIN Inventory inv ON i.item_id = inv.item_id
                WHERE soi.so_number = ?
            ''', (so_number,))
            
            for item_id, name, ordered, stock in self.db.fetchall():
                tree_id = tree.insert("", "end", values=(name, ordered, ordered, stock))
                item_data[tree_id] = (item_id, ordered, stock)
        
        so_combo.bind('<<ComboboxSelected>>', load_so_items)
        
        # Edit delivery quantity
        current_entry = None
        
        def edit_deliver_qty(event):
            nonlocal current_entry
            if current_entry:
                try:
                    current_entry.destroy()
                except:
                    pass
                current_entry = None
            
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            
            row_id = tree.identify_row(event.y)
            col_id = tree.identify_column(event.x)
            
            if not row_id or col_id != "#3":  # Only "Deliver" column
                return
            
            try:
                x, y, width, height = tree.bbox(row_id, col_id)
            except:
                return
            
            current_value = tree.item(row_id)["values"][2]
            
            entry = ttk.Entry(tree, font=('Arial', 10))
            entry.insert(0, str(current_value))
            entry.select_range(0, tk.END)
            entry.place(x=x, y=y, width=width, height=height)
            entry.focus()
            current_entry = entry
            
            def save_edit(event=None):
                nonlocal current_entry
                try:
                    new_qty = int(entry.get())
                    item_id, ordered, stock = item_data[row_id]
                    
                    if new_qty < 0:
                        messagebox.showerror("Error", "Quantity cannot be negative")
                        return
                    if new_qty > ordered:
                        messagebox.showerror("Error", f"Cannot deliver more than ordered ({ordered})")
                        return
                    if new_qty > stock:
                        messagebox.showerror("Error", f"Insufficient stock! Available: {stock}")
                        return
                    
                    values = list(tree.item(row_id)["values"])
                    values[2] = new_qty
                    tree.item(row_id, values=values)
                except ValueError:
                    messagebox.showerror("Error", "Enter valid quantity")
                finally:
                    entry.destroy()
                    current_entry = None
            
            def cancel_edit(event):
                nonlocal current_entry
                entry.destroy()
                current_entry = None
            
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", save_edit)
            entry.bind("<Escape>", cancel_edit)
        
        tree.bind("<Double-1>", edit_deliver_qty)
        
        ttk.Label(dialog, text="ℹ️ Double-click 'Deliver' column to edit quantity", 
            font=('Arial', 9), foreground='blue').pack(pady=5)
        
        def process_delivery():
            """Process the delivery and update inventory"""
            if not so_var.get():
                messagebox.showerror("Error", "Select a sales order")
                return
            
            if not tree.get_children():
                messagebox.showerror("Error", "No items to deliver")
                return
            
            try:
                so_number = so_dict[so_var.get()]
                
                total_delivered = 0
                items_fully_delivered = 0
                items_partially_delivered = 0
                
                for tree_id in tree.get_children():
                    values = tree.item(tree_id)["values"]
                    deliver_qty = int(values[2])
                    item_id, ordered_qty, stock = item_data[tree_id]
                    
                    if deliver_qty > stock:
                        messagebox.showerror("Error", f"{values[0]}: Insufficient stock!")
                        return
                    
                    if deliver_qty > 0:
                        # Reduce inventory
                        self.db.execute('''UPDATE Inventory 
                            SET quantity_on_hand = quantity_on_hand - ?,
                                last_updated = ?
                            WHERE item_id = ?''',
                            (deliver_qty, datetime.now(), item_id))
                        
                        total_delivered += deliver_qty
                        
                        if deliver_qty == ordered_qty:
                            items_fully_delivered += 1
                        else:
                            items_partially_delivered += 1
                
                # Update SO status
                if items_partially_delivered > 0 or total_delivered == 0:
                    new_status = "Partially Delivered"
                else:
                    new_status = "Delivered"
                
                self.db.execute('''UPDATE Sales_Orders 
                    SET status = ?, delivery_date = ?
                    WHERE so_number = ?''',
                    (new_status, datetime.now().date(), so_number))
                
                self.db.commit()
                
                msg = f"Delivery Recorded!\n\n"
                msg += f"SO #{so_number}\n"
                msg += f"Total Quantity Delivered: {total_delivered}\n"
                msg += f"Status: {new_status}"
                
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.app.refresh_all_tabs()
                
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="✅ Process Delivery", command=process_delivery).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def edit_delivery(self):
        """Edit/Complete a partial delivery"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a delivery record")
            return
        
        values = self.delivery_tree.item(selected[0])['values']
        so_number = values[0]
        status = values[5]
        
        # Only allow editing partially delivered orders
        if status == "Delivered":
            messagebox.showinfo("Info", f"SO #{so_number} is already fully delivered")
            return
        
        # Check if it's partially delivered
        self.db.execute("SELECT status FROM Sales_Orders WHERE so_number = ?", (so_number,))
        current_status = self.db.fetchone()[0]
        
        if current_status != "Partially Delivered":
            messagebox.showinfo("Info", "This order hasn't been partially delivered yet")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Complete Delivery - SO #{so_number}")
        dialog.geometry("900x650")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        info_frame = ttk.LabelFrame(dialog, text="Sales Order Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"SO #{so_number} - Status: {current_status}", 
            font=('Arial', 12, 'bold')).pack()
        ttk.Label(info_frame, text="Deliver remaining quantities to complete the order", 
            font=('Arial', 9), foreground='blue').pack(pady=5)
        
        # Get items with remaining quantities
        items_frame = ttk.LabelFrame(dialog, text="Items (Double-click 'Deliver' to edit)", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Ordered", "Remaining", "Deliver", "Stock")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=12)
        col_widths = [250, 100, 100, 100, 100]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=col_widths[i])
        tree.pack(fill='both', expand=True)
        
        # Load items - show remaining to deliver
        self.db.execute('''
            SELECT soi.item_id, i.name, soi.quantity, inv.quantity_on_hand
            FROM Sales_Order_Items soi
            JOIN Items i ON soi.item_id = i.item_id
            JOIN Inventory inv ON i.item_id = inv.item_id
            WHERE soi.so_number = ?
        ''', (so_number,))
        
        item_data = {}  # {tree_id: (item_id, ordered_qty, stock)}
        
        for item_id, name, ordered, stock in self.db.fetchall():
            # For partially delivered, assume we need to deliver the rest
            # In a real system, you'd track delivered quantities separately
            remaining = ordered  # Simplified: show full quantity as remaining
            tree_id = tree.insert("", "end", values=(name, ordered, remaining, remaining, stock))
            item_data[tree_id] = (item_id, ordered, stock)
        
        # Edit delivery quantity on double-click
        current_entry = None
        
        def edit_deliver_qty(event):
            nonlocal current_entry
            if current_entry:
                try:
                    current_entry.destroy()
                except:
                    pass
                current_entry = None
            
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            
            row_id = tree.identify_row(event.y)
            col_id = tree.identify_column(event.x)
            
            if not row_id or col_id != "#4":  # Only "Deliver" column
                return
            
            try:
                x, y, width, height = tree.bbox(row_id, col_id)
            except:
                return
            
            current_value = tree.item(row_id)["values"][3]
            
            entry = ttk.Entry(tree, font=('Arial', 10))
            entry.insert(0, str(current_value))
            entry.select_range(0, tk.END)
            entry.place(x=x, y=y, width=width, height=height)
            entry.focus()
            current_entry = entry
            
            def save_edit(event=None):
                nonlocal current_entry
                try:
                    new_qty = int(entry.get())
                    item_id, ordered, stock = item_data[row_id]
                    remaining = int(tree.item(row_id)["values"][2])
                    
                    if new_qty < 0:
                        messagebox.showerror("Error", "Quantity cannot be negative")
                        return
                    if new_qty > remaining:
                        messagebox.showerror("Error", f"Cannot deliver more than remaining ({remaining})")
                        return
                    if new_qty > stock:
                        messagebox.showerror("Error", f"Insufficient stock! Available: {stock}")
                        return
                    
                    values = list(tree.item(row_id)["values"])
                    values[3] = new_qty
                    tree.item(row_id, values=values)
                except ValueError:
                    messagebox.showerror("Error", "Enter valid quantity")
                finally:
                    entry.destroy()
                    current_entry = None
            
            def cancel_edit(event):
                nonlocal current_entry
                entry.destroy()
                current_entry = None
            
            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", save_edit)
            entry.bind("<Escape>", cancel_edit)
        
        tree.bind("<Double-1>", edit_deliver_qty)
        
        def complete_delivery():
            """Complete the remaining delivery"""
            try:
                # STEP 1: VALIDATE ALL ITEMS FIRST (before making any changes)
                items_to_deliver = []
                
                for tree_id in tree.get_children():
                    values = tree.item(tree_id)["values"]
                    deliver_qty = int(values[3])
                    remaining_qty = int(values[2])
                    item_id, ordered_qty, stock = item_data[tree_id]
                    
                    # Check stock BEFORE doing anything
                    if deliver_qty > stock:
                        messagebox.showerror("Error", f"{values[0]}: Insufficient stock! Available: {stock}")
                        return  # Exit without making ANY changes
                    
                    # Store validated items
                    items_to_deliver.append({
                        'item_id': item_id,
                        'item_name': values[0],
                        'deliver_qty': deliver_qty,
                        'remaining_qty': remaining_qty,
                        'ordered_qty': ordered_qty
                    })
                
                # STEP 2: ALL ITEMS VALIDATED - NOW UPDATE DATABASE
                total_delivered = 0
                all_items_complete = True
                
                for item_info in items_to_deliver:
                    if item_info['deliver_qty'] > 0:
                        # Reduce inventory
                        self.db.execute('''UPDATE Inventory 
                            SET quantity_on_hand = quantity_on_hand - ?,
                                last_updated = ?
                            WHERE item_id = ?''',
                            (item_info['deliver_qty'], datetime.now(), item_info['item_id']))
                        
                        total_delivered += item_info['deliver_qty']
                    
                    # Check if this item is fully delivered
                    if item_info['deliver_qty'] < item_info['remaining_qty']:
                        all_items_complete = False
                
                # Update SO status
                if all_items_complete and total_delivered > 0:
                    new_status = "Delivered"
                else:
                    new_status = "Partially Delivered"
                
                self.db.execute('''UPDATE Sales_Orders 
                    SET status = ?, delivery_date = ?
                    WHERE so_number = ?''',
                    (new_status, datetime.now().date(), so_number))
                
                self.db.commit()
                
                msg = f"Delivery Updated!\n\n"
                msg += f"SO #{so_number}\n"
                msg += f"Additional Quantity Delivered: {total_delivered}\n"
                msg += f"New Status: {new_status}"
                
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.app.refresh_all_tabs()
                
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="✅ Complete Delivery", command=complete_delivery).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def view_delivery_details(self):
        """View delivery details"""
        selected = self.delivery_tree.selection()
        if not selected:
            return
        
        values = self.delivery_tree.item(selected[0])['values']
        so_number = values[0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Delivery Details - SO #{so_number}")
        dialog.geometry("800x500")
        dialog.transient(self.app.root)
        
        # Info
        info_frame = ttk.LabelFrame(dialog, text="Delivery Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"SO #: {values[0]} | Customer: {values[1]} | Date: {values[2]}", 
            font=('Arial', 11, 'bold')).pack()
        
        # Items
        items_frame = ttk.LabelFrame(dialog, text="Delivered Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Quantity Delivered")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        tree.heading("Item", text="Item")
        tree.column("Item", width=400)
        tree.heading("Quantity Delivered", text="Quantity Delivered")
        tree.column("Quantity Delivered", width=200)
        tree.pack(fill='both', expand=True)
        
        self.db.execute('''SELECT i.name, soi.quantity
            FROM Sales_Order_Items soi
            JOIN Items i ON soi.item_id = i.item_id
            WHERE soi.so_number = ?''', (so_number,))
        
        for row in self.db.fetchall():
            tree.insert('', 'end', values=row)
            
            
    
    # ==================== GST SUMMARY TAB ====================
    
    def create_gst_summary_tab(self):
        """Create dedicated GST summary tab with improved UI"""
        gst_frame = ttk.Frame(self.notebook)
        self.notebook.add(gst_frame, text="💰 GST Summary")
    
        # Top frame with title and refresh
        top_frame = ttk.Frame(gst_frame)
        top_frame.pack(side='top', fill='x', padx=15, pady=15)

        ttk.Label(top_frame, text="GST Tax Summary & Liability", 
            font=('Arial', 18, 'bold')).pack(side='left', padx=10)
        ttk.Button(top_frame, text="🔄 Refresh", command=self.refresh_gst_summary).pack(side='right', padx=10)

        # Scrollable container
        canvas = tk.Canvas(gst_frame)
        scrollbar = ttk.Scrollbar(gst_frame, orient="vertical", command=canvas.yview)
        self.gst_scrollable_frame = ttk.Frame(canvas)

        self.gst_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=self.gst_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # Make scrollable frame expand to fill canvas width and height
        def configure_canvas_size(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", configure_canvas_size)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initial load
        self.refresh_gst_summary()

    def refresh_gst_summary(self):
        """Refresh GST summary with HORIZONTAL layout"""
        # Clear existing content
        for widget in self.gst_scrollable_frame.winfo_children():
            widget.destroy()

        # Get data
        self.db.execute('''
            SELECT 
                soi.gst_percent,
                COALESCE(SUM(soi.gst_amount), 0) as total_gst_collected,
                COALESCE(SUM(soi.rate * soi.quantity), 0) as total_base_amount,
                COUNT(DISTINCT so.so_number) as order_count,
                COUNT(*) as item_count
            FROM Sales_Order_Items soi
            JOIN Sales_Orders so ON soi.so_number = so.so_number
            GROUP BY soi.gst_percent
            ORDER BY soi.gst_percent
        ''')
        output_gst_data = {row[0]: {'gst': row[1], 'base': row[2], 'orders': row[3], 'items': row[4]} 
                           for row in self.db.fetchall()}

        self.db.execute('''
            SELECT 
                poi.gst_percent,
                COALESCE(SUM(poi.gst_amount), 0) as total_gst_paid,
                COALESCE(SUM(poi.rate * poi.quantity), 0) as total_base_amount,
                COUNT(DISTINCT po.po_number) as order_count,
                COUNT(*) as item_count
            FROM Purchase_Order_Items poi
            JOIN Purchase_Orders po ON poi.po_number = po.po_number
            GROUP BY poi.gst_percent
            ORDER BY poi.gst_percent
        ''')
        input_gst_data = {row[0]: {'gst': row[1], 'base': row[2], 'orders': row[3], 'items': row[4]} 
                          for row in self.db.fetchall()}

        all_gst_rates = sorted(set(list(output_gst_data.keys()) + list(input_gst_data.keys())))

        if all_gst_rates:
            # === QUICK SUMMARY - HORIZONTAL CARDS (4 cards in one row) ===
            total_output_gst = sum(d['gst'] for d in output_gst_data.values())
            total_input_gst = sum(d['gst'] for d in input_gst_data.values())
            net_gst = total_output_gst - total_input_gst
        
            summary_section = ttk.LabelFrame(self.gst_scrollable_frame, 
                text="📊 GST Quick Summary", padding=20)
            summary_section.pack(fill='x', pady=(0, 15), padx=10)
    
            summary_cards = ttk.Frame(summary_section)
            summary_cards.pack(fill='both', expand=True)
        
            # Configure grid for equal spacing
            for i in range(4):
                summary_cards.grid_columnconfigure(i, weight=1)
            summary_cards.grid_rowconfigure(0, weight=1)
        
            # Card 1: Output GST
            card1 = ttk.Frame(summary_cards, relief='solid', borderwidth=2)
            card1.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
            ttk.Label(card1, text="Output GST", font=('Arial', 10), 
                foreground='gray').pack(pady=(15, 5))
            ttk.Label(card1, text=f"₹{total_output_gst:,.2f}", font=('Arial', 16, 'bold'), 
                foreground='green').pack(pady=(0, 5))
            ttk.Label(card1, text="Collected from Sales", font=('Arial', 8), 
                foreground='gray').pack(pady=(0, 15))
    
            # Card 2: Input GST
            card2 = ttk.Frame(summary_cards, relief='solid', borderwidth=2)
            card2.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
            ttk.Label(card2, text="Input GST", font=('Arial', 10), 
                foreground='gray').pack(pady=(15, 5))
            ttk.Label(card2, text=f"₹{total_input_gst:,.2f}", font=('Arial', 16, 'bold'), 
                foreground='orange').pack(pady=(0, 5))
            ttk.Label(card2, text="Paid on Purchases", font=('Arial', 8), 
                foreground='gray').pack(pady=(0, 15))
    
            # Card 3: Net Liability
            card3 = ttk.Frame(summary_cards, relief='solid', borderwidth=2)
            card3.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
            ttk.Label(card3, text="Net GST Liability", font=('Arial', 10), 
                foreground='gray').pack(pady=(15, 5))
            net_color = '#dc3545' if net_gst > 0 else ('#28a745' if net_gst < 0 else '#17a2b8')
            ttk.Label(card3, text=f"₹{net_gst:,.2f}", font=('Arial', 16, 'bold'), 
                foreground=net_color).pack(pady=(0, 5))
            status_text = "To Pay" if net_gst > 0 else ("Refund" if net_gst < 0 else "Balanced")
            ttk.Label(card3, text=status_text, font=('Arial', 8), 
                foreground=net_color).pack(pady=(0, 15))
    
            # Card 4: Total Orders
            total_orders = sum(d['orders'] for d in output_gst_data.values())
            card4 = ttk.Frame(summary_cards, relief='solid', borderwidth=2)
            card4.grid(row=0, column=3, padx=10, pady=10, sticky='nsew')
            ttk.Label(card4, text="Sales Orders", font=('Arial', 10), 
                foreground='gray').pack(pady=(15, 5))
            ttk.Label(card4, text=str(total_orders), font=('Arial', 16, 'bold'), 
                foreground='blue').pack(pady=(0, 5))
            ttk.Label(card4, text="With GST", font=('Arial', 8), 
                foreground='gray').pack(pady=(0, 15))
    
            # === COLOR LEGEND - HORIZONTAL (one row) ===
            legend_frame = ttk.LabelFrame(self.gst_scrollable_frame, text="Color Legend", padding=10)
            legend_frame.pack(fill='x', pady=(0, 15), padx=10)
        
            legend_container = ttk.Frame(legend_frame)
            legend_container.pack()
    
            legend_items = [
                ("● 0%", '#666666'), ("● 1-5%", '#28a745'), ("● 6-12%", '#17a2b8'),
                ("● 13-18%", '#ffc107'), ("● 19%+", '#dc3545')
            ]
    
            for text, color in legend_items:
                ttk.Label(legend_container, text=text, font=('Arial', 10, 'bold'), 
                    foreground=color).pack(side='left', padx=15)
        
            # === TAX BRACKET COMPARISON - COMPACT TABLE ===
            comparison_section = ttk.LabelFrame(self.gst_scrollable_frame, 
                text="📊 Tax Bracket Comparison (Output vs Input)", padding=20)
            comparison_section.pack(fill='x', pady=(0, 15), padx=10)
    
            # Header row - SINGLE LINE
            header_frame = ttk.Frame(comparison_section)
            header_frame.pack(fill='x', pady=(0, 5))
    
            headers = [
                ("Rate", 10), ("Output GST", 15), ("Input GST", 15), 
                ("Net Liability", 15), ("Out Orders", 12), ("In Orders", 12)
            ]
    
            for text, width in headers:
                ttk.Label(header_frame, text=text, font=('Arial', 10, 'bold'), 
                    width=width).pack(side='left', padx=5)
    
            ttk.Separator(comparison_section, orient='horizontal').pack(fill='x', pady=3)
    
            # Data rows - COMPACT
            for gst_rate in all_gst_rates:
                output_gst_amt = output_gst_data.get(gst_rate, {}).get('gst', 0)
                input_gst_amt = input_gst_data.get(gst_rate, {}).get('gst', 0)
                net_bracket = output_gst_amt - input_gst_amt
                output_orders = output_gst_data.get(gst_rate, {}).get('orders', 0)
                input_orders = input_gst_data.get(gst_rate, {}).get('orders', 0)
        
                if output_gst_amt > 0 or input_gst_amt > 0:
                    color = self._get_gst_color(gst_rate)
            
                    row_frame = ttk.Frame(comparison_section)
                    row_frame.pack(fill='x', pady=2)
            
                    ttk.Label(row_frame, text=f"{gst_rate:.1f}%", 
                        font=('Arial', 10, 'bold'), foreground=color, width=10).pack(side='left', padx=5)
                    ttk.Label(row_frame, text=f"₹{output_gst_amt:,.2f}", 
                        font=('Arial', 10), width=15).pack(side='left', padx=5)
                    ttk.Label(row_frame, text=f"₹{input_gst_amt:,.2f}", 
                        font=('Arial', 10), width=15).pack(side='left', padx=5)
            
                    net_color = '#dc3545' if net_bracket > 0 else ('#28a745' if net_bracket < 0 else '#17a2b8')
                    ttk.Label(row_frame, text=f"₹{net_bracket:,.2f}", 
                        font=('Arial', 10, 'bold'), foreground=net_color, width=15).pack(side='left', padx=5)
            
                    ttk.Label(row_frame, text=str(output_orders), 
                        font=('Arial', 10), width=12).pack(side='left', padx=5)
                    ttk.Label(row_frame, text=str(input_orders), 
                        font=('Arial', 10), width=12).pack(side='left', padx=5)
    
            # === DETAILED BREAKDOWN - SIDE BY SIDE (Output and Input) ===
            details_section = ttk.LabelFrame(self.gst_scrollable_frame, 
                text="📋 Detailed Breakdown by Tax Rate", padding=15)
            details_section.pack(fill='both', expand=True, pady=(0, 15), padx=10)
    
            # Create two-column layout
            columns_frame = ttk.Frame(details_section)
            columns_frame.pack(fill='both', expand=True)
            
            # Configure columns
            columns_frame.grid_columnconfigure(0, weight=1)
            columns_frame.grid_columnconfigure(1, weight=1)
    
            # Output GST details (LEFT COLUMN)
            output_frame = ttk.LabelFrame(columns_frame, text="Output GST (Sales)", padding=10)
            output_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
    
            # Header for output
            out_header = ttk.Frame(output_frame)
            out_header.pack(fill='x', pady=(0, 5))
            ttk.Label(out_header, text="Rate", font=('Arial', 9, 'bold'), width=8).pack(side='left', padx=3)
            ttk.Label(out_header, text="Base", font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=3)
            ttk.Label(out_header, text="GST", font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=3)
            ttk.Label(out_header, text="Orders", font=('Arial', 9, 'bold'), width=8).pack(side='left', padx=3)
            ttk.Label(out_header, text="Items", font=('Arial', 9, 'bold'), width=8).pack(side='left', padx=3)
        
            ttk.Separator(output_frame, orient='horizontal').pack(fill='x', pady=3)
    
            for gst_rate in all_gst_rates:
                if gst_rate in output_gst_data:
                    data = output_gst_data[gst_rate]
                    color = self._get_gst_color(gst_rate)
                    row = ttk.Frame(output_frame)
                    row.pack(fill='x', pady=1)
            
                    ttk.Label(row, text=f"{gst_rate:.1f}%", font=('Arial', 9, 'bold'), 
                        foreground=color, width=8).pack(side='left', padx=3)
                    ttk.Label(row, text=f"₹{data['base']:,.0f}", 
                        font=('Arial', 9), width=12).pack(side='left', padx=3)
                    ttk.Label(row, text=f"₹{data['gst']:,.0f}", 
                        font=('Arial', 9, 'bold'), foreground=color, width=12).pack(side='left', padx=3)
                    ttk.Label(row, text=f"{data['orders']}", 
                        font=('Arial', 9), width=8).pack(side='left', padx=3)
                    ttk.Label(row, text=f"{data['items']}", 
                        font=('Arial', 9), width=8).pack(side='left', padx=3)
        
            # Input GST details (RIGHT COLUMN)
            input_frame = ttk.LabelFrame(columns_frame, text="Input GST (Purchases)", padding=10)
            input_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
    
            # Header for input
            in_header = ttk.Frame(input_frame)
            in_header.pack(fill='x', pady=(0, 5))
            ttk.Label(in_header, text="Rate", font=('Arial', 9, 'bold'), width=8).pack(side='left', padx=3)
            ttk.Label(in_header, text="Base", font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=3)
            ttk.Label(in_header, text="GST", font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=3)
            ttk.Label(in_header, text="Orders", font=('Arial', 9, 'bold'), width=8).pack(side='left', padx=3)
            ttk.Label(in_header, text="Items", font=('Arial', 9, 'bold'), width=8).pack(side='left', padx=3)
        
            ttk.Separator(input_frame, orient='horizontal').pack(fill='x', pady=3)
    
            for gst_rate in all_gst_rates:
                if gst_rate in input_gst_data:
                    data = input_gst_data[gst_rate]
                    color = self._get_gst_color(gst_rate)
                    row = ttk.Frame(input_frame)
                    row.pack(fill='x', pady=1)
            
                    ttk.Label(row, text=f"{gst_rate:.1f}%", font=('Arial', 9, 'bold'), 
                        foreground=color, width=8).pack(side='left', padx=3)
                    ttk.Label(row, text=f"₹{data['base']:,.0f}", 
                        font=('Arial', 9), width=12).pack(side='left', padx=3)
                    ttk.Label(row, text=f"₹{data['gst']:,.0f}", 
                        font=('Arial', 9, 'bold'), foreground=color, width=12).pack(side='left', padx=3)
                    ttk.Label(row, text=f"{data['orders']}", 
                        font=('Arial', 9), width=8).pack(side='left', padx=3)
                    ttk.Label(row, text=f"{data['items']}", 
                        font=('Arial', 9), width=8).pack(side='left', padx=3)
    
        else:
            # No data
            empty_frame = ttk.Frame(self.gst_scrollable_frame)
            empty_frame.pack(expand=True, fill='both', pady=100)
        
            ttk.Label(empty_frame, text="📊 No GST Data Available", 
                font=('Arial', 18, 'bold'), foreground='gray').pack(pady=15)
            ttk.Label(empty_frame, 
                text="Create sales and purchase orders to see GST analysis", 
                font=('Arial', 12), foreground='gray').pack(pady=8)

    def _get_gst_color(self, gst_rate):
        """Helper to get color for GST rate"""
        if gst_rate == 0:
            return '#666666'
        elif gst_rate <= 5:
            return '#28a745'
        elif gst_rate <= 12:
            return '#17a2b8'
        elif gst_rate <= 18:
            return '#ffc107'
        else:
            return '#dc3545'
    
    # ==================== INVOICES TAB ====================
    
    def create_invoices_tab(self):
        """Create invoices tab"""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="📄 Invoices")
        
        top_frame = ttk.Frame(inv_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Button(top_frame, text="➕ Generate Invoice", command=self.generate_invoice).pack(side='left', padx=3)
        ttk.Button(top_frame, text="💰 Mark as Paid", command=self.mark_invoice_paid).pack(side='left', padx=3)
        ttk.Button(top_frame, text="👁️ View Invoice", command=self.view_invoice_details).pack(side='left', padx=3)
        ttk.Button(top_frame, text="🔄 Refresh", command=self.refresh_invoices).pack(side='right', padx=3)
        
        list_frame = ttk.LabelFrame(inv_frame, text="All Invoices", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Inv#", "SO#", "Customer", "Date", "Due Date", "Subtotal", "GST", "Total", "Status")
        self.inv_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        widths = [50, 50, 130, 90, 90, 80, 70, 90, 80]
        for i, col in enumerate(columns):
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=widths[i])
        
        self.inv_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.inv_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.inv_tree.configure(yscrollcommand=scrollbar.set)
        
        self.refresh_invoices()
    
    def refresh_invoices(self):
        """Refresh invoices list"""
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        
        self.db.execute('''
            SELECT inv.invoice_id, inv.so_number, c.name, inv.invoice_date, inv.due_date,
                inv.subtotal, inv.total_gst, inv.total_amount, inv.status
            FROM Invoices inv
            JOIN Customers c ON inv.customer_id = c.customer_id
            ORDER BY inv.invoice_id DESC
        ''')
        
        for row in self.db.fetchall():
            display_row = (row[0], row[1], row[2], row[3], row[4],
                          f"₹{row[5]:.2f}", f"₹{row[6]:.2f}", f"₹{row[7]:.2f}", row[8])
            
            # Insert ONCE with appropriate tag
            if row[8] == "Paid":
                self.inv_tree.insert('', 'end', values=display_row, tags=('paid',))
            else:
                self.inv_tree.insert('', 'end', values=display_row, tags=('unpaid',))
    
        self.inv_tree.tag_configure('paid', background='#d4edda', foreground='#155724')
        self.inv_tree.tag_configure('unpaid', background='#f8d7da', foreground='#721c24')

    def generate_invoice(self):
        """Generate invoice from delivered sales order"""
        # Get delivered orders that don't have invoices
        self.db.execute('''
            SELECT so.so_number, c.name, so.delivery_date, so.subtotal, so.total_gst, so.total_amount
            FROM Sales_Orders so
            JOIN Customers c ON so.customer_id = c.customer_id
            WHERE so.status = 'Delivered' 
            AND so.so_number NOT IN (SELECT so_number FROM Invoices WHERE so_number IS NOT NULL)
            ORDER BY so.so_number DESC
        ''')
        
        orders = self.db.fetchall()
        
        if not orders:
            messagebox.showinfo("Info", "No delivered orders without invoices")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Generate Invoice")
        dialog.geometry("600x400")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select Sales Order", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Order selection
        frame = ttk.LabelFrame(dialog, text="Delivered Orders", padding=10)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        so_dict = {f"SO #{so[0]} - {so[1]} (₹{so[5]:.2f})": so for so in orders}
        so_var = tk.StringVar()
        
        for label in so_dict.keys():
            ttk.Radiobutton(frame, text=label, variable=so_var, value=label).pack(anchor='w', pady=3)
        
        # Payment terms
        terms_frame = ttk.Frame(dialog)
        terms_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(terms_frame, text="Due Date (YYYY-MM-DD):").pack(side='left', padx=5)
        due_entry = ttk.Entry(terms_frame, width=20)
        due_entry.insert(0, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        due_entry.pack(side='left', padx=5)
        
        def create_invoice():
            if not so_var.get():
                messagebox.showerror("Error", "Select a sales order")
                return
            
            try:
                so_data = so_dict[so_var.get()]
                so_number = so_data[0]
                
                # Get customer ID
                self.db.execute("SELECT customer_id FROM Sales_Orders WHERE so_number = ?", (so_number,))
                customer_id = self.db.fetchone()[0]
                
                # Create invoice
                self.db.execute('''
                    INSERT INTO Invoices (so_number, customer_id, invoice_date, due_date,
                        subtotal, total_gst, total_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (so_number, customer_id, datetime.now().date(), due_entry.get(),
                      so_data[3], so_data[4], so_data[5], 'Unpaid'))
                
                invoice_id = self.db.lastrowid()
                self.db.commit()
                
                messagebox.showinfo("Success", 
                    f"Invoice #{invoice_id} generated!\n\nSO #{so_number}\nAmount: ₹{so_data[5]:.2f}\nDue: {due_entry.get()}")
                dialog.destroy()
                self.refresh_invoices()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="✅ Generate Invoice", command=create_invoice).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def mark_invoice_paid(self):
        """Mark selected invoice as paid"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice to mark as paid")
            return
    
        values = self.inv_tree.item(selected[0])['values']
        invoice_id = values[0]
        status = values[8]
    
        # Check if already paid
        if status == "Paid":
            messagebox.showinfo("Info", f"Invoice #{invoice_id} is already marked as Paid")
            return
        
        # Confirm action
        customer = values[2]
        amount = values[7]

        if messagebox.askyesno("Confirm Payment",f"Mark Invoice #{invoice_id} as Paid?\n\nCustomer: {customer}\nAmount: {amount}\n\nThis action will update the payment status."):
            try:
                # Update invoice status
                self.db.execute(
                    "UPDATE Invoices SET status = 'Paid' WHERE invoice_id = ?",
                    (invoice_id,)
                )
                self.db.commit()

                messagebox.showinfo("Success", f"Invoice #{invoice_id} marked as Paid!")
                self.refresh_invoices()
                self.refresh_sales_reports()  # Update reports

            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Error", f"Failed to update invoice: {str(e)}")

    
    def view_invoice_details(self):
        """View detailed invoice information"""
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an invoice to view")
            return
        
        values = self.inv_tree.item(selected[0])['values']
        invoice_id = values[0]
        so_number = values[1]
        
        # Get invoice details
        self.db.execute('''
            SELECT inv.invoice_id, inv.so_number, c.name, c.gstin, c.address,
                inv.invoice_date, inv.due_date, inv.subtotal, inv.total_gst, 
                inv.total_amount, inv.status
            FROM Invoices inv
            JOIN Customers c ON inv.customer_id = c.customer_id
            WHERE inv.invoice_id = ?
        ''', (invoice_id,))
        
        inv_data = self.db.fetchone()
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Invoice #{invoice_id} Details")
        dialog.geometry("1500x900")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Header
        header_frame = ttk.Frame(dialog, padding=15)
        header_frame.pack(fill='x')
        
        ttk.Label(header_frame, text=f"INVOICE #{invoice_id}", 
            font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text=f"Sales Order: #{so_number}", 
            font=('Arial', 10)).pack()
        
        # Customer Info
        cust_frame = ttk.LabelFrame(dialog, text="Customer Information", padding=10)
        cust_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(cust_frame, text=f"Name: {inv_data[2]}", font=('Arial', 10)).pack(anchor='w', pady=2)
        ttk.Label(cust_frame, text=f"GSTIN: {inv_data[3] or 'N/A'}", font=('Arial', 10)).pack(anchor='w', pady=2)
        ttk.Label(cust_frame, text=f"Address: {inv_data[4] or 'N/A'}", font=('Arial', 10)).pack(anchor='w', pady=2)
        
        # Invoice Info
        info_frame = ttk.LabelFrame(dialog, text="Invoice Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        info_labels = [
            f"Invoice Date: {inv_data[5]}",
            f"Due Date: {inv_data[6]}",
            f"Status: {inv_data[10]}"
        ]
        
        for text in info_labels:
            ttk.Label(info_frame, text=text, font=('Arial', 10)).pack(anchor='w', pady=2)
        
        # Items
        items_frame = ttk.LabelFrame(dialog, text="Invoice Items", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item", "Qty", "Rate", "GST%", "GST Amount", "Total")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        col_widths = [300, 70, 100, 80, 120, 120]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=col_widths[i])
        tree.pack(fill='both', expand=True)
        
        # Get items from sales order
        self.db.execute('''
            SELECT i.name, soi.quantity, soi.rate, soi.gst_percent, 
                soi.gst_amount, soi.total_price
            FROM Sales_Order_Items soi
            JOIN Items i ON soi.item_id = i.item_id
            WHERE soi.so_number = ?
        ''', (so_number,))
        
        for row in self.db.fetchall():
            tree.insert('', 'end', values=(
                row[0], row[1], f"₹{row[2]:.2f}", 
                f"{row[3]:.1f}%", f"₹{row[4]:.2f}", f"₹{row[5]:.2f}"
            ))
        
        # Amount Summary
        summary_frame = ttk.LabelFrame(dialog, text="Amount Summary", padding=15)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(summary_frame, text="Subtotal:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{inv_data[7]:.2f}", font=('Arial', 10, 'bold')).grid(
            row=0, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Label(summary_frame, text="GST:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{inv_data[8]:.2f}", font=('Arial', 10, 'bold'), 
            foreground='blue').grid(row=1, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Separator(summary_frame, orient='horizontal').grid(
            row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Total Amount:", font=('Arial', 12, 'bold')).grid(
            row=3, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{inv_data[9]:.2f}", font=('Arial', 12, 'bold'), 
            foreground='green').grid(row=3, column=1, sticky='e', padx=10, pady=3)
        
        # Status badge
        status_color = 'green' if inv_data[10] == 'Paid' else 'red'
        ttk.Label(summary_frame, text=f"Payment Status: {inv_data[10]}", 
            font=('Arial', 11, 'bold'), foreground=status_color).grid(
            row=4, column=0, columnspan=2, pady=10)
        
        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        if inv_data[10] == 'Unpaid':
            def mark_paid_from_view():
                try:
                    self.db.execute("UPDATE Invoices SET status = 'Paid' WHERE invoice_id = ?", (invoice_id,))
                    self.db.commit()
                    messagebox.showinfo("Success", f"Invoice #{invoice_id} marked as Paid!")
                    dialog.destroy()
                    self.refresh_invoices()
                    self.refresh_sales_reports()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            ttk.Button(btn_frame, text="💰 Mark as Paid", command=mark_paid_from_view).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="❌ Close", command=dialog.destroy).pack(side='left', padx=5)
        
    
    
    
    # ==================== SALES REPORTS TAB ====================
    
    def create_sales_reports_tab(self):
        """Create sales reports tab"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📊 Reports")
    
        top_frame = ttk.Frame(report_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)

        ttk.Label(top_frame, text="Sales Reports & Analytics", font=('Arial', 14, 'bold')).pack(side='left', padx=10)
        ttk.Button(top_frame, text="🔄 Refresh", command=self.refresh_sales_reports).pack(side='right', padx=10)
    
        # Summary cards
        summary_frame = ttk.LabelFrame(report_frame, text="Summary Statistics", padding=15)
        summary_frame.pack(fill='x', padx=10, pady=10)
    
        # Create grid for stats
        self.stats_labels = {}
    
        stats = [
            ("Total Orders:", "total_orders"),
            ("Pending Orders:", "pending_orders"),
            ("Delivered Orders:", "delivered_orders"),
            ("Total Revenue:", "total_revenue"),
            ("Pending Revenue:", "pending_revenue"),
            ("Total Invoices:", "total_invoices"),
            ("Unpaid Invoices:", "unpaid_invoices"),
            ("Total Customers:", "total_customers")
        ]
    
        for i, (label, key) in enumerate(stats):
            row = i // 2
            col = (i % 2) * 2
        
            ttk.Label(summary_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=row, column=col, sticky='w', padx=20, pady=8)
            value_label = ttk.Label(summary_frame, text="0", font=('Arial', 10), foreground='blue')
            value_label.grid(row=row, column=col+1, sticky='w', padx=10, pady=8)
            self.stats_labels[key] = value_label
    
        # ADD THIS SECTION - GST Brackets Frame
        self.gst_brackets_frame = ttk.LabelFrame(report_frame, text="💰 GST Collection Breakdown by Tax Bracket", padding=15)
        self.gst_brackets_frame.pack(fill='x', padx=10, pady=10)
    
        # Top customers
        customers_frame = ttk.LabelFrame(report_frame, text="Top Customers by Revenue (Double-click to view details)", padding=10)
        customers_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
        columns = ("Customer", "Orders", "Subtotal", "GST", "Total (Inc. GST)", "Avg Order")
        self.report_tree = ttk.Treeview(customers_frame, columns=columns, show='headings', height=15)
    
        widths = [180, 80, 120, 100, 130, 120]
        for i, col in enumerate(columns):
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=widths[i])
    
        self.report_tree.pack(side='left', fill='both', expand=True)
    
        scrollbar = ttk.Scrollbar(customers_frame, orient='vertical', command=self.report_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.report_tree.configure(yscrollcommand=scrollbar.set)
    
        # Bind double-click to view customer order details
        self.report_tree.bind('<Double-1>', lambda e: self.view_customer_order_details())
    
        self.refresh_sales_reports()
    
    def refresh_sales_reports(self):
        """Refresh sales reports and statistics"""
        
        # Total orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders")
        self.stats_labels['total_orders'].config(text=str(self.db.fetchone()[0]))
        
        # Pending orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Pending'")
        self.stats_labels['pending_orders'].config(text=str(self.db.fetchone()[0]))
        
        # Delivered orders
        self.db.execute("SELECT COUNT(*) FROM Sales_Orders WHERE status = 'Delivered'")
        self.stats_labels['delivered_orders'].config(text=str(self.db.fetchone()[0]))
        
        # Total revenue (all orders)
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Sales_Orders")
        total_rev = self.db.fetchone()[0]
        self.stats_labels['total_revenue'].config(text=f"₹{total_rev:.2f}")
        
        # Pending revenue
        self.db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM Sales_Orders WHERE status = 'Pending'")
        pending_rev = self.db.fetchone()[0]
        self.stats_labels['pending_revenue'].config(text=f"₹{pending_rev:.2f}")
        
        # Total invoices
        self.db.execute("SELECT COUNT(*) FROM Invoices")
        self.stats_labels['total_invoices'].config(text=str(self.db.fetchone()[0]))
        
        # Unpaid invoices
        self.db.execute("SELECT COUNT(*) FROM Invoices WHERE status = 'Unpaid'")
        self.stats_labels['unpaid_invoices'].config(text=str(self.db.fetchone()[0]))
        
                # Total customers
        self.db.execute("SELECT COUNT(*) FROM Customers")
        self.stats_labels['total_customers'].config(text=str(self.db.fetchone()[0]))
        
        # Clear existing GST brackets content to prevent duplication
        for widget in self.gst_brackets_frame.winfo_children():
            widget.destroy()
        
        # Query to get GST collected by bracket from all sales orders
        self.db.execute('''
            SELECT 
                soi.gst_percent,
                COALESCE(SUM(soi.gst_amount), 0) as total_gst_collected,
                COALESCE(SUM(soi.rate * soi.quantity), 0) as total_base_amount,
                COALESCE(SUM(soi.total_price), 0) as total_with_gst,
                COUNT(DISTINCT so.so_number) as order_count,
                COUNT(*) as item_count
            FROM Sales_Order_Items soi
            JOIN Sales_Orders so ON soi.so_number = so.so_number
            GROUP BY soi.gst_percent
            ORDER BY soi.gst_percent
        ''')
        
        gst_brackets = self.db.fetchall()
        
        if gst_brackets:
            # Add color legend at the top
            legend_frame = ttk.Frame(self.gst_brackets_frame)
            legend_frame.pack(fill='x', pady=(0, 10))
            
            ttk.Label(legend_frame, text="Color Legend:", 
                font=('Arial', 9, 'bold')).pack(side='left', padx=(0, 10))
            
            # Color indicators
            ttk.Label(legend_frame, text="● 0%", 
                font=('Arial', 9), foreground='#666666').pack(side='left', padx=5)
            ttk.Label(legend_frame, text="● 1-5%", 
                font=('Arial', 9), foreground='#28a745').pack(side='left', padx=5)
            ttk.Label(legend_frame, text="● 6-12%", 
                font=('Arial', 9), foreground='#17a2b8').pack(side='left', padx=5)
            ttk.Label(legend_frame, text="● 13-18%", 
                font=('Arial', 9), foreground='#ffc107').pack(side='left', padx=5)
            ttk.Label(legend_frame, text="● 19%+", 
                font=('Arial', 9), foreground='#dc3545').pack(side='left', padx=5)
            
            ttk.Label(legend_frame, text="(Higher rates = warmer colors)", 
                font=('Arial', 8), foreground='gray').pack(side='left', padx=(10, 0))
            
            # Create header
            header_frame = ttk.Frame(self.gst_brackets_frame)
            header_frame.pack(fill='x', pady=(0, 5))
            
            ttk.Label(header_frame, text="Tax Rate", font=('Arial', 9, 'bold'), width=12).pack(side='left', padx=5)
            ttk.Label(header_frame, text="Base Amount", font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            ttk.Label(header_frame, text="GST Collected", font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            ttk.Label(header_frame, text="Total (Inc GST)", font=('Arial', 9, 'bold'), width=15).pack(side='left', padx=5)
            ttk.Label(header_frame, text="Orders", font=('Arial', 9, 'bold'), width=10).pack(side='left', padx=5)
            ttk.Label(header_frame, text="Items", font=('Arial', 9, 'bold'), width=10).pack(side='left', padx=5)
            
            # Add separator
            ttk.Separator(self.gst_brackets_frame, orient='horizontal').pack(fill='x', pady=5)
            
            # Display each bracket
            total_base = 0
            total_gst = 0
            total_with_gst = 0
            
            for bracket in gst_brackets:
                gst_percent, gst_collected, base_amount, amount_with_gst, orders, items = bracket
                
                total_base += base_amount
                total_gst += gst_collected
                total_with_gst += amount_with_gst
                
                bracket_frame = ttk.Frame(self.gst_brackets_frame)
                bracket_frame.pack(fill='x', pady=2)
                
                # Color code based on GST rate
                if gst_percent == 0:
                    color = '#666666'  # Gray for 0%
                elif gst_percent <= 5:
                    color = '#28a745'  # Green for low tax
                elif gst_percent <= 12:
                    color = '#17a2b8'  # Blue for medium-low
                elif gst_percent <= 18:
                    color = '#ffc107'  # Yellow for medium
                else:
                    color = '#dc3545'  # Red for high tax
                
                ttk.Label(bracket_frame, text=f"{gst_percent:.1f}%", 
                    font=('Arial', 10, 'bold'), foreground=color, width=12).pack(side='left', padx=5)
                ttk.Label(bracket_frame, text=f"₹{base_amount:.2f}", 
                    font=('Arial', 10), width=15).pack(side='left', padx=5)
                ttk.Label(bracket_frame, text=f"₹{gst_collected:.2f}", 
                    font=('Arial', 10, 'bold'), foreground=color, width=15).pack(side='left', padx=5)
                ttk.Label(bracket_frame, text=f"₹{amount_with_gst:.2f}", 
                    font=('Arial', 10), width=15).pack(side='left', padx=5)
                ttk.Label(bracket_frame, text=str(orders), 
                    font=('Arial', 10), width=10).pack(side='left', padx=5)
                ttk.Label(bracket_frame, text=str(items), 
                    font=('Arial', 10), width=10).pack(side='left', padx=5)
            
            # Add total row
            ttk.Separator(self.gst_brackets_frame, orient='horizontal').pack(fill='x', pady=5)
            
            total_frame = ttk.Frame(self.gst_brackets_frame)
            total_frame.pack(fill='x', pady=5)
            
            ttk.Label(total_frame, text="TOTAL", 
                font=('Arial', 10, 'bold'), width=12).pack(side='left', padx=5)
            ttk.Label(total_frame, text=f"₹{total_base:.2f}", 
                font=('Arial', 10, 'bold'), foreground='blue', width=15).pack(side='left', padx=5)
            ttk.Label(total_frame, text=f"₹{total_gst:.2f}", 
                font=('Arial', 10, 'bold'), foreground='red', width=15).pack(side='left', padx=5)
            ttk.Label(total_frame, text=f"₹{total_with_gst:.2f}", 
                font=('Arial', 10, 'bold'), foreground='green', width=15).pack(side='left', padx=5)
            
            # Add info note
            info_frame = ttk.Frame(self.gst_brackets_frame)
            info_frame.pack(fill='x', pady=(10, 0))
            ttk.Label(info_frame, 
                text="ℹ️ GST liability to be paid to government: Red amount above. This is calculated from all sales orders.", 
                font=('Arial', 9), foreground='#666666').pack()
            
        else:
            # No sales data
            ttk.Label(self.gst_brackets_frame, 
                text="No sales data available yet. GST brackets will appear once orders are created.", 
                font=('Arial', 10), foreground='gray').pack(pady=20)
        
        # === END GST BRACKET BREAKDOWN ===
        
        # Top customers with GST breakdown
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Top customers with GST breakdown
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        self.db.execute('''
            SELECT c.customer_id,
                c.name, 
                COUNT(so.so_number) as order_count,
                COALESCE(SUM(so.subtotal), 0) as total_subtotal,
                COALESCE(SUM(so.total_gst), 0) as total_gst,
                COALESCE(SUM(so.total_amount), 0) as total_revenue,
                COALESCE(AVG(so.total_amount), 0) as avg_order
            FROM Customers c
            LEFT JOIN Sales_Orders so ON c.customer_id = so.customer_id
            GROUP BY c.customer_id, c.name
            HAVING order_count > 0
            ORDER BY total_revenue DESC
            LIMIT 20
        ''')
        
        for row in self.db.fetchall():
            # Store customer_id in the item's tags for later retrieval
            item_id = self.report_tree.insert('', 'end', values=(
                row[1],  # Customer name
                row[2],  # Order count
                f"₹{row[3]:.2f}",  # Subtotal
                f"₹{row[4]:.2f}",  # GST
                f"₹{row[5]:.2f}",  # Total
                f"₹{row[6]:.2f}"   # Avg
            ))
            # Store customer_id as a tag so we can retrieve it later
            self.report_tree.item(item_id, tags=(str(row[0]),))
    
    def view_customer_order_details(self):
        """View detailed order breakdown for a customer"""
        selected = self.report_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a customer to view details")
            return
        
        # Get customer_id from tags
        tags = self.report_tree.item(selected[0])['tags']
        if not tags:
            messagebox.showerror("Error", "Cannot retrieve customer information")
            return
            
        customer_id = tags[0]
        customer_name = self.report_tree.item(selected[0])['values'][0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Order Details - {customer_name}")
        dialog.geometry("1100x700")
        dialog.transient(self.app.root)
        
        # Wait for window to be visible before grabbing
        dialog.update_idletasks()
        dialog.grab_set()
        
        # Header
        header_frame = ttk.Frame(dialog, padding=10)
        header_frame.pack(fill='x')
        
        ttk.Label(header_frame, text=f"All Orders for: {customer_name}", 
            font=('Arial', 14, 'bold')).pack()
        
        # Summary frame
        summary_frame = ttk.LabelFrame(dialog, text="Customer Summary", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        # Get summary data
        self.db.execute('''
            SELECT 
                COUNT(so.so_number) as total_orders,
                COALESCE(SUM(so.subtotal), 0) as total_subtotal,
                COALESCE(SUM(so.total_gst), 0) as total_gst,
                COALESCE(SUM(so.total_amount), 0) as total_amount,
                COALESCE(AVG(so.total_amount), 0) as avg_order
            FROM Sales_Orders so
            WHERE so.customer_id = ?
        ''', (customer_id,))
        
        summary = self.db.fetchone()
        
        summary_text = f"Total Orders: {summary[0]}  |  "
        summary_text += f"Subtotal: ₹{summary[1]:.2f}  |  "
        summary_text += f"GST: ₹{summary[2]:.2f}  |  "
        summary_text += f"Total: ₹{summary[3]:.2f}  |  "
        summary_text += f"Avg Order: ₹{summary[4]:.2f}"
        
        ttk.Label(summary_frame, text=summary_text, font=('Arial', 10, 'bold'), 
            foreground='blue').pack()
        
        # Orders list
        orders_frame = ttk.LabelFrame(dialog, text="Individual Orders", padding=10)
        orders_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("SO#", "Order Date", "Status", "Items", "Subtotal", "GST", "Total")
        tree = ttk.Treeview(orders_frame, columns=columns, show='headings', height=20)
        
        widths = [60, 100, 100, 60, 110, 100, 110]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=widths[i])
        
        tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(orders_frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Get all orders for this customer
        self.db.execute('''
            SELECT so.so_number, so.order_date, so.status,
                (SELECT COUNT(*) FROM Sales_Order_Items WHERE so_number = so.so_number) as item_count,
                so.subtotal, so.total_gst, so.total_amount
            FROM Sales_Orders so
            WHERE so.customer_id = ?
            ORDER BY so.so_number DESC
        ''', (customer_id,))
        
        for row in self.db.fetchall():
            tree.insert('', 'end', values=(
                row[0],  # SO#
                row[1],  # Date
                row[2],  # Status
                row[3],  # Items count
                f"₹{row[4]:.2f}",  # Subtotal
                f"₹{row[5]:.2f}",  # GST
                f"₹{row[6]:.2f}"   # Total
            ))
        
        # Info label
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(info_frame, text="ℹ️ Subtotal = Base amount before GST  |  GST = Tax amount  |  Total = Final amount (Subtotal + GST)", 
            font=('Arial', 9), foreground='gray').pack()
        
        # Close button
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="✖ Close", command=dialog.destroy).pack()
