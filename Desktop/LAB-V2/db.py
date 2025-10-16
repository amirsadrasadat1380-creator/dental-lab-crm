# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Tuple, Any
import os

# --- CONFIGURATION ---
DATABASE_URL = "postgresql://neondb_owner:npg_8OQ4bidvJtVx@ep-rapid-dust-adifrhxq-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_conn():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    """Create all required tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    # Customers
    c.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT,
        category TEXT CHECK(category IN ('Clinic','Doctor','Lab')),
        notes TEXT,
        price_tier TEXT DEFAULT 'Standard'
    )
    """)

    # Suppliers
    c.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('Porcelain', 'Laminate', 'PFM', 'Post NPG', 'Milling', 'Customize Abutment'))
    )
    """)

    # Orders
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
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
        status TEXT
    )
    """)

    # Reminders
    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
        reminder_date TEXT,
        note TEXT
    )
    """)

    # Price List
    c.execute("""
    CREATE TABLE IF NOT EXISTS price_list (
        id SERIAL PRIMARY KEY,
        dent_category TEXT NOT NULL UNIQUE,
        price_per_unit REAL NOT NULL CHECK(price_per_unit >= 0)
    )
    """)

    conn.commit()
    conn.close()
    init_price_list()

# --- CUSTOMERS ---
def add_customer(name: str, phone: str, category: str, notes: str, price_tier: str = "Standard") -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO customers (name, phone, category, notes, price_tier) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (name, phone, category, notes, price_tier)
    )
    new_id = c.fetchone()["id"]
    conn.commit()
    conn.close()
    return new_id

