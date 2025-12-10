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
from tkinter import ttk
from database import Database
from purchase_module import PurchaseModule
from sales_module import SalesModule

class IntegratedManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Purchase & Sales Management System")
        self.root.geometry("1200x700")
        
        # Initialize database
        self.db = Database()
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize Purchase Module
        self.purchase_module = PurchaseModule(self.notebook, self.db, self)
        
        # Initialize Sales Module
        self.sales_module = SalesModule(self.notebook, self.db, self)
        
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
