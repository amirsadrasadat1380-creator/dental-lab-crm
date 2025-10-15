-- models.sql
-- Updated to match Streamlit app's actual column names and logic

-- -------------------
-- Customers Table
-- -------------------
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    category TEXT CHECK(category IN ('Clinic','Doctor','Lab')),
    notes TEXT
);

-- -------------------
-- Suppliers Table
-- -------------------
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('Porcelain', 'Laminate', 'PFM', 'Post NPG', 'Milling', 'Customize Abutment'))
);

-- -------------------
-- Orders Table
-- -------------------
-- Updated Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    day_arrival_number INTEGER CHECK(day_arrival_number BETWEEN 1 AND 30),
    month_arrival_number INTEGER CHECK(month_arrival_number BETWEEN 1 AND 12),
    year_arrival_number INTEGER,  -- NEW
    day_departure_number INTEGER CHECK(day_departure_number BETWEEN 1 AND 30),
    month_departure_number INTEGER CHECK(month_departure_number BETWEEN 1 AND 12),
    year_departure_number INTEGER,  -- NEW
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
);

-- -------------------
-- Reminders Table
-- -------------------
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    reminder_date TEXT, -- ISO format: 'YYYY-MM-DD'
    note TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL
);