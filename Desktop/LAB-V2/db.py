# db.py
import sqlite3
from typing import List, Tuple, Any

DB_FILE = "lab.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")  # Enforce foreign keys
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Customers
    c.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        category TEXT CHECK(category IN ('Clinic','Doctor','Lab')),
        notes TEXT
    )
    """)

    # Suppliers
    c.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('Porcelain', 'Laminate', 'PFM', 'Post NPG', 'Milling', 'Customize Abutment'))
    )
    """)


    # Orders
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        day_arrival_number INTEGER CHECK(day_arrival_number BETWEEN 1 AND 30),
        month_arrival_number INTEGER CHECK(month_arrival_number BETWEEN 1 AND 12),
        year_arrival_number INTEGER,
        day_departure_number INTEGER CHECK(day_departure_number BETWEEN 1 AND 30),
        month_departure_number INTEGER CHECK(month_departure_number BETWEEN 1 AND 12),
        year_departure_number INTEGER,
        doctor_name TEXT,
        patient_name TEXT,
        dent_category TEXT,
        co_worker_owns TEXT,
        no_units INTEGER CHECK(no_units >= 1),
        color TEXT CHECK(color IN (
            'A1','A2','A3','A3.5','A4','B1','B2','B3','B4',
            'C1','C2','C3','C4','D2','D3','D4','OM1','OM2','OM3','BW',
            'BL1','BL2','BL3','BL4'
        )),
        price REAL CHECK(price >= 0),
        status TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE
    )
    """)

    # Reminders
    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        reminder_date TEXT,
        note TEXT,
        FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL
    )
    """)

    # Price List
    c.execute("""
    CREATE TABLE IF NOT EXISTS price_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dent_category TEXT NOT NULL UNIQUE,
        price_per_unit REAL NOT NULL CHECK(price_per_unit >= 0)
    )
    """)

    conn.commit()
    conn.close()

    # Initialize default prices if empty
    init_price_list()

