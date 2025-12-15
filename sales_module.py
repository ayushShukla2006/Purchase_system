"""
Sales Module with GST Support (India) - Multi-item orders - ENHANCED VERSION
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
        self.create_delivery_tab()  # NEW TAB
        self.create_invoices_tab()
        self.create_sales_reports_tab()
    
    def refresh_all(self):
        self.refresh_customers()
        self.refresh_sales_orders()
        self.refresh_delivery_history()  # NEW
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
        
        ttk.Label(top_frame, text="Record Deliveries", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Button(top_frame, text="➕ New Delivery", command=self.new_delivery).pack(pady=5)
        ttk.Button(top_frame, text="✏️ Edit Delivery", command=self.edit_delivery).pack(pady=5)
        
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
        """Edit a delivery record"""
        selected = self.delivery_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a delivery record")
            return
        
        messagebox.showinfo("Info", "Delivery editing: Check delivered quantities against invoices.\nFor now, use 'View Details' to review.")
    
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
            
    # ==================== INVOICES TAB ====================
    
    def create_invoices_tab(self):
        """Create invoices tab"""
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="📄 Invoices")
        
        top_frame = ttk.Frame(inv_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Invoice Management", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Button(top_frame, text="➕ Generate Invoice", command=self.generate_invoice).pack(pady=5)
        ttk.Button(top_frame, text="💰 Mark as Paid", command=self.mark_invoice_paid).pack(pady=5)
        ttk.Button(top_frame, text="👁️ View Invoice", command=self.view_invoice_details).pack(pady=5)
        ttk.Button(top_frame, text="🔄 Refresh", command=self.refresh_invoices).pack(pady=5)
        
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
            self.inv_tree.insert('', 'end', values=display_row)
    
        if row[8] == "Paid":
            self.inv_tree.insert('', 'end', values=display_row, tags=('paid',))
        else:
            self.inv_tree.insert('', 'end', values=display_row, tags=('unpaid',))
    
        self.inv_tree.tag_configure('paid', background='#d4edda', foreground='#155724')  # Light green
        self.inv_tree.tag_configure('unpaid', background='#f8d7da', foreground='#721c24')  # Light red
    
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
        dialog.geometry("1200x800")
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
    
    # ==================== SALES REPORTS TAB ====================
    
    def create_sales_reports_tab(self):
        """Create sales reports tab"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📊 Reports")
        
        top_frame = ttk.Frame(report_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Sales Reports & Analytics", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Button(top_frame, text="🔄 Refresh", command=self.refresh_sales_reports).pack(pady=5)
        
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
        
        # Top customers
        customers_frame = ttk.LabelFrame(report_frame, text="Top Customers by Revenue", padding=10)
        customers_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Customer", "Total Orders", "Total Revenue", "Avg Order Value")
        self.report_tree = ttk.Treeview(customers_frame, columns=columns, show='headings', height=15)
        
        widths = [200, 120, 150, 150]
        for i, col in enumerate(columns):
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=widths[i])
        
        self.report_tree.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(customers_frame, orient='vertical', command=self.report_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
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
        
        # Top customers
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        self.db.execute('''
            SELECT c.name, 
                COUNT(so.so_number) as order_count,
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
            display_row = (row[0], row[1], f"₹{row[2]:.2f}", f"₹{row[3]:.2f}")
            self.report_tree.insert('', 'end', values=display_row)
