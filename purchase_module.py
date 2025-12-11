"""
Purchase Module with GST Support (India) - Multi-item orders
Save as: purchase_module.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PurchaseModule:
    def __init__(self, notebook, db, app):
        self.notebook = notebook
        self.db = db
        self.app = app
        self.create_inventory_tab()
        self.create_purchase_order_tab()
        self.create_suppliers_tab()
        self.create_goods_receipt_tab()
        self.create_alerts_tab()
    
    def refresh_all(self):
        self.refresh_inventory()
        self.refresh_purchase_orders()
        self.refresh_suppliers()
        self.refresh_receipt_history()
        self.refresh_alerts()
    
    def calculate_gst_price(self, rate, gst_percent):
        """Calculate final price from rate and GST"""
        gst_amount = (rate * gst_percent) / 100
        final_price = rate + gst_amount
        return gst_amount, final_price
    
    # ==================== INVENTORY TAB ====================
    
    def create_inventory_tab(self):
        inv_frame = ttk.Frame(self.notebook)
        self.notebook.add(inv_frame, text="📦 Inventory")
        top_btn_frame = ttk.Frame(inv_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Add Item", command=self.add_new_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit", command=self.edit_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete", command=self.delete_item).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_inventory).pack(side='right', padx=3)
        columns = ("ID", "Name", "Category", "Qty", "Reorder", "Buy Rate", "Buy GST%", "Buy Price", "Sell Rate", "Sell GST%", "Sell Price", "Status")
        self.inv_tree = ttk.Treeview(inv_frame, columns=columns, show='headings', height=25)
        widths = [40, 140, 100, 60, 70, 90, 70, 100, 90, 70, 100, 70]
        for i, col in enumerate(columns):
            self.inv_tree.heading(col, text=col)
            self.inv_tree.column(col, width=widths[i])
        self.inv_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(inv_frame, orient='vertical', command=self.inv_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.inv_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_inventory()
    
    def refresh_inventory(self):
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        self.db.execute('''SELECT i.item_id, i.name, i.category, inv.quantity_on_hand, inv.reorder_level,
            i.purchase_rate, i.purchase_gst_percent, i.purchase_price, 
            i.selling_rate, i.selling_gst_percent, i.selling_price
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id ORDER BY i.item_id''')
        for row in self.db.fetchall():
            status = "LOW" if row[3] <= row[4] else "OK"
            tag = 'low' if status == "LOW" else ''
            display_row = (row[0], row[1], row[2], row[3], row[4], 
                          f"₹{row[5]:.2f}", f"{row[6]:.1f}%", f"₹{row[7]:.2f}",
                          f"₹{row[8]:.2f}", f"{row[9]:.1f}%", f"₹{row[10]:.2f}", status)
            self.inv_tree.insert('', 'end', values=display_row, tags=(tag,))
        self.inv_tree.tag_configure('low', background='#ffcccc')
    
    def validate_item_data(self, name, purchase_rate, purchase_gst, selling_rate, selling_gst, qty, reorder):
        if not name or not name.strip():
            raise ValueError("Item name cannot be empty")
        try:
            p_rate = float(purchase_rate)
            if p_rate < 0:
                raise ValueError("Purchase rate cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid purchase rate")
        try:
            p_gst = float(purchase_gst)
            if p_gst < 0 or p_gst > 100:
                raise ValueError("Purchase GST must be between 0 and 100")
        except (ValueError, TypeError):
            raise ValueError("Invalid purchase GST")
        try:
            s_rate = float(selling_rate)
            if s_rate < 0:
                raise ValueError("Selling rate cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid selling rate")
        try:
            s_gst = float(selling_gst)
            if s_gst < 0 or s_gst > 100:
                raise ValueError("Selling GST must be between 0 and 100")
        except (ValueError, TypeError):
            raise ValueError("Invalid selling GST")
        try:
            qty_val = int(qty)
            if qty_val < 0:
                raise ValueError("Quantity cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid quantity")
        try:
            reorder_val = int(reorder)
            if reorder_val < 0:
                raise ValueError("Reorder level cannot be negative")
        except (ValueError, TypeError):
            raise ValueError("Invalid reorder level")
        return p_rate, p_gst, s_rate, s_gst, qty_val, reorder_val
    
    def add_new_item(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add New Item")
        dialog.geometry("500x550")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = [
            ("Item Name:*", "name"),
            ("Description:", "desc"),
            ("Category:", "cat"),
            ("Unit of Measure:", "uom"),
            ("HSN Code:", "hsn"),
            ("Purchase Rate (₹):*", "p_rate"),
            ("Purchase GST (%):*", "p_gst"),
            ("Selling Rate (₹):*", "s_rate"),
            ("Selling GST (%):*", "s_gst"),
            ("Initial Quantity:*", "qty"),
            ("Reorder Level:*", "reorder"),
            ("Location:", "loc")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=6, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            if key == "p_gst" or key == "s_gst":
                entry.insert(0, "18.0")  # Default GST 18%
            entry.grid(row=i, column=1, padx=10, pady=6)
            entries[key] = entry
        
        # Price preview labels
        ttk.Label(dialog, text="Purchase Price Preview:", font=('Arial', 9, 'bold')).grid(row=len(fields), column=0, padx=10, pady=5, sticky='w')
        p_price_label = ttk.Label(dialog, text="₹0.00", foreground='blue')
        p_price_label.grid(row=len(fields), column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(dialog, text="Selling Price Preview:", font=('Arial', 9, 'bold')).grid(row=len(fields)+1, column=0, padx=10, pady=5, sticky='w')
        s_price_label = ttk.Label(dialog, text="₹0.00", foreground='green')
        s_price_label.grid(row=len(fields)+1, column=1, padx=10, pady=5, sticky='w')
        
        def update_preview(*args):
            try:
                p_rate = float(entries["p_rate"].get() or 0)
                p_gst = float(entries["p_gst"].get() or 0)
                s_rate = float(entries["s_rate"].get() or 0)
                s_gst = float(entries["s_gst"].get() or 0)
                _, p_final = self.calculate_gst_price(p_rate, p_gst)
                _, s_final = self.calculate_gst_price(s_rate, s_gst)
                p_price_label.config(text=f"₹{p_final:.2f} (Rate: ₹{p_rate:.2f} + GST: ₹{p_final-p_rate:.2f})")
                s_price_label.config(text=f"₹{s_final:.2f} (Rate: ₹{s_rate:.2f} + GST: ₹{s_final-s_rate:.2f})")
            except:
                pass
        
        for key in ["p_rate", "p_gst", "s_rate", "s_gst"]:
            entries[key].bind('<KeyRelease>', update_preview)
        
        def save():
            try:
                p_rate, p_gst, s_rate, s_gst, qty_val, reorder_val = self.validate_item_data(
                    entries["name"].get(), entries["p_rate"].get(), entries["p_gst"].get(),
                    entries["s_rate"].get(), entries["s_gst"].get(), entries["qty"].get(), entries["reorder"].get())
                
                _, p_price = self.calculate_gst_price(p_rate, p_gst)
                _, s_price = self.calculate_gst_price(s_rate, s_gst)
                
                self.db.execute("""INSERT INTO Items (name, description, category, unit_of_measure, hsn_code,
                    purchase_rate, purchase_gst_percent, purchase_price, 
                    selling_rate, selling_gst_percent, selling_price) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (entries["name"].get().strip(), entries["desc"].get(), entries["cat"].get(), 
                     entries["uom"].get(), entries["hsn"].get(), p_rate, p_gst, p_price, s_rate, s_gst, s_price))
                item_id = self.db.lastrowid()
                
                self.db.execute("INSERT INTO Inventory (item_id, quantity_on_hand, reorder_level, location, last_updated) VALUES (?, ?, ?, ?, ?)",
                    (item_id, qty_val, reorder_val, entries["loc"].get(), datetime.now()))
                
                self.db.commit()
                messagebox.showinfo("Success", f"Item added!\nPurchase: ₹{p_price:.2f}\nSelling: ₹{s_price:.2f}")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except ValueError as ve:
                messagebox.showerror("Validation Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Save Item", command=save).grid(row=len(fields)+2, column=0, columnspan=2, pady=15)
        update_preview()
    
    def edit_item(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
        
        # Get item ID from first column
        values = self.inv_tree.item(selected[0])['values']
        item_id = values[0]
        
        self.db.execute('''SELECT i.name, i.description, i.category, i.unit_of_measure, i.hsn_code,
            i.purchase_rate, i.purchase_gst_percent, i.selling_rate, i.selling_gst_percent,
            inv.quantity_on_hand, inv.reorder_level, inv.location
            FROM Items i JOIN Inventory inv ON i.item_id = inv.item_id WHERE i.item_id = ?''', (item_id,))
        data = self.db.fetchone()
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Item")
        dialog.geometry("500x550")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        fields = [
            ("Item Name:", data[0]),
            ("Description:", data[1] or ""),
            ("Category:", data[2] or ""),
            ("Unit of Measure:", data[3] or ""),
            ("HSN Code:", data[4] or ""),
            ("Purchase Rate (₹):", data[5]),
            ("Purchase GST (%):", data[6]),
            ("Selling Rate (₹):", data[7]),
            ("Selling GST (%):", data[8]),
            ("Quantity:", data[9]),
            ("Reorder Level:", data[10]),
            ("Location:", data[11] or "")
        ]
        
        entries = []
        for i, (label, value) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=6, sticky='w')
            entry = ttk.Entry(dialog, width=30)
            entry.insert(0, value)
            entry.grid(row=i, column=1, padx=10, pady=6)
            entries.append(entry)
        
        # Price preview
        p_price_label = ttk.Label(dialog, text="", foreground='blue')
        p_price_label.grid(row=len(fields), column=0, columnspan=2, pady=3)
        s_price_label = ttk.Label(dialog, text="", foreground='green')
        s_price_label.grid(row=len(fields)+1, column=0, columnspan=2, pady=3)
        
        def update_preview(*args):
            try:
                p_rate = float(entries[5].get() or 0)
                p_gst = float(entries[6].get() or 0)
                s_rate = float(entries[7].get() or 0)
                s_gst = float(entries[8].get() or 0)
                _, p_final = self.calculate_gst_price(p_rate, p_gst)
                _, s_final = self.calculate_gst_price(s_rate, s_gst)
                p_price_label.config(text=f"Purchase Price: ₹{p_final:.2f}")
                s_price_label.config(text=f"Selling Price: ₹{s_final:.2f}")
            except:
                pass
        
        for idx in [5, 6, 7, 8]:
            entries[idx].bind('<KeyRelease>', update_preview)
        
        def update():
            try:
                p_rate, p_gst, s_rate, s_gst, qty_val, reorder_val = self.validate_item_data(
                    entries[0].get(), entries[5].get(), entries[6].get(),
                    entries[7].get(), entries[8].get(), entries[9].get(), entries[10].get())
                
                _, p_price = self.calculate_gst_price(p_rate, p_gst)
                _, s_price = self.calculate_gst_price(s_rate, s_gst)
                
                self.db.execute("""UPDATE Items SET name=?, description=?, category=?, unit_of_measure=?, hsn_code=?,
                    purchase_rate=?, purchase_gst_percent=?, purchase_price=?,
                    selling_rate=?, selling_gst_percent=?, selling_price=? WHERE item_id=?""",
                    (entries[0].get().strip(), entries[1].get(), entries[2].get(), entries[3].get(), entries[4].get(),
                     p_rate, p_gst, p_price, s_rate, s_gst, s_price, item_id))
                self.db.execute("UPDATE Inventory SET quantity_on_hand=?, reorder_level=?, location=?, last_updated=? WHERE item_id=?",
                    (qty_val, reorder_val, entries[11].get(), datetime.now(), item_id))
                self.db.commit()
                messagebox.showinfo("Success", "Item updated!")
                dialog.destroy()
                self.app.refresh_all_tabs()
            except ValueError as ve:
                messagebox.showerror("Validation Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields)+2, column=0, columnspan=2, pady=15)
        update_preview()
    
    def delete_item(self):
        selected = self.inv_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item")
            return
        values = self.inv_tree.item(selected[0])['values']
        item_id, item_name = values[0], values[1]
        
        self.db.execute("SELECT COUNT(*) FROM Purchase_Order_Items WHERE item_id = ?", (item_id,))
        po_count = self.db.fetchone()[0]
        self.db.execute("SELECT COUNT(*) FROM Sales_Order_Items WHERE item_id = ?", (item_id,))
        so_count = self.db.fetchone()[0]
        self.db.execute("SELECT COUNT(*) FROM Goods_Receipt WHERE item_id = ?", (item_id,))
        gr_count = self.db.fetchone()[0]
        
        if po_count > 0 or so_count > 0 or gr_count > 0:
            msg = f"Cannot delete '{item_name}'\n\nReferenced in:\n"
            if po_count > 0: msg += f"- {po_count} Purchase Order(s)\n"
            if so_count > 0: msg += f"- {so_count} Sales Order(s)\n"
            if gr_count > 0: msg += f"- {gr_count} Goods Receipt(s)\n"
            msg += "\nData integrity protected."
            messagebox.showerror("Cannot Delete", msg)
            return
        
        if messagebox.askyesno("Confirm", f"Delete '{item_name}'?"):
            try:
                self.db.execute("DELETE FROM Inventory WHERE item_id = ?", (item_id,))
                self.db.execute("DELETE FROM Items WHERE item_id = ?", (item_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Deleted!")
                self.app.refresh_all_tabs()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    # ==================== PURCHASE ORDERS TAB ====================
    
    def create_purchase_order_tab(self):
        po_frame = ttk.Frame(self.notebook)
        self.notebook.add(po_frame, text="🛒 Purchase Orders")
        top_btn_frame = ttk.Frame(po_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Create PO", command=self.create_purchase_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="👁️ View Details", command=self.view_po_details).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete PO", command=self.delete_purchase_order).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_purchase_orders).pack(side='right', padx=3)
        columns = ("PO#", "Supplier", "Order Date", "Delivery", "Status", "Subtotal", "GST", "Total", "Items")
        self.po_tree = ttk.Treeview(po_frame, columns=columns, show='headings', height=25)
        widths = [50, 130, 90, 90, 90, 80, 70, 90, 50]
        for i, col in enumerate(columns):
            self.po_tree.heading(col, text=col)
            self.po_tree.column(col, width=widths[i])
        self.po_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(po_frame, orient='vertical', command=self.po_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.po_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_purchase_orders()
    
    def refresh_purchase_orders(self):
        for item in self.po_tree.get_children():
            self.po_tree.delete(item)
        self.db.execute('''SELECT po.po_number, s.name, po.order_date, po.expected_delivery, po.status, 
            po.subtotal, po.total_gst, po.total_amount,
            (SELECT COUNT(*) FROM Purchase_Order_Items WHERE po_number = po.po_number) as item_count
            FROM Purchase_Orders po JOIN Suppliers s ON po.supplier_id = s.supplier_id ORDER BY po.po_number''')
        for row in self.db.fetchall():
            display_row = (row[0], row[1], row[2], row[3], row[4], 
                          f"₹{row[5]:.2f}", f"₹{row[6]:.2f}", f"₹{row[7]:.2f}", row[8])
            self.po_tree.insert('', 'end', values=display_row)
    
    def create_purchase_order(self):
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add suppliers first")
            return
        self.db.execute("SELECT COUNT(*) FROM Items")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add items first")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create Purchase Order - Multi-Item (with GST)")
        dialog.geometry("950x700")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Supplier
        ttk.Label(dialog, text="Supplier:*", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.db.execute("SELECT supplier_id, name, gstin FROM Suppliers ORDER BY name")
        suppliers = self.db.fetchall()
        supplier_dict = {f"{s[1]} (GSTIN: {s[2] or 'N/A'})": s[0] for s in suppliers}
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(dialog, textvariable=supplier_var, values=list(supplier_dict.keys()), width=50, state='readonly')
        supplier_combo.grid(row=0, column=1, padx=10, pady=10, columnspan=3)
        
        # Delivery Date
        ttk.Label(dialog, text="Delivery Date (YYYY-MM-DD):*", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        delivery_entry = ttk.Entry(dialog, width=52)
        delivery_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=3)
        
        # Item Selection
        ttk.Label(dialog, text="Add Items:", font=('Arial', 11, 'bold')).grid(row=2, column=0, padx=10, pady=(20, 10), sticky='w', columnspan=4)
        item_frame = ttk.LabelFrame(dialog, text="Item Selection", padding=10)
        item_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky='ew')
        
        ttk.Label(item_frame, text="Item:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.db.execute("SELECT item_id, name, purchase_rate, purchase_gst_percent, purchase_price FROM Items ORDER BY name")
        items = self.db.fetchall()
        item_dict = {f"{i[1]} (Rate: ₹{i[2]:.2f} + {i[3]:.1f}% GST = ₹{i[4]:.2f})": (i[0], i[2], i[3]) for i in items}
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(item_frame, textvariable=item_var, values=list(item_dict.keys()), width=50, state='readonly')
        item_combo.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        
        ttk.Label(item_frame, text="Qty:").grid(row=0, column=3, padx=5, pady=5)
        qty_entry = ttk.Entry(item_frame, width=10)
        qty_entry.grid(row=0, column=4, padx=5, pady=5)
        
        selected_items = []
        
        def add_item():
            if not item_var.get():
                messagebox.showwarning("Warning", "Select an item")
                return
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showerror("Error", "Quantity must be positive")
                    return
                item_id, rate, gst_percent = item_dict[item_var.get()]
                item_name = item_var.get().split(' (Rate:')[0]
                
                for existing in selected_items:
                    if existing[0] == item_id:
                        messagebox.showwarning("Warning", "Item already added")
                        return
                
                gst_amt, total = self.calculate_gst_price(rate * qty, gst_percent)
                selected_items.append((item_id, item_name, qty, rate, gst_percent, gst_amt, total))
                items_tree.insert('', 'end', values=(item_name, qty, f"₹{rate:.2f}", f"{gst_percent:.1f}%", f"₹{gst_amt:.2f}", f"₹{total:.2f}"))
                update_total()
                item_var.set('')
                qty_entry.delete(0, tk.END)
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
        col_widths = [250, 60, 80, 60, 80, 100]
        for i, col in enumerate(columns):
            items_tree.heading(col, text=col)
            items_tree.column(col, width=col_widths[i])
        items_tree.pack(fill='both', expand=True)
        
        total_label = ttk.Label(dialog, text="Subtotal: ₹0.00  |  GST: ₹0.00  |  Total: ₹0.00", font=('Arial', 11, 'bold'), foreground='blue')
        total_label.grid(row=5, column=0, columnspan=4, pady=10)
        
        def save_po():
            try:
                if not supplier_var.get():
                    messagebox.showerror("Error", "Select a supplier")
                    return
                if not delivery_entry.get().strip():
                    messagebox.showerror("Error", "Enter delivery date")
                    return
                if not selected_items:
                    messagebox.showerror("Error", "Add at least one item")
                    return
                
                supplier_id = supplier_dict[supplier_var.get()]
                subtotal = sum(item[3] * item[2] for item in selected_items)
                total_gst = sum(item[5] for item in selected_items)
                total_amount = sum(item[6] for item in selected_items)
                
                self.db.execute("INSERT INTO Purchase_Orders (supplier_id, order_date, expected_delivery, status, subtotal, total_gst, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (supplier_id, datetime.now().date(), delivery_entry.get(), "Pending", subtotal, total_gst, total_amount))
                po_number = self.db.lastrowid()
                
                for item_id, item_name, qty, rate, gst_percent, gst_amt, total in selected_items:
                    self.db.execute("INSERT INTO Purchase_Order_Items (po_number, item_id, quantity, rate, gst_percent, gst_amount, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (po_number, item_id, qty, rate, gst_percent, gst_amt, total))
                
                self.db.commit()
                messagebox.showinfo("Success", f"PO #{po_number} created!\n\nItems: {len(selected_items)}\nSubtotal: ₹{subtotal:.2f}\nGST: ₹{total_gst:.2f}\nTotal: ₹{total_amount:.2f}")
                dialog.destroy()
                self.refresh_purchase_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {str(e)}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=4, pady=20)
        ttk.Button(btn_frame, text="✅ Create Purchase Order", command=save_po, width=30).pack()
    
    def delete_purchase_order(self):
        selected = self.po_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a purchase order")
            return
        values = self.po_tree.item(selected[0])['values']
        po_number = values[0]
        
        self.db.execute("SELECT COUNT(*) FROM Goods_Receipt WHERE po_number = ?", (po_number,))
        gr_count = self.db.fetchone()[0]
        if gr_count > 0:
            messagebox.showerror("Cannot Delete", f"PO #{po_number} has {gr_count} goods receipt(s).\nData integrity protected.")
            return
        
        if messagebox.askyesno("Confirm", f"Delete PO #{po_number} and all items?"):
            try:
                self.db.execute("DELETE FROM Purchase_Order_Items WHERE po_number = ?", (po_number,))
                self.db.execute("DELETE FROM Purchase_Orders WHERE po_number = ?", (po_number,))
                self.db.commit()
                messagebox.showinfo("Success", f"PO #{po_number} deleted!")
                self.refresh_purchase_orders()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def view_po_details(self):
        selected = self.po_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a PO")
            return
        values = self.po_tree.item(selected[0])['values']
        po_number = values[0]
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"PO #{po_number} Details")
        dialog.geometry("1000x600")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        self.db.execute('''SELECT po.po_number, s.name, s.gstin, po.order_date, po.expected_delivery, 
            po.status, po.subtotal, po.total_gst, po.total_amount
            FROM Purchase_Orders po JOIN Suppliers s ON po.supplier_id = s.supplier_id WHERE po.po_number = ?''', (po_number,))
        po_info = self.db.fetchone()
        
        info_frame = ttk.LabelFrame(dialog, text="Order Information", padding=15)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        labels = [
            f"PO Number: {po_info[0]}",
            f"Supplier: {po_info[1]}",
            f"GSTIN: {po_info[2] or 'N/A'}",
            f"Order Date: {po_info[3]}",
            f"Expected Delivery: {po_info[4]}",
            f"Status: {po_info[5]}"
        ]
        
        for i, text in enumerate(labels):
            ttk.Label(info_frame, text=text, font=('Arial', 10)).grid(row=i//2, column=i%2, sticky='w', padx=20, pady=5)
        
        # Amount summary
        summary_frame = ttk.LabelFrame(dialog, text="Amount Summary", padding=10)
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(summary_frame, text=f"Subtotal (Before GST):", font=('Arial', 10)).grid(row=0, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{po_info[6]:.2f}", font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Label(summary_frame, text=f"Total GST:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{po_info[7]:.2f}", font=('Arial', 10, 'bold'), foreground='blue').grid(row=1, column=1, sticky='e', padx=10, pady=3)
        
        ttk.Separator(summary_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        ttk.Label(summary_frame, text=f"Total Amount:", font=('Arial', 11, 'bold')).grid(row=3, column=0, sticky='w', padx=10, pady=3)
        ttk.Label(summary_frame, text=f"₹{po_info[8]:.2f}", font=('Arial', 11, 'bold'), foreground='green').grid(row=3, column=1, sticky='e', padx=10, pady=3)
        
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
        
        self.db.execute('''SELECT i.name, poi.quantity, poi.rate, poi.gst_percent, poi.gst_amount, poi.total_price
            FROM Purchase_Order_Items poi JOIN Items i ON poi.item_id = i.item_id WHERE poi.po_number = ?''', (po_number,))
        for row in self.db.fetchall():
            tree.insert('', 'end', values=(row[0], row[1], f"₹{row[2]:.2f}", f"{row[3]:.1f}%", f"₹{row[4]:.2f}", f"₹{row[5]:.2f}"))
    
    # ==================== SUPPLIERS TAB ====================
    
    def create_suppliers_tab(self):
        sup_frame = ttk.Frame(self.notebook)
        self.notebook.add(sup_frame, text="🏢 Suppliers")
        top_btn_frame = ttk.Frame(sup_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        ttk.Button(top_btn_frame, text="➕ Add", command=self.add_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="✏️ Edit", command=self.edit_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🗑️ Delete", command=self.delete_supplier).pack(side='left', padx=3)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_suppliers).pack(side='right', padx=3)
        columns = ("ID", "Name", "Contact", "Phone", "Email", "GSTIN", "Terms")
        self.sup_tree = ttk.Treeview(sup_frame, columns=columns, show='headings', height=25)
        widths = [40, 150, 120, 100, 150, 150, 100]
        for i, col in enumerate(columns):
            self.sup_tree.heading(col, text=col)
            self.sup_tree.column(col, width=widths[i])
        self.sup_tree.pack(side='left', fill='both', expand=True, padx=10, pady=(0, 10))
        scrollbar = ttk.Scrollbar(sup_frame, orient='vertical', command=self.sup_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(0, 10), padx=(0, 10))
        self.sup_tree.configure(yscrollcommand=scrollbar.set)
        self.refresh_suppliers()
    
    def refresh_suppliers(self):
        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)
        self.db.execute("SELECT supplier_id, name, contact_person, phone, email, gstin, payment_terms FROM Suppliers")
        for row in self.db.fetchall():
            self.sup_tree.insert('', 'end', values=row)
    
    def add_supplier(self):
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add Supplier")
        dialog.geometry("500x400")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = [("Name:*", "name"), ("Contact Person:", "contact"), ("Phone:", "phone"), 
                  ("Email:", "email"), ("Address:", "address"), ("GSTIN:", "gstin"), ("Payment Terms:", "terms")]
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=8, sticky='w')
            entry = ttk.Entry(dialog, width=35)
            entry.grid(row=i, column=1, padx=10, pady=8)
            entries[key] = entry
        
        def save():
            try:
                if not entries["name"].get().strip():
                    messagebox.showerror("Error", "Supplier name required")
                    return
                self.db.execute("INSERT INTO Suppliers (name, contact_person, phone, email, address, gstin, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (entries["name"].get().strip(), entries["contact"].get(), entries["phone"].get(),
                     entries["email"].get(), entries["address"].get(), entries["gstin"].get(), entries["terms"].get()))
                self.db.commit()
                messagebox.showinfo("Success", "Supplier added!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Save", command=save).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def edit_supplier(self):
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a supplier")
            return
        supplier_id = self.sup_tree.item(selected[0])['values'][0]
        self.db.execute("SELECT name, contact_person, phone, email, address, gstin, payment_terms FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
        data = self.db.fetchone()
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Supplier")
        dialog.geometry("500x400")
        dialog.transient(self.app.root)
        dialog.grab_set()
        fields = ["Name:", "Contact:", "Phone:", "Email:", "Address:", "GSTIN:", "Terms:"]
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
                self.db.execute("UPDATE Suppliers SET name=?, contact_person=?, phone=?, email=?, address=?, gstin=?, payment_terms=? WHERE supplier_id=?",
                    tuple(e.get() for e in entries) + (supplier_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Updated!")
                dialog.destroy()
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        ttk.Button(dialog, text="Update", command=update).grid(row=len(fields), column=0, columnspan=2, pady=15)
    
    def delete_supplier(self):
        selected = self.sup_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a supplier")
            return
        supplier_id, name = self.sup_tree.item(selected[0])['values'][0], self.sup_tree.item(selected[0])['values'][1]
        self.db.execute("SELECT COUNT(*) FROM Purchase_Orders WHERE supplier_id = ?", (supplier_id,))
        if self.db.fetchone()[0] > 0:
            messagebox.showerror("Cannot Delete", f"'{name}' has purchase orders.\nData integrity protected.")
            return
        if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            try:
                self.db.execute("DELETE FROM Suppliers WHERE supplier_id = ?", (supplier_id,))
                self.db.commit()
                messagebox.showinfo("Success", "Deleted!")
                self.refresh_suppliers()
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
		# ==================== GOODS RECEIPT TABS ====================
    def create_goods_receipt_tab(self):
        """Create goods receipt tab"""
        gr_frame = ttk.Frame(self.notebook)
        self.notebook.add(gr_frame, text="📥 Goods Receipt")
    
        top_frame = ttk.Frame(gr_frame)
        top_frame.pack(side='top', fill='x', padx=10, pady=10)
        
        ttk.Label(top_frame, text="Record Goods Receipt", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Button(top_frame, text="➕ New Receipt", command=self.new_goods_receipt).pack(pady=5)
    
        history_frame = ttk.LabelFrame(gr_frame, text="Receipt History", padding=10)
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
        columns = ("ID", "PO#", "Supplier", "Invoice", "Items", "Total Received", "Total Accepted", "Date")
        self.receipt_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=20)
    
        widths = [50, 60, 150, 120, 60, 100, 100, 100]
        for i, col in enumerate(columns):
            self.receipt_tree.heading(col, text=col)
            self.receipt_tree.column(col, width=widths[i])
    
        self.receipt_tree.pack(side='left', fill='both', expand=True)
    
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical', command=self.receipt_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.receipt_tree.configure(yscrollcommand=scrollbar.set)
    
        # Bind double-click to view details
        self.receipt_tree.bind('<Double-1>', lambda e: self.view_receipt_details())
        
        self.refresh_receipt_history()
    
    def refresh_receipt_history(self):
        """Refresh goods receipt history - showing grouped receipts"""
        for item in self.receipt_tree.get_children():
            self.receipt_tree.delete(item)
        
        # Get unique receipts grouped by invoice number and PO
        self.db.execute('''
            SELECT 
                MIN(gr.receipt_id) as receipt_id,
                gr.po_number, 
                s.name, 
                gr.invoice_number,
                COUNT(DISTINCT gr.item_id) as item_count,
                SUM(gr.received_quantity) as total_received,
                SUM(gr.accepted_quantity) as total_accepted,
                gr.receipt_date
                FROM Goods_Receipt gr
                JOIN Suppliers s ON gr.supplier_id = s.supplier_id
            GROUP BY gr.invoice_number, gr.po_number, gr.receipt_date
            ORDER BY MIN(gr.receipt_id) 
        ''')
    
        for row in self.db.fetchall():
            self.receipt_tree.insert('', 'end', values=row)
    
    def view_receipt_details(self):
        """View detailed items in a receipt"""
        selected = self.receipt_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a receipt to view details")
            return
    
        values = self.receipt_tree.item(selected[0])['values']
        invoice_number = values[3]
    
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Receipt Details - Invoice: {invoice_number}")
        dialog.geometry("900x500")
        dialog.transient(self.app.root)
        dialog.grab_set()
    
        #Header info
        info_frame = ttk.LabelFrame(dialog, text="Receipt Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"PO #: {values[1]}  |  Supplier: {values[2]}  |  Invoice: {values[3]}  |  Date: {values[7]}", 
                font=('Arial', 10, 'bold')).pack()
    
        #Items details
        items_frame = ttk.LabelFrame(dialog, text="Items Received", padding=10)
        items_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item Name", "Received", "Accepted", "Rejected", "Notes")
        tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        
        widths = [250, 100, 100, 100, 200]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=widths[i])
    
        tree.pack(fill='both', expand=True)
    
        #Get items for this receipt
        self.db.execute('''
            SELECT i.name, gr.received_quantity, gr.accepted_quantity, 
                gr.rejected_quantity, gr.notes
            FROM Goods_Receipt gr
            JOIN Items i ON gr.item_id = i.item_id
            WHERE gr.invoice_number = ?
            ORDER BY i.name
            ''', (invoice_number,))
    
        for row in self.db.fetchall():
            tree.insert('', 'end', values=row)
    
    def new_goods_receipt(self):
        """Create new goods receipt - multi-item"""
        self.db.execute("SELECT COUNT(*) FROM Suppliers")
        if self.db.fetchone()[0] == 0:
            messagebox.showwarning("Warning", "Add suppliers first")
            return
    
        dialog = tk.Toplevel(self.app.root)
        dialog.title("New Goods Receipt - Multi-Item")
        dialog.geometry("1200x800")
        dialog.resizable(True, True)
        dialog.transient(self.app.root)
        dialog.grab_set()
    
        # Step 1: Supplier & Invoice Details
        header_frame = ttk.LabelFrame(dialog, text="Step 1: Supplier & Invoice Details", padding=15)
        header_frame.pack(fill='x', padx=10, pady=10)
    
        ttk.Label(header_frame, text="Supplier:*").grid(row=0, column=0, padx=10, pady=8, sticky='w')
    
        self.db.execute("SELECT supplier_id, name FROM Suppliers ORDER BY name")
        suppliers = self.db.fetchall()
        supplier_dict = {f"{s[1]} (ID: {s[0]})": s[0] for s in suppliers}
    
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(header_frame, textvariable=supplier_var, 
                                    values=list(supplier_dict.keys()), width=40, state='readonly')
        supplier_combo.grid(row=0, column=1, padx=10, pady=8)
    
        ttk.Label(header_frame, text="Purchase Order:*").grid(row=1, column=0, padx=10, pady=8, sticky='w')
        po_var = tk.StringVar()
        po_combo = ttk.Combobox(header_frame, textvariable=po_var, width=40, state='disabled')
        po_combo.grid(row=1, column=1, padx=10, pady=8)
    
        ttk.Label(header_frame, text="Invoice Number:*").grid(row=0, column=2, padx=10, pady=8, sticky='w')
        invoice_entry = ttk.Entry(header_frame, width=30)
        invoice_entry.grid(row=0, column=3, padx=10, pady=8)
    
        ttk.Label(header_frame, text="Receipt Date:*").grid(row=1, column=2, padx=10, pady=8, sticky='w')
        date_entry = ttk.Entry(header_frame, width=30)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.grid(row=1, column=3, padx=10, pady=8)
    
        # Step 2: Add Items
        items_input_frame = ttk.LabelFrame(dialog, text="Step 2: Add Items from PO", padding=10)
        items_input_frame.pack(fill='x', padx=10, pady=10)
    
        ttk.Label(items_input_frame, text="Select Item:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        item_var = tk.StringVar()
        item_combo = ttk.Combobox(items_input_frame, textvariable=item_var, width=40, state='disabled')
        item_combo.grid(row=0, column=1, padx=5, pady=5)
    
        ttk.Label(items_input_frame, text="Ordered:").grid(row=0, column=2, padx=5, pady=5)
        ordered_label = ttk.Label(items_input_frame, text="0", font=('Arial', 10, 'bold'), foreground='blue')
        ordered_label.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(items_input_frame, text="Received:*").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        recv_entry = ttk.Entry(items_input_frame, width=15, state='disabled')
        recv_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(items_input_frame, text="Accepted:*").grid(row=1, column=2, padx=5, pady=5)
        accept_entry = ttk.Entry(items_input_frame, width=15, state='disabled')
        accept_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(items_input_frame, text="Rejected:*").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        reject_entry = ttk.Entry(items_input_frame, width=15, state='disabled')
        reject_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(items_input_frame, text="Notes:").grid(row=2, column=2, padx=5, pady=5)
        notes_entry = ttk.Entry(items_input_frame, width=30, state='disabled')
        notes_entry.grid(row=2, column=3, padx=5, pady=5, columnspan=2)
        
        add_item_btn = ttk.Button(items_input_frame, text="➕ Add Item", state='disabled')
        add_item_btn.grid(row=3, column=0, columnspan=4, pady=10)
        
        # Step 3: Items List
        list_frame = ttk.LabelFrame(dialog, text="Step 3: Items in This Receipt", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ("Item Name", "Ordered", "Received", "Accepted", "Rejected", "Notes")
        items_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        col_widths = [200, 80, 80, 80, 80, 200]
        for i, col in enumerate(columns):
                items_tree.heading(col, text=col)
                items_tree.column(col, width=col_widths[i])
        
        items_tree.pack(side='left', fill='both', expand=True)
        
        list_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=items_tree.yview)
        list_scroll.pack(side='right', fill='y')
        items_tree.configure(yscrollcommand=list_scroll.set)
        
        # Summary
        summary_label = ttk.Label(dialog, text="Total Items: 0 | Total Received: 0 | Total Accepted: 0 | Total Rejected: 0", 
                                font=('Arial', 11, 'bold'), foreground='blue')
        summary_label.pack(pady=10)
        
        # Store data
        po_dict = {}
        item_dict = {}
        selected_items = []  # List of tuples: (item_id, item_name, ordered_qty, recv, accept, reject, notes)
        
        def update_summary():
            total_items = len(selected_items)
            total_recv = sum(item[3] for item in selected_items)
            total_accept = sum(item[4] for item in selected_items)
            total_reject = sum(item[5] for item in selected_items)
            summary_label.config(text=f"Total Items: {total_items} | Total Received: {total_recv} | Total Accepted: {total_accept} | Total Rejected: {total_reject}")
    
        
        def on_supplier_selected(event):
            """When supplier is selected, load their POs"""
            if not supplier_var.get():
                    return
        
            supplier_id = supplier_dict[supplier_var.get()]
            
            self.db.execute('''
                SELECT po_number, order_date, status 
                FROM Purchase_Orders 
                WHERE supplier_id = ? 
                ORDER BY po_number DESC
            ''', (supplier_id,))
            
            pos = self.db.fetchall()
            if not pos:
                messagebox.showinfo("Info", "No purchase orders for this supplier")
                po_combo['state'] = 'disabled'
                return
                
            po_dict.clear()
            po_list = [f"PO #{po[0]} - {po[1]} ({po[2]})" for po in pos]
            for i, po in enumerate(pos):
                po_dict[po_list[i]] = po[0]
            
            po_combo['values'] = po_list
            po_combo['state'] = 'readonly'
            po_combo.set('')
            
            #Reset items
            item_combo['state'] = 'disabled'
            item_combo.set('')
            selected_items.clear()
            for item in items_tree.get_children():
                items_tree.delete(item)
            update_summary()
            
        def on_po_selected(event):
            """When PO is selected, load its items"""
            if not po_var.get():
                return
        
            po_number = po_dict[po_var.get()]
        
            #Get items for this PO
            self.db.execute('''
                SELECT poi.item_id, i.name, poi.quantity
                FROM Purchase_Order_Items poi
                JOIN Items i ON poi.item_id = i.item_id
                WHERE poi.po_number = ?
            ''', (po_number,))
            
            items = self.db.fetchall()
            if not items:
                messagebox.showinfo("Info", "No items in this PO")
                item_combo['state'] = 'disabled'
                return
            
            item_dict.clear()
            item_list = [f"{item[1]} (Ordered: {item[2]})" for item in items]
            for i, item in enumerate(items):
                item_dict[item_list[i]] = (item[0], item[1], item[2])  # (id, name, qty)
            
            item_combo['values'] = item_list
            item_combo['state'] = 'readonly'
            item_combo.set('')
        
            # Enable entry fields
            recv_entry['state'] = 'normal'
            accept_entry['state'] = 'normal'
            reject_entry['state'] = 'normal'
            notes_entry['state'] = 'normal'
            add_item_btn['state'] = 'normal'
            
        def on_item_selected(event):
            """Show ordered quantity"""
            if item_var.get():
                _, _, ordered_qty = item_dict[item_var.get()]
                ordered_label.config(text=str(ordered_qty))
            else:
                ordered_label.config(text="0")
        
        def validate_item_quantities():
            """Validate item quantities"""
            try:
                recv = int(recv_entry.get())
                accept = int(accept_entry.get())
                reject = int(reject_entry.get())
                
                if recv <= 0:
                    messagebox.showerror("Error", "Received quantity must be positive")
                    return None
            
                if accept < 0 or reject < 0:
                    messagebox.showerror("Error", "Quantities cannot be negative")
                    return None
                
                if accept + reject != recv:
                    messagebox.showerror("Error", f"Accepted ({accept}) + Rejected ({reject}) must equal Received ({recv})")
                    return None
                
                return recv, accept, reject
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers")
                return None
        
        def add_item_to_list():
            """Add item to receipt list"""
            if not item_var.get():
                messagebox.showwarning("Warning", "Select an item")
                return
        
            item_id, item_name, ordered_qty = item_dict[item_var.get()]
            
            #Check if already added
            for existing in selected_items:
                if existing[0] == item_id:
                    messagebox.showwarning("Warning", "Item already added to this receipt")
                    return
            
            quantities = validate_item_quantities()
            if not quantities:
                return
            
            recv, accept, reject = quantities
            notes = notes_entry.get().strip()
            
            #Add to list
            selected_items.append((item_id, item_name, ordered_qty, recv, accept, reject, notes))
            items_tree.insert('', 'end', values=(item_name, ordered_qty, recv, accept, reject, notes))
            
            #Clear inputs
            item_var.set('')
            ordered_label.config(text="0")
            recv_entry.delete(0, tk.END)
            accept_entry.delete(0, tk.END)
            reject_entry.delete(0, tk.END)
            notes_entry.delete(0, tk.END)
            
            update_summary()
    
        def remove_item_from_list():
            """Remove selected item from list"""
            selected = items_tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Select item to remove")
                return
        
            idx = items_tree.index(selected[0])
            selected_items.pop(idx)
            items_tree.delete(selected[0])
            update_summary()
        
        def save_receipt():
            """Save the complete goods receipt"""
            if not supplier_var.get():
                messagebox.showerror("Error", "Select a supplier")
                return
            if not po_var.get():
                messagebox.showerror("Error", "Select a purchase order")
                return
            if not invoice_entry.get().strip():
                messagebox.showerror("Error", "Enter invoice number")
                return
            if not selected_items:
                messagebox.showerror("Error", "Add at least one item to the receipt")
                return
            
            try:
                supplier_id = supplier_dict[supplier_var.get()]
                po_number = po_dict[po_var.get()]
                invoice_no = invoice_entry.get().strip()
                receipt_date = date_entry.get()
                
                #Insert all items with same invoice number
                for item_id, item_name, ordered_qty, recv, accept, reject, notes in selected_items:
                    self.db.execute('''
                        INSERT INTO Goods_Receipt 
                        (po_number, item_id, supplier_id, invoice_number, received_quantity, 
                        accepted_quantity, rejected_quantity, receipt_date, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (po_number, item_id, supplier_id, invoice_no, recv, accept, reject, receipt_date, notes))
                
                # Update inventory with ONLY accepted quantity
                    self.db.execute('''
                        UPDATE Inventory 
                        SET quantity_on_hand = quantity_on_hand + ?, 
                            last_updated = ?
                        WHERE item_id = ?
                    ''', (accept, datetime.now(), item_id))
                
                # Check if all items in PO have been fully received
                self.db.execute('''
                    SELECT COUNT(*) FROM Purchase_Order_Items poi
                    WHERE poi.po_number = ?
                    AND poi.quantity > (
                        SELECT COALESCE(SUM(gr.received_quantity), 0)
                        FROM Goods_Receipt gr
                        WHERE gr.po_number = poi.po_number 
                        AND gr.item_id = poi.item_id
                    )
                ''', (po_number,))
                
                unreceived_items = self.db.fetchone()[0]
                
                # Update PO status
                if unreceived_items == 0:
                    self.db.execute('UPDATE Purchase_Orders SET status = "Completed" WHERE po_number = ?', (po_number,))
                else:
                    self.db.execute('UPDATE Purchase_Orders SET status = "Partially Received" WHERE po_number = ?', (po_number,))
                
                self.db.commit()
                
                #Summary message
                total_recv = sum(item[3] for item in selected_items)
                total_accept = sum(item[4] for item in selected_items)
                total_reject = sum(item[5] for item in selected_items)
                
                msg = f"Goods Receipt Recorded Successfully!\n\n"
                msg += f"Invoice: {invoice_no}\n"
                msg += f"Items: {len(selected_items)}\n"
                msg += f"Total Received: {total_recv} units\n"
                msg += f"Total Accepted: {total_accept} units (added to inventory)\n"
                msg += f"Total Rejected: {total_reject} units\n"
                
                messagebox.showinfo("Success", msg)
                dialog.destroy()
                self.app.refresh_all_tabs()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save receipt: {str(e)}")
    
        #Bind events
        supplier_combo.bind('<<ComboboxSelected>>', on_supplier_selected)
        po_combo.bind('<<ComboboxSelected>>', on_po_selected)
        item_combo.bind('<<ComboboxSelected>>', on_item_selected)
        add_item_btn.config(command=add_item_to_list)
        
        #Buttons frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="➖ Remove Selected Item", command=remove_item_from_list).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✅ Save Receipt", command=save_receipt).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side='right', padx=5)
        # ==================== ALERTS TAB ====================
        
    def create_alerts_tab(self):
        """Create alerts/reports tab"""
        alert_frame = ttk.Frame(self.notebook)
        self.notebook.add(alert_frame, text="⚠️ Alerts")
        
        top_btn_frame = ttk.Frame(alert_frame)
        top_btn_frame.pack(side='top', fill='x', padx=10, pady=8)
        
        ttk.Label(top_btn_frame, text="Low Stock Alerts", font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        ttk.Button(top_btn_frame, text="🔄 Refresh", command=self.refresh_alerts).pack(side='right', padx=3)
        
        columns = ("Item ID", "Item Name", "Current Stock", "Reorder Level", "Action Needed")
        self.alert_tree = ttk.Treeview(alert_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=180)
        
        self.alert_tree.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.refresh_alerts()
    
    def refresh_alerts(self):
        """Refresh low stock alerts"""
        for item in self.alert_tree.get_children():
            self.alert_tree.delete(item)
        
        self.db.execute('''
            SELECT i.item_id, i.name, inv.quantity_on_hand, inv.reorder_level
            FROM Items i
            JOIN Inventory inv ON i.item_id = inv.item_id
            WHERE inv.quantity_on_hand <= inv.reorder_level
            ORDER BY (inv.quantity_on_hand - inv.reorder_level)
        ''')
        
        for row in self.db.fetchall():
            action = f"Order {row[3] * 2 - row[2]} units"
            self.alert_tree.insert('', 'end', values=row + (action,))
    