def get_customers() -> List[Tuple[Any, ...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, phone, category, notes, price_tier FROM customers ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [tuple(row.values()) for row in rows]

def edit_customer(id_: int, name: str, phone: str, category: str, notes: str, price_tier: str = "Standard"):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE customers SET name=%s, phone=%s, category=%s, notes=%s, price_tier=%s WHERE id=%s",
        (name, phone, category, notes, price_tier, id_)
    )
    conn.commit()
    conn.close()

def delete_customer(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM customers WHERE id=%s", (id_,))
    conn.commit()
    conn.close()

# --- SUPPLIERS ---
def add_supplier(name: str, type_: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO suppliers (name, type) VALUES (%s, %s) RETURNING id", (name, type_))
    new_id = c.fetchone()["id"]
    conn.commit()
    conn.close()
    return new_id

def get_suppliers() -> List[Tuple[Any, ...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, type FROM suppliers ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [tuple(row.values()) for row in rows]

def edit_supplier(id_: int, name: str, type_: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE suppliers SET name=%s, type=%s WHERE id=%s", (name, type_, id_))
    conn.commit()
    conn.close()

def delete_supplier(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM suppliers WHERE id=%s", (id_,))
    conn.commit()
    conn.close()

# --- ORDERS ---
def add_order(
    customer_id: int,
    day_arrival_number: int, month_arrival_number: int, year_arrival_number: int,
    day_departure_number: int, month_departure_number: int, year_departure_number: int,
    doctor_name: str, patient_name: str, dent_category: str, co_worker_owns: str,
    no_units: int, color: str, price: float, status: str
) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (
            customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
            day_departure_number, month_departure_number, year_departure_number,
            doctor_name, patient_name, dent_category, co_worker_owns,
            no_units, color, price, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
        day_departure_number, month_departure_number, year_departure_number,
        doctor_name, patient_name, dent_category, co_worker_owns,
        no_units, color, price, status
    ))
    new_id = c.fetchone()["id"]
    conn.commit()
    conn.close()
    return new_id

def get_orders() -> List[Tuple[Any, ...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
               day_departure_number, month_departure_number, year_departure_number,
               doctor_name, patient_name, dent_category, co_worker_owns,
               no_units, color, price, status
        FROM orders ORDER BY id
    """)
    rows = c.fetchall()
    conn.close()
    return [tuple(row.values()) for row in rows]

def edit_order(
    id_: int,
    customer_id: int,
    day_arrival_number: int, month_arrival_number: int, year_arrival_number: int,
    day_departure_number: int, month_departure_number: int, year_departure_number: int,
    doctor_name: str, patient_name: str, dent_category: str, co_worker_owns: str,
    no_units: int, color: str, price: float, status: str
):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE orders SET
            customer_id=%s, day_arrival_number=%s, month_arrival_number=%s, year_arrival_number=%s,
            day_departure_number=%s, month_departure_number=%s, year_departure_number=%s,
            doctor_name=%s, patient_name=%s, dent_category=%s, co_worker_owns=%s,
            no_units=%s, color=%s, price=%s, status=%s
        WHERE id=%s
    """, (
        customer_id, day_arrival_number, month_arrival_number, year_arrival_number,
        day_departure_number, month_departure_number, year_departure_number,
        doctor_name, patient_name, dent_category, co_worker_owns,
        no_units, color, price, status, id_
    ))
    conn.commit()
    conn.close()

def delete_order(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=%s", (id_,))
    conn.commit()
    conn.close()

# --- REMINDERS ---
def add_reminder(customer_id: int, reminder_date: str, note: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO reminders (customer_id, reminder_date, note) VALUES (%s, %s, %s) RETURNING id",
              (customer_id, reminder_date, note))
    new_id = c.fetchone()["id"]
    conn.commit()
    conn.close()
    return new_id

def get_reminders() -> List[Tuple[Any, ...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, customer_id, reminder_date, note FROM reminders ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return [tuple(row.values()) for row in rows]

def edit_reminder(id_: int, customer_id: int, reminder_date: str, note: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE reminders SET customer_id=%s, reminder_date=%s, note=%s WHERE id=%s",
              (customer_id, reminder_date, note, id_))
    conn.commit()
    conn.close()

def delete_reminder(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id=%s", (id_,))
    conn.commit()
    conn.close()

# --- PRICE LIST ---
def init_price_list():
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
            ("Gingival Mask", 1500000.0),
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
    c.execute("INSERT INTO price_list (dent_category, price_per_unit) VALUES (%s, %s) RETURNING id",
              (dent_category, price_per_unit))
    new_id = c.fetchone()["id"]
    conn.commit()
    conn.close()
    return new_id

def get_price_list() -> List[Tuple[Any, ...]]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, dent_category, price_per_unit FROM price_list ORDER BY dent_category")
    rows = c.fetchall()
    conn.close()
    return [tuple(row.values()) for row in rows]

def edit_price_item(id_: int, dent_category: str, price_per_unit: float):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE price_list SET dent_category=%s, price_per_unit=%s WHERE id=%s",
              (dent_category, price_per_unit, id_))
    conn.commit()
    conn.close()

def delete_price_item(id_: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM price_list WHERE id=%s", (id_,))
    conn.commit()
    conn.close()

def get_price_by_category(dent_category: str) -> float:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT price_per_unit FROM price_list WHERE dent_category = %s", (dent_category,))
    row = c.fetchone()
    conn.close()
    return row["price_per_unit"] if row else 0.0

def calculate_total_price(dent_category_with_qty: str, customer_id: int = None) -> float:
    if not dent_category_with_qty:
        return 0.0
    total = 0.0
    tier = get_customer_price_tier(customer_id) if customer_id else "Standard"
    for item in dent_category_with_qty.split(","):
        item = item.strip()
        if ":" in item:
            cat, qty_str = item.rsplit(":", 1)
            try:
                qty = int(qty_str)
                base_price = get_price_by_category(cat.strip())
                adjusted_price = base_price * 0.90 if tier == "Legacy" else base_price
                total += adjusted_price * qty
            except (ValueError, TypeError):
                continue
    return total

def get_customer_price_tier(customer_id: int) -> str:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT price_tier FROM customers WHERE id = %s", (customer_id,))
    result = c.fetchone()
    conn.close()
    return result["price_tier"] if result else "Standard"

def get_dent_categories() -> List[str]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT dent_category FROM price_list ORDER BY dent_category")
    rows = c.fetchall()
    conn.close()
    return [row["dent_category"] for row in rows] if rows else []

# Initialize tables on import
init_db()