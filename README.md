# Inventory Management System with GST Support

*A College Project – Integrated Purchase & Sales Management System for India*

---

## 📘 About the Project

**Inventory Management System** is a desktop-based application built as a **college project** to demonstrate practical understanding of how real businesses structure their data and workflows.

The focus of this project is not government portal automation, but **clean transactional accounting**:

* GUI development using Python Tkinter
* Relational database design with SQLite
* Real-world purchase & sales workflows
* Modular software architecture
* **GST-aware accounting design for India**

The system models how GST is **captured, stored, and summarized** inside a business before filing, rather than attempting to automate statutory filing itself.

This project is intended strictly for **educational and architectural demonstration purposes**, not for production or commercial deployment.

---

## 🎯 What This Project Is For

The objective of this project is to model a **mini ERP-style system** where different departments interact with shared, GST-aware data.

* **Purchase Department** records purchases and captures *Input GST*
* **Sales Department** records sales and captures *Output GST*
* **Inventory Control** reflects only physically accepted stock

The system demonstrates how value (and tax) flows through a business:

**Items → Purchase Orders → Goods Receipt → Inventory → Sales Orders → Invoices → Reports**

GST is treated as **data captured at the transaction level**, not as a value reconstructed later.

---

## 🛠 Technologies Used

* **Python 3** – Core programming language
* **Tkinter / ttk** – GUI framework for desktop interface
* **SQLite3** – Embedded relational database
* Modular architecture with separate Python modules for different business functions

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

## 🧾 GST Handling Philosophy (Important)

This system does **not** file GST returns.

Instead, it prepares **accurate, auditable GST data** that a business would use *before* filing:

* GST is stored **per item** at the time of purchase and sale
* Purchase transactions generate **Input GST**
* Sales transactions generate **Output GST**
* Reports summarize GST amounts automatically

This mirrors how real accounting systems work internally. Actual filing (GSTR-1, GSTR-3B, portal submission, OTPs, validations) is intentionally **out of scope** for this project.

**Net GST Liability (Conceptual):**

`GST Payable = Output GST – Input GST`

The system ensures both sides of this equation are captured cleanly and transparently.

---

## ⚠️ Known Limitations

### GST Scope Limitations

* No CGST / SGST / IGST split
* No place-of-supply logic
* No HSN-wise statutory summaries
* No return matching (GSTR-1 vs 2B)
* No credit reversal or time-limit rules

These are **regulatory layers**, not architectural flaws, and can be added on top of the existing design.

### System Limitations

* No user authentication or role-based access
* No export to PDF or Excel
* Single-user desktop system
* No email or portal integration

---

## ▶️ How to Run the Project

1. Ensure Python 3.7 or higher is installed
2. Navigate to the project directory
3. Run:

```bash
python main.py
```

The application will initialize the database automatically and launch the GUI.


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

## 📸Screenshots

![screenshot1](screenshots/APPFINAL1.png)
![screenshot2](screenshots/APPFINAL2.png)
![screenshot3](screenshots/APPFINAL3.png)
![screenshot4](screenshots/APPFINAL4.png)
![screenshot5](screenshots/APPFINAL5.png)
![screenshot6](screenshots/APPFINAL7.png)
![screenshot7](screenshots/APPFINAL8.png)
![screenshot8](screenshots/APPFINAL9.png)
![screenshot9](screenshots/APPFINAL6.png)
