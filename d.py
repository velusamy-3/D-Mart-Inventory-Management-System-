import sys
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QVBoxLayout, QMessageBox,QGridLayout)
import mysql.connector

# Load database configuration from JSON
def load_db_config():
    with open('db_config.json') as config_file:
        return json.load(config_file)

# Database Manager for interacting with MySQL
def create_database_and_tables():
    config = load_db_config()
    try:
        conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password']
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
        cursor.execute("USE inventory_db")

        # Create inventory table
        cursor.execute("""CREATE TABLE IF NOT EXISTS inventory (
            item_id INT AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(255) NOT NULL,
            quantity INT NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )""")

        # Create customers table
        cursor.execute("""CREATE TABLE IF NOT EXISTS customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            loyalty_points INT DEFAULT 0
        )""")

        # Create purchases table
        cursor.execute("""CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            item_id INT NOT NULL,
            quantity INT NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (item_id) REFERENCES inventory(item_id)
        )""")

        print("Database and tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()

class DatabaseManager:
    def __init__(self):
        config = load_db_config()
        self.conn = mysql.connector.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
        self.cursor = self.conn.cursor()

    def add_inventory_item(self, name, quantity, price):
        query = "INSERT INTO inventory (item_name, quantity, price) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (name, quantity, price))
        self.conn.commit()

    def update_inventory_item(self, item_id, quantity):
        query = "UPDATE inventory SET quantity = quantity - %s WHERE item_id = %s"
        self.cursor.execute(query, (quantity, item_id))
        self.conn.commit()

    def delete_inventory_item(self, item_id):
        query = "DELETE FROM inventory WHERE item_id = %s"
        self.cursor.execute(query, (item_id,))
        self.conn.commit()

    def get_inventory(self):
        self.cursor.execute("SELECT * FROM inventory")
        return self.cursor.fetchall()

    def add_customer(self, name, email, phone):
        query = "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (name, email, phone))
        self.conn.commit()

    def update_customer(self, customer_id, name, email, phone):
        query = "UPDATE customers SET name = %s, email = %s, phone = %s WHERE customer_id = %s"
        self.cursor.execute(query, (name, email, phone, customer_id))
        self.conn.commit()

    def delete_customer(self, customer_id):
        query = "DELETE FROM customers WHERE customer_id = %s"
        self.cursor.execute(query, (customer_id,))
        self.conn.commit()

    def get_customers(self):
        self.cursor.execute("SELECT * FROM customers")
        return self.cursor.fetchall()

    def log_purchase(self, customer_id, item_id, quantity, total_price):
        query = "INSERT INTO purchases (customer_id, item_id, quantity, total_price) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (customer_id, item_id, quantity, total_price))
        self.conn.commit()

    def get_purchase_history(self):
        self.cursor.execute("""
            SELECT p.purchase_id, c.name, i.item_name, p.quantity, p.total_price, p.purchase_date 
            FROM purchases p 
            JOIN customers c ON p.customer_id = c.customer_id 
            JOIN inventory i ON p.item_id = i.item_id
        """)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()

# Main Application Window
class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 500, 500)
        self.db = DatabaseManager()  # Connect to the MySQL database
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QGridLayout()
        
        # Set margins and spacing for the layout
        layout.setContentsMargins(10, 10, 10, 10)  # Adjust values as needed
        layout.setSpacing(4)  # Adjust spacing between widgets
    
        # Application heading
        self.heading_label = QLabel('D-Mart Inventory Management System', self)
        self.heading_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.heading_label.setAlignment(Qt.AlignCenter)
    
        # Create buttons for navigating to different views
        self.inventory_button = QPushButton('Inventory Data View', self)
        self.inventory_button.setFixedSize(250, 250)
        self.inventory_button.setStyleSheet("font-size: 18px; background-color: red;")
        self.inventory_button.clicked.connect(self.show_inventory_view)
    
        self.customer_button = QPushButton('Customer Details View', self)
        self.customer_button.setFixedSize(250, 250)
        self.customer_button.setStyleSheet("font-size: 18px; background-color: green;")
        self.customer_button.clicked.connect(self.show_customer_view)
    
        self.purchase_button = QPushButton('Buy Product View', self)
        self.purchase_button.setFixedSize(250, 250)
        self.purchase_button.setStyleSheet("font-size: 18px; background-color: blue;")
        self.purchase_button.clicked.connect(self.show_purchase_view)
    
        self.purchase_history_button = QPushButton('Purchase History View', self)
        self.purchase_history_button.setFixedSize(250, 250)
        self.purchase_history_button.setStyleSheet("font-size: 18px; background-color: coral;")
        self.purchase_history_button.clicked.connect(self.show_purchase_history_view)
    
        # Add heading and buttons to layout
        layout.addWidget(self.heading_label, 0, 0, 1, 4)  # Heading spans all columns
        layout.addWidget(self.inventory_button, 1, 0)
        layout.addWidget(self.customer_button, 1, 1)
        layout.addWidget(self.purchase_button, 1, 2)
        layout.addWidget(self.purchase_history_button, 1, 3)
    
        self.central_widget.setLayout(layout)
        
            
        
    def show_inventory_view(self):
        self.clear_central_widget()
        self.inventory_view = InventoryView(self)
        self.central_widget.layout().addWidget(self.inventory_view)

    def show_customer_view(self):
        self.clear_central_widget()
        self.customer_view = CustomerView(self)
        self.central_widget.layout().addWidget(self.customer_view)

    def show_purchase_view(self):
        self.clear_central_widget()
        self.purchase_view = PurchaseView(self)
        self.central_widget.layout().addWidget(self.purchase_view)

    def show_purchase_history_view(self):
        self.clear_central_widget()
        self.purchase_history_view = PurchaseHistoryView(self)
        self.central_widget.layout().addWidget(self.purchase_history_view)

    def clear_central_widget(self):
        while self.central_widget.layout().count():
            child = self.central_widget.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def closeEvent(self, event):
        self.db.close()  # Close the MySQL connection when the app closes

