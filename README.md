# Inventory Management System with GST Support
*A College Project – Integrated Purchase & Sales Management System for India*

---

## 📘 About the Project

**Inventory Management System** is a desktop-based application built as a **college project** to demonstrate practical understanding of:

- GUI development using Python Tkinter
- Relational database design with SQLite
- Real-world business workflows
- Modular software architecture
- Indian GST (Goods and Services Tax) compliance

The application simulates how a small business manages its **inventory, purchases, sales, goods receipt, and billing** using a local database and a graphical interface with comprehensive GST support.

This project is intended for **educational purposes**, not for production or commercial deployment.

---

## 🎯 What This Project Is For

The main objective of this project is to model a **basic ERP-style system** where different departments interact with shared data:

- **Purchase Department** - Manages suppliers, purchase orders, and goods receipt
- **Sales Department** - Handles customers, sales orders, and invoicing
- **Inventory Control** - Tracks stock levels and alerts for low inventory

It demonstrates how data flows through an integrated business system:

**Items → Purchase Orders → Goods Receipt → Inventory → Sales Orders → Invoices → Reports**

---

## 🛠 Technologies Used

- **Python 3** - Core programming language
- **Tkinter / ttk** - GUI framework for desktop interface
- **SQLite3** - Embedded relational database
- Modular architecture with separate Python modules for different business functions

---

## 📂 Project Structure

```text
inventory-management/
├── main.py                 # Application entry point & window manager
├── database.py             # Database schema and initialization
├── purchase_module.py      # Purchase orders, suppliers & goods receipt
├── sales_module.py         # Sales orders, customers, invoices & reports
├── screenshots/
│   ├── APPFINAL1.png
│   ├── APPFINAL2.png
│   ├── APPFINAL3.png
│   ├── APPFINAL4.png
│   └── APPFINAL5.png
└── README.md
```

---

## ✅ Features That Are Working

### 📦 Inventory & Items Management
- ✅ Add, edit, and delete inventory items with full validation
- ✅ Separate **Purchase Rate** and **Selling Rate** with individual GST percentages
- ✅ Automatic price calculation: `Final Price = Rate + (Rate × GST%)`
- ✅ Real-time price preview while adding/editing items
- ✅ HSN code support for GST compliance
- ✅ Track quantity on hand with automatic updates
- ✅ Reorder level alerts for low stock items (visual indicators)
- ✅ Prevent deletion of items referenced in orders or receipts

### 🏢 Supplier Management
- ✅ Add, edit, view, and delete suppliers
- ✅ GSTIN (GST Identification Number) tracking
- ✅ Contact details and payment terms
- ✅ Data integrity: Prevent deletion of suppliers with purchase orders

### 👥 Customer Management
- ✅ Complete customer database with GSTIN support
- ✅ Credit limit tracking
- ✅ Contact information management
- ✅ Payment terms configuration
- ✅ Protected deletion (cannot delete customers with orders)

### 🛒 Purchase Orders (Multi-Item Support)
- ✅ **Create multi-item purchase orders** with multiple products
- ✅ Item-wise GST calculation and display
- ✅ Real-time order total calculation (Subtotal + GST = Total)
- ✅ Purchase order status tracking:
  - **Pending** - Order created, waiting for goods
  - **Partially Received** - Some items received
  - **Completed** - All items fully received
- ✅ View detailed PO breakdown with GST amounts
- ✅ **Toggle visibility** of completed orders (hide/show)
- ✅ Prevent deletion of POs with goods receipts