# -------------------------
# Customers
# -------------------------
def add_customer(name: str, phone: str, category: str, notes: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO customers (name, phone, category, notes) VALUES (?,?,?,?)",
              (name, phone, category, notes))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_customers() -> List[Tuple[Any,...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, phone, category, notes FROM customers ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def edit_customer(id_: int, name: str, phone: str, category: str, notes: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE customers SET name=?, phone=?, category=?, notes=? WHERE id=?",
              (name, phone, category, notes, id_))
    conn.commit()
    conn.close()

def delete_customer(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM customers WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# -------------------------
# Suppliers
# -------------------------
def add_supplier(name: str, type_: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO suppliers (name, type) VALUES (?,?)", (name, type_))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_suppliers() -> List[Tuple[Any,...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, type FROM suppliers ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def edit_supplier(id_: int, name: str, type_: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE suppliers SET name=?, type=? WHERE id=?", (name, type_, id_))
    conn.commit()
    conn.close()

def delete_supplier(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM suppliers WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# -------------------------
# Orders
# -------------------------
def add_order(customer_id: int, 
              day_arrival_number: int, month_arrival_number: int, year_arrival_number: int,
              day_departure_number: int | None, month_departure_number: int | None, year_departure_number: int | None,
              doctor_name: str, patient_name: str, dent_category: str, co_worker_owns: str,
              no_units: int, color: str, price: float, status: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (
            customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
            day_departure_number, month_departure_number, year_departure_number, doctor_name,
            patient_name, dent_category, co_worker_owns, no_units, color, price, status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
          day_departure_number, month_departure_number, year_departure_number, doctor_name,
          patient_name, dent_category, co_worker_owns, no_units, color, price, status))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_orders() -> List[Tuple[Any,...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
               day_departure_number, month_departure_number, year_departure_number, doctor_name,
               patient_name, dent_category, co_worker_owns, no_units, color, price, status
        FROM orders ORDER BY id
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def edit_order(id_: int, customer_id: int,
               day_arrival_number: int, month_arrival_number: int, year_arrival_number: int,
               day_departure_number: int | None, month_departure_number: int | None, year_departure_number: int | None,
               doctor_name: str, patient_name: str, dent_category: str, co_worker_owns: str,
               no_units: int, color: str, price: float, status: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE orders SET
            customer_id=?, day_arrival_number=?, month_arrival_number=?, year_arrival_number=?,
            day_departure_number=?, month_departure_number=?, year_departure_number=?, doctor_name=?,
            patient_name=?, dent_category=?, co_worker_owns=?, no_units=?, color=?, 
            price=?, status=?
        WHERE id=?
    """, (customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
          day_departure_number, month_departure_number, year_departure_number, doctor_name,
          patient_name, dent_category, co_worker_owns, no_units, color, 
          price, status, id_))
    conn.commit()
    conn.close()

def delete_order(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# -------------------------
# Reminders
# -------------------------
def add_reminder(customer_id: int, reminder_date: str, note: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO reminders (customer_id, reminder_date, note) VALUES (?,?,?)",
              (customer_id, reminder_date, note))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_reminders() -> List[Tuple[Any,...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, customer_id, reminder_date, note FROM reminders ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def edit_reminder(id_: int, customer_id: int, reminder_date: str, note: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE reminders SET customer_id=?, reminder_date=?, note=? WHERE id=?",
              (customer_id, reminder_date, note, id_))
    conn.commit()
    conn.close()

def delete_reminder(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# -------------------------
# Price List
# -------------------------
def init_price_list():
    """Initialize default price list if empty."""
    prices = get_price_list()
    if not prices:
        default_items = [
            ("Zirconia Implant", 1900000.0),
            ("Zirconia Crown", 1750000.0),
            ("Laminate (Emax)", 3800000.0),
            ("Glass Ceramic (Crown & Laminate)", 3500000.0),
            ("Inlay / Onlay / 2-unit Crown (Zirconia)", 2700000.0),
            ("Inlay / Onlay / 2-unit Crown (Emax)", 3800000.0),
            ("PFM Bridge", 1750000.0),
            ("PFM Crown", 1450000.0),
            ("Ni.Cr Bridge", 700000.0),
            ("NPG Bridge", 700000.0),
            ("Full Zirconia Crown (Single Unit)", 1100000.0),
            ("ZIR Bridge", 800000.0),
            ("Full Zirconia Crown (Multi-unit, Anterior)", 1700000.0),
            ("Full Zirconia Crown (Multi-unit, Posterior)", 1500000.0),
            ("PMMA", 500000.0),
            ("Resin", 180000.0),
            ("Full Arch Cast Framework", 700000.0),
            ("Mock-up", 1500000.0),
            ("Partial Cast Framework", 700000.0),
            ("Full Arch Cast Framework (Zirconia)", 900000.0),
            ("Gingival Mask", 150000.0),
            ("Base & Wax", 700000.0),
            ("Metal-Ceramic Crown & Bridge (Full Arch)", 1100000.0),
            ("Metal-Ceramic Crown & Bridge (Partial Arch)", 1300000.0),
            ("Metal-Ceramic Crown & Bridge (14 Units)", 1800000.0),
            ("European Company Abutment", 1500000.0),
            ("European Company Abutment (Full Arch)", 850000.0)
        ]
        for item, price in default_items:
            add_price_item(item, price)

def add_price_item(dent_category: str, price_per_unit: float) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO price_list (dent_category, price_per_unit) VALUES (?,?)",
              (dent_category, price_per_unit))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_price_list() -> List[Tuple[Any,...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, dent_category, price_per_unit FROM price_list ORDER BY dent_category")
    rows = c.fetchall()
    conn.close()
    return rows

def edit_price_item(id_: int, dent_category: str, price_per_unit: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE price_list SET dent_category=?, price_per_unit=? WHERE id=?",
              (dent_category, price_per_unit, id_))
    conn.commit()
    conn.close()

def delete_price_item(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM price_list WHERE id=?", (id_,))
    conn.commit()
    conn.close()

def get_price_by_category(dent_category: str) -> float:
    """Return price per unit for a dent category, or 0.0 if not found."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT price_per_unit FROM price_list WHERE dent_category = ?", (dent_category,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0.0

def get_dent_categories() -> List[str]:
    """Get all dent categories from price_list table."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT dent_category FROM price_list ORDER BY dent_category")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows] if rows else []

def calculate_total_price(dent_category_with_qty: str) -> float:
    """
    Calculate total price from string like 'Zirconia Implant:2, PFM Crown:1'.
    Handles old format (without :qty) by assuming qty=1.
    """
    if not dent_category_with_qty:
        return 0.0
    total = 0.0
    for item in dent_category_with_qty.split(","):
        item = item.strip()
        if not item:
            continue
        if ":" in item:
            # New format: "Category:qty"
            cat, qty_str = item.rsplit(":", 1)
            try:
                qty = int(qty_str)
                price_per = get_price_by_category(cat.strip())
                total += price_per * qty
            except (ValueError, TypeError):
                continue
        else:
            # Old format: "Category" → assume qty=1
            price_per = get_price_by_category(item)
            total += price_per
    return total

# Initialize on import
init_db()