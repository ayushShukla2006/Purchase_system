"""
Database Module - Handles all database operations
"""

import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='integrated_system.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        """Initialize all database tables"""
        
        # SHARED TABLES (used by both Purchase and Sales)
        
        # Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                unit_of_measure TEXT,
                unit_price REAL,
                selling_price REAL
            )
        ''')
        
        # Inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Inventory (
                item_id INTEGER PRIMARY KEY,
                quantity_on_hand INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 10,
                location TEXT,
                last_updated TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # PURCHASE DEPARTMENT TABLES
        
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                payment_terms TEXT
            )
        ''')
        
        # Purchase Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Orders (
                po_number INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                order_date DATE,
                expected_delivery DATE,
                status TEXT DEFAULT 'Pending',
                total_amount REAL,
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
            )
        ''')
        
        # Purchase Order Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Order_Items (
                po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                subtotal REAL,
                FOREIGN KEY (po_number) REFERENCES Purchase_Orders(po_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # Goods Receipt table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Goods_Receipt (
                receipt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_number INTEGER,
                item_id INTEGER,
                supplier_id INTEGER,
                invoice_number TEXT,
                received_quantity INTEGER,
                accepted_quantity INTEGER,
                rejected_quantity INTEGER,
                receipt_date DATE,
                notes TEXT,
                FOREIGN KEY (po_number) REFERENCES Purchase_Orders(po_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id),
                FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id)
            )
        ''')
        
        # SALES DEPARTMENT TABLES
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                credit_limit REAL,
                payment_terms TEXT
            )
        ''')
        
        # Sales Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales_Orders (
                so_number INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                order_date DATE,
                delivery_date DATE,
                status TEXT DEFAULT 'Pending',
                total_amount REAL,
                FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
            )
        ''')
        
        # Sales Order Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales_Order_Items (
                so_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                so_number INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                subtotal REAL,
                FOREIGN KEY (so_number) REFERENCES Sales_Orders(so_number),
                FOREIGN KEY (item_id) REFERENCES Items(item_id)
            )
        ''')
        
        # Invoices table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                so_number INTEGER,
                customer_id INTEGER,
                invoice_date DATE,
                due_date DATE,
                total_amount REAL,
                status TEXT DEFAULT 'Unpaid',
                FOREIGN KEY (so_number) REFERENCES Sales_Orders(so_number),
                FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
            )
        ''')
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        """Execute a query"""
        return self.cursor.execute(query, params)
    
    def fetchall(self):
        """Fetch all results"""
        return self.cursor.fetchall()
    
    def fetchone(self):
        """Fetch one result"""
        return self.cursor.fetchone()
    
    def commit(self):
        """Commit changes"""
        self.conn.commit()
    
    def lastrowid(self):
        """Get last inserted row ID"""
        return self.cursor.lastrowid
    
    def close(self):
        """Close database connection"""
        self.conn.close()