class InventoryView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Inventory form
        self.name_label = QLabel('Item Name:', self)
        self.name_input = QLineEdit(self)

        self.quantity_label = QLabel('Quantity:', self)
        self.quantity_input = QLineEdit(self)

        self.price_label = QLabel('Price:', self)
        self.price_input = QLineEdit(self)

        self.add_inventory_button = QPushButton('Add Inventory Item', self)
        self.add_inventory_button.clicked.connect(self.add_inventory_item)

        self.delete_inventory_button = QPushButton('Delete Inventory Item', self)
        self.delete_inventory_button.clicked.connect(self.delete_inventory_item)

        self.inventory_table = QTableWidget(self)
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Item Name", "Quantity", "Price"])
        self.load_inventory()

        # Back button
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.go_back)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(self.add_inventory_button)
        layout.addWidget(self.delete_inventory_button)
        layout.addWidget(self.inventory_table)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_inventory(self):
        items = self.parent.db.get_inventory()
        self.inventory_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item[0])))  # ID
            self.inventory_table.setItem(row, 1, QTableWidgetItem(item[1]))  # Item name
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(item[2])))  # Quantity
            self.inventory_table.setItem(row, 3, QTableWidgetItem(str(item[3])))  # Price

    def add_inventory_item(self):
        name = self.name_input.text()
        quantity = self.quantity_input.text()
        price = self.price_input.text()
        self.parent.db.add_inventory_item(name, quantity, price)
        self.load_inventory()

    def delete_inventory_item(self):
        selected_row = self.inventory_table.currentRow()
        if selected_row >= 0:
            item_id = self.inventory_table.item(selected_row, 0).text()
            self.parent.db.delete_inventory_item(item_id)
            self.load_inventory()

    def go_back(self):
        self.parent.clear_central_widget()
        self.parent.initUI()

