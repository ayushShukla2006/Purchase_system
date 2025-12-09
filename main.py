"""
Main Application File - Integrated Purchase & Sales Management System
Run this file to start the application

File Structure:
- main.py (this file)
- database.py (database initialization)
- purchase_module.py (purchase department functions)
- sales_module.py (sales department functions)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from database import Database
from purchase_module import PurchaseModule
from sales_module import SalesModule

class DataValidator:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return True  # Empty is okay
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number (10 digits)"""
        if not phone:
            return True  # Empty is okay
        pattern = r'^\d{10}'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_gstin(gstin):
        """Validate GSTIN format (15 characters)"""
        if not gstin:
            return True  # Empty is okay
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}'
        return re.match(pattern, gstin) is not None
    
    @staticmethod
    def validate_positive_number(value, field_name="Value"):
        """Validate positive number"""
        try:
            num = float(value)
            if num <= 0:
                messagebox.showerror("Validation Error", f"{field_name} must be positive")
                return False
            return True
        except ValueError:
            messagebox.showerror("Validation Error", f"{field_name} must be a valid number")
            return False
    
    @staticmethod
    def validate_non_negative_number(value, field_name="Value"):
        """Validate non-negative number"""
        try:
            num = float(value)
            if num < 0:
                messagebox.showerror("Validation Error", f"{field_name} cannot be negative")
                return False
            return True
        except ValueError:
            messagebox.showerror("Validation Error", f"{field_name} must be a valid number")
            return False
    
    @staticmethod
    def validate_required(value, field_name="Field"):
        """Validate required field"""
        if not value or str(value).strip() == "":
            messagebox.showerror("Validation Error", f"{field_name} is required")
            return False
        return True
    
    @staticmethod
    def validate_date(date_str):
        """Validate date format YYYY-MM-DD"""
        if not date_str:
            return True  # Empty is okay
        pattern = r'^\d{4}-\d{2}-\d{2}'
        return re.match(pattern, date_str) is not None

class IntegratedManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Purchase & Sales Management System")
        self.root.geometry("1200x700")
        
        # Initialize database
        self.db = Database()
        
        # Set up theme
        self.dark_mode = self.db.get_setting('dark_mode') == 'on'
        self.setup_theme()
        
        # Create menu bar
        self.create_menu()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize Purchase Module
        self.purchase_module = PurchaseModule(self.notebook, self.db, self)
        
        # Initialize Sales Module
        self.sales_module = SalesModule(self.notebook, self.db, self)
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        settings_menu.add_separator()
        settings_menu.add_command(label="Exit", command=self.on_closing)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_theme(self):
        """Setup color theme based on dark mode setting"""
        style = ttk.Style()
        
        if self.dark_mode:
            # Dark mode colors
            self.root.config(bg='#2b2b2b')
            style.theme_use('clam')
            
            style.configure('TFrame', background='#2b2b2b')
            style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
            style.configure('TButton', background='#404040', foreground='#ffffff')
            style.map('TButton', background=[('active', '#505050')])
            style.configure('TNotebook', background='#2b2b2b')
            style.configure('TNotebook.Tab', background='#404040', foreground='#ffffff')
            style.map('TNotebook.Tab', background=[('selected', '#505050')])
            
            style.configure('Treeview', 
                background='#3a3a3a',
                foreground='#ffffff',
                fieldbackground='#3a3a3a',
                borderwidth=0)
            style.configure('Treeview.Heading',
                background='#505050',
                foreground='#ffffff',
                borderwidth=1)
            style.map('Treeview', background=[('selected', '#4a4a4a')])
            
            style.configure('TEntry', fieldbackground='#404040', foreground='#ffffff')
            style.configure('TCombobox', fieldbackground='#404040', foreground='#ffffff')
            style.configure('TLabelframe', background='#2b2b2b', foreground='#ffffff')
            style.configure('TLabelframe.Label', background='#2b2b2b', foreground='#ffffff')
        else:
            # Light mode colors
            self.root.config(bg='#f0f0f0')
            style.theme_use('clam')
            
            style.configure('TFrame', background='#f0f0f0')
            style.configure('TLabel', background='#f0f0f0', foreground='#000000')
            style.configure('TButton', background='#e0e0e0', foreground='#000000')
            style.map('TButton', background=[('active', '#d0d0d0')])
            style.configure('TNotebook', background='#f0f0f0')
            style.configure('TNotebook.Tab', background='#e0e0e0', foreground='#000000')
            style.map('TNotebook.Tab', background=[('selected', '#ffffff')])
            
            style.configure('Treeview',
                background='#ffffff',
                foreground='#000000',
                fieldbackground='#ffffff')
            style.configure('Treeview.Heading',
                background='#d0d0d0',
                foreground='#000000')
            style.map('Treeview', background=[('selected', '#0078d7')])
    
    def toggle_dark_mode(self):
        """Toggle between dark and light mode"""
        self.dark_mode = not self.dark_mode
        self.db.set_setting('dark_mode', 'on' if self.dark_mode else 'off')
        
        messagebox.showinfo("Theme Changed", 
            "Dark mode " + ("enabled" if self.dark_mode else "disabled") + 
            "!\nPlease restart the application for changes to take full effect.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Integrated Purchase & Sales Management System
Version 2.0

Features:
• Multi-item Purchase & Sales Orders
• GST Support (Purchase & Sales)
• Inventory Management
• Goods Receipt with QC
• Invoice Generation
• Sales Reports & Analytics
• Dark Mode Support
• Data Validation

Developed for College Project"""
        messagebox.showinfo("About", about_text)
    
    def refresh_all_tabs(self):
        """Refresh all tabs across both modules"""
        self.purchase_module.refresh_all()
        self.sales_module.refresh_all()
    
    def on_closing(self):
        """Handle application close"""
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