### 📥 Goods Receipt (Advanced Multi-Item)
- ✅ **Multi-item goods receipt** - Receive multiple items in one invoice
- ✅ Track **Received**, **Accepted**, and **Rejected** quantities separately
- ✅ **Inventory updates only with accepted quantity** (rejected items don't affect stock)
- ✅ **Validation**: Received quantity cannot exceed ordered quantity
- ✅ **Edit receipts** with smart validation:
  - Double-click cells to edit
  - Shows ordered quantity for reference (read-only)
  - Auto-calculates rejected = received - accepted
  - Real-time summary updates
- ✅ Duplicate invoice prevention
- ✅ Invoice number tracking with date stamps
- ✅ Notes field for quality issues or remarks
- ✅ Automatic PO status updates based on received quantities

### 🛍️ Sales Orders (Multi-Item Support)
- ✅ **Create multi-item sales orders** for customers
- ✅ Item-wise GST calculation for selling prices
- ✅ **Real-time stock validation** - Cannot sell more than available
- ✅ Automatic inventory deduction after order creation
- ✅ View detailed breakdown with GST amounts
- ✅ Sales order status: Completed
- ✅ Generate invoices directly from sales orders

### 📄 Invoices & Billing
- ✅ Generate invoices from sales orders (one-click)
- ✅ Prevent duplicate invoice creation
- ✅ Track invoice status: **Paid** / **Unpaid**
- ✅ Visual indicators (red for unpaid, green for paid)
- ✅ Due date tracking (default 30 days)
- ✅ Mark invoices as paid
- ✅ Delete invoices with confirmation (warns if paid)
- ✅ Complete GST breakdown on invoices

### 📊 Sales Reports & Analytics
- ✅ **Total sales value** and **GST collected**
- ✅ Total orders count
- ✅ Completed vs pending orders
- ✅ **Unpaid invoices** - Count and total amount
- ✅ **Paid invoices** - Count and total amount
- ✅ **Top 10 selling items** by quantity and revenue
- ✅ One-click report refresh

### ⚠️ Alerts & Notifications
- ✅ **Low stock alerts** - Shows items below reorder level
- ✅ Highlighted in red on inventory view
- ✅ Suggested reorder quantity calculation
- ✅ Sorted by urgency (most critical first)

### 💾 Data Integrity
- ✅ Foreign key constraints enforced
- ✅ Cascade prevention on deletions
- ✅ Transaction management with rollback on errors
- ✅ Validation at multiple levels (UI, business logic, database)

---

## 🆕 Recent Improvements

### Enhanced Goods Receipt Editing
- **Smart cell editing** - Double-click any cell to edit, press Enter to save
- **Ordered quantity display** - Always visible for reference (cannot be edited)
- **Intelligent validation** - Cannot exceed ordered quantities
- **Auto-calculation** - Rejected quantity updates automatically
- **Live summary** - Real-time totals at bottom of screen
- **Better UX** - Escape to cancel, instructions displayed

### Purchase Orders Management
- **Completed orders toggle** - Hide completed POs by default to reduce clutter
- **Show/Hide button** - View historical completed orders when needed
- **Visual distinction** - Completed orders appear grayed out
- **Cleaner interface** - Focus on active orders

---

## ⚠️ Known Limitations

### Current Restrictions
- ❌ No user authentication or role-based access control
- ❌ No export to PDF or Excel (CSV)
- ❌ No backup/restore functionality
- ❌ Single-user system (no multi-user support)
- ❌ No email integration for invoices
- ❌ No barcode scanning support
- ❌ No batch/lot tracking
- ❌ No expiry date management

### Design Choices
- Inventory is **immediately reduced** when sales order is created (not when invoice is paid)
- Deleting a sales order does **not restore inventory** (intentional to prevent misuse)
- One invoice per sales order (no partial invoicing)

---

## ▶️ How to Run the Project

### Prerequisites
- Python 3.7 or higher
- No additional packages required (uses standard library only)

### Running the Application

1. **Clone or download** the project files
2. **Navigate** to the project directory:
   ```bash
   cd inventory-management
   ```
3. **Run the main file**:
   ```bash
   python3 main.py
   ```
   or on Windows:
   ```bash
   python main.py
   ```

The application will automatically:
- Create `integrated_system.db` SQLite database
- Initialize all required tables
- Launch the GUI window

---

## 🚀 Possible Future Enhancements

### High Priority
- [ ] PDF invoice generation
- [ ] Export reports to Excel/CSV
- [ ] User login system with roles (Admin, Purchaser, Sales)
- [ ] Dashboard with key metrics and charts

### Medium Priority
- [ ] Purchase returns and credit notes
- [ ] Sales returns and refunds
- [ ] Email invoice to customers
- [ ] Backup and restore database
- [ ] Search and filter across all modules

### Low Priority
- [ ] Dark mode theme
- [ ] Barcode scanning integration
- [ ] Multiple warehouse locations
- [ ] Batch/lot tracking for items
- [ ] Expiry date management
- [ ] SMS notifications for low stock

---

## 📸 Screenshots

![Inventory Management](screenshots/APPFINAL1.png)

![Purchase Orders](screenshots/APPFINAL2.png)

![Goods Receipt](screenshots/APPFINAL3.png)

![Sales Orders](screenshots/APPFINAL4.png)

![Reports](screenshots/APPFINAL5.png)

---

## 🧪 Testing the System

### Sample Workflow

1. **Add Items** - Create inventory items with purchase and selling prices
2. **Add Supplier** - Create a supplier with GSTIN
3. **Create PO** - Order items from supplier
4. **Receive Goods** - Record goods receipt (accept/reject quantities)
5. **Add Customer** - Create customer with GSTIN
6. **Create SO** - Sell items to customer (inventory auto-reduces)
7. **Generate Invoice** - Create invoice from sales order
8. **Mark Paid** - Update invoice payment status
9. **View Reports** - Check sales analytics and top items

---

## 📌 Important Notes

### GST Compliance
This system follows Indian GST structure:
- Purchase GST and Selling GST tracked separately
- HSN code support
- GSTIN tracking for suppliers and customers
- Subtotal, GST Amount, and Total displayed clearly

### Data Integrity
- The system enforces referential integrity
- Cannot delete records that are referenced elsewhere
- All monetary values use 2 decimal precision
- Timestamps track last updates

### Educational Purpose
This project was created **strictly for academic learning** and demonstrates:
- Professional software structure
- Business logic implementation
- Database normalization
- User interface design
- Error handling and validation

It prioritizes **clarity and correctness** over production-grade performance optimization.

---

## 👨‍💻 Author

**Mehroom**  
Inventory Management System with GST Support  
College Project - 2024

---

## 📝 License

This project is for educational purposes only.  
Not intended for commercial use or production deployment.

---

## 🙏 Acknowledgments

- Python and Tkinter communities for excellent documentation
- SQLite for providing a robust embedded database
- College faculty for project guidance

---

**Last Updated:** December 2025  
**Version:** 2.0 (Multi-item + GST Support)