class CustomerView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Customer form
        self.name_label = QLabel('Customer Name:', self)
        self.name_input = QLineEdit(self)

        self.email_label = QLabel('Email:', self)
        self.email_input = QLineEdit(self)

        self.phone_label = QLabel('Phone:', self)
        self.phone_input = QLineEdit(self)

        self.add_customer_button = QPushButton('Add Customer', self)
        self.add_customer_button.clicked.connect(self.add_customer)

        self.delete_customer_button = QPushButton('Delete Customer', self)
        self.delete_customer_button.clicked.connect(self.delete_customer)

        self.customer_table = QTableWidget(self)
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone"])
        self.load_customers()

        # Back button
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.go_back)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.add_customer_button)
        layout.addWidget(self.delete_customer_button)
        layout.addWidget(self.customer_table)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_customers(self):
        customers = self.parent.db.get_customers()
        self.customer_table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            self.customer_table.setItem(row, 0, QTableWidgetItem(str(customer[0])))  # ID
            self.customer_table.setItem(row, 1, QTableWidgetItem(customer[1]))  # Name
            self.customer_table.setItem(row, 2, QTableWidgetItem(customer[2]))  # Email
            self.customer_table.setItem(row, 3, QTableWidgetItem(customer[3]))  # Phone

    def add_customer(self):
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        self.parent.db.add_customer(name, email, phone)
        self.load_customers()

    def delete_customer(self):
        selected_row = self.customer_table.currentRow()
        if selected_row >= 0:
            customer_id = self.customer_table.item(selected_row, 0).text()
            self.parent.db.delete_customer(customer_id)
            self.load_customers()

    def go_back(self):
        self.parent.clear_central_widget()
        self.parent.initUI()

class PurchaseView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Purchase form
        self.customer_id_label = QLabel('Customer ID:', self)
        self.customer_id_input = QLineEdit(self)

        self.item_id_label = QLabel('Item ID:', self)
        self.item_id_input = QLineEdit(self)

        self.quantity_label = QLabel('Quantity:', self)
        self.quantity_input = QLineEdit(self)

        self.purchase_button = QPushButton('Purchase Item', self)
        self.purchase_button.clicked.connect(self.purchase_item)

        # Back button
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.go_back)

        layout.addWidget(self.customer_id_label)
        layout.addWidget(self.customer_id_input)
        layout.addWidget(self.item_id_label)
        layout.addWidget(self.item_id_input)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.purchase_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def purchase_item(self):
        customer_id = self.customer_id_input.text()
        item_id = self.item_id_input.text()
        quantity = self.quantity_input.text()

        # Get item price
        self.parent.db.cursor.execute("SELECT price, quantity FROM inventory WHERE item_id = %s", (item_id,))
        item = self.parent.db.cursor.fetchone()

        if item and item[1] >= int(quantity):  # Check if there's enough stock
            total_price = float(item[0]) * int(quantity)
            self.parent.db.log_purchase(customer_id, item_id, quantity, total_price)
            self.parent.db.update_inventory_item(item_id, quantity)  # Update inventory
            QMessageBox.information(self, 'Success', 'Purchase successful!')
        else:
            QMessageBox.warning(self, 'Error', 'Insufficient stock or invalid item ID!')

    def go_back(self):
        self.parent.clear_central_widget()
        self.parent.initUI()

class PurchaseHistoryView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.purchase_history_table = QTableWidget(self)
        self.purchase_history_table.setColumnCount(6)
        self.purchase_history_table.setHorizontalHeaderLabels(
            ["Purchase ID", "Customer Name", "Item Name", "Quantity", "Total Price", "Purchase Date"]
        )
        self.load_purchase_history()

        # Back button
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.go_back)

        layout.addWidget(self.purchase_history_table)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def load_purchase_history(self):
        purchases = self.parent.db.get_purchase_history()
        self.purchase_history_table.setRowCount(len(purchases))
        for row, purchase in enumerate(purchases):
            self.purchase_history_table.setItem(row, 0, QTableWidgetItem(str(purchase[0])))  # Purchase ID
            self.purchase_history_table.setItem(row, 1, QTableWidgetItem(purchase[1]))  # Customer Name
            self.purchase_history_table.setItem(row, 2, QTableWidgetItem(purchase[2]))  # Item Name
            self.purchase_history_table.setItem(row, 3, QTableWidgetItem(str(purchase[3])))  # Quantity
            self.purchase_history_table.setItem(row, 4, QTableWidgetItem(str(purchase[4])))  # Total Price
            self.purchase_history_table.setItem(row, 5, QTableWidgetItem(str(purchase[5])))  # Purchase Date

    def go_back(self):
        self.parent.clear_central_widget()
        self.parent.initUI()

if __name__ == "__main__":
    create_database_and_tables()
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())

