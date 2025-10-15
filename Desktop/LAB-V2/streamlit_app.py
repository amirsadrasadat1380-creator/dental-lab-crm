# app-V1.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from db import (
    add_customer, get_customers, edit_customer, delete_customer,
    add_order, get_orders, edit_order, delete_order,
    add_supplier, get_suppliers, edit_supplier, delete_supplier,
    add_reminder, get_reminders, edit_reminder, delete_reminder,
    get_price_list, add_price_item, edit_price_item, delete_price_item,
    get_price_by_category, calculate_total_price, get_dent_categories
)
st.set_page_config(page_title="CRM Lab", layout="wide", initial_sidebar_state="expanded")
# Simple styling
PRIMARY = "#152A46"
ACCENT = "#D4AF37"
st.markdown(
    f"""
    <style>
    .sidebar .sidebar-content {{ background-color: {PRIMARY}; color: white; }}
    .stButton>button {{ background-color: {ACCENT}; color: black; border-radius:6px; padding:6px 10px; }}
    .stDataFrame {{ border: 1px solid #ddd; }}
    </style>
    """, unsafe_allow_html=True
)
# -------------------------
# Sidebar navigation
# -------------------------
st.sidebar.title("Unique Complex")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Customers", "Orders", "Suppliers", "Reminders", "Price List", "Reports"]
)
# helper for rerun
def do_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        st.stop()
# -------------------------
# Dashboard
# -------------------------
if page == "Dashboard":
    st.title("🏠 Dashboard — Unique Complex")
    customers = pd.DataFrame(get_customers(), columns=["ID", "Name", "Phone", "Category", "Notes"])
    orders = pd.DataFrame(get_orders(), columns=[
        "ID", "Customer_ID", "Day_Arrival_Number", "Month_Arrival_Number", "Year_Arrival_Number",
        "Day_Departure_Number", "Month_Departure_Number", "Year_Departure_Number", "Doctor_Name",
        "Patient_Name", "Dent_Category", "Co_Worker_Owns", "No_Units", "Color", "Price", "Status"
    ])
    reminders = pd.DataFrame(get_reminders(), columns=["ID","Customer_ID","Reminder_Date","Note"])
    suppliers = pd.DataFrame(get_suppliers(), columns=["ID","Name","Type"])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Customers", len(customers))
    c2.metric("Total Orders", len(orders))
    # Incomplete = no departure date set (NULL)
    incomplete_orders = len(orders[orders["Day_Departure_Number"].isna()]) if not orders.empty else 0
    c3.metric("Incomplete Orders", incomplete_orders)
    c4.metric("Pending Reminders", len(reminders))
    c5.metric("Suppliers", len(suppliers))
# -------------------------
# Customers Page
# -------------------------
elif page == "Customers":
    st.title("👥 Customers")
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_customers"):
            st._rerun()
    c_main, c_filters = st.columns([3, 1])
    # Add form
    with c_main.expander("➕ Add Customer", expanded=True):
        with st.form("add_customer_form"):
            name = st.text_input("Name", key="add_c_name")
            phone = st.text_input("Phone", key="add_c_phone")
            category = st.selectbox("Category", ["Clinic", "Doctor", "Lab"], key="add_c_cat")
            notes = st.text_area("Notes", key="add_c_notes")
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                if not name.strip():
                    st.warning("Name required")
                else:
                    new_id = add_customer(name.strip(), phone.strip(), category, notes.strip())
                    st.success(f"Customer added (ID {new_id})")
                    do_rerun()
    # Filters
    with c_filters.expander("🔍 Filters", expanded=True):
        name_filter = st.text_input("Name contains", key="cust_filter_name")
        id_filter = st.text_input("ID exact", key="cust_filter_id")
        category_filter = st.selectbox("Category", ["All", "Clinic", "Doctor", "Lab"], key="cust_filter_cat")
        apply_filter = st.button("Apply Filter", key="cust_filter_btn")
    # Get & filter
    customers_list = get_customers()
    df = pd.DataFrame(customers_list, columns=["ID","Name","Phone","Category","Notes"])
    if apply_filter:
        if name_filter.strip():
            df = df[df["Name"].str.contains(name_filter.strip(), case=False, na=False)]
        if id_filter.strip().isdigit():
            df = df[df["ID"] == int(id_filter.strip())]
        if category_filter != "All":
            df = df[df["Category"] == category_filter]
    st.subheader("All Customers")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        ids = df["ID"].tolist()
        # Edit block
        st.markdown("### ✏️ Edit customer")
        edit_id = st.selectbox("Select ID to edit", [""] + ids, key="cust_edit_select")
        if edit_id != "":
            sel = df[df["ID"] == int(edit_id)].iloc[0]
            with st.form(f"cust_edit_form_{edit_id}"):
                new_name = st.text_input("Name", value=sel["Name"], key=f"cust_e_name_{edit_id}")
                new_phone = st.text_input("Phone", value=sel["Phone"] or "", key=f"cust_e_phone_{edit_id}")
                new_cat = st.selectbox("Category", ["Clinic","Doctor","Lab"],
                                       index=["Clinic","Doctor","Lab"].index(sel["Category"]),
                                       key=f"cust_e_cat_{edit_id}")
                new_notes = st.text_area("Notes", value=sel["Notes"] or "", key=f"cust_e_notes_{edit_id}")
                edit_sub = st.form_submit_button("Update Customer")
                if edit_sub:
                    edit_customer(int(edit_id), new_name.strip(), new_phone.strip(), new_cat, new_notes.strip())
                    st.success(f"Customer {edit_id} updated")
                    do_rerun()
        # Delete block
        st.markdown("### 🗑 Delete customer")
        del_id = st.selectbox("Select ID to delete", [""] + ids, key="cust_del_select")
        if del_id != "" and st.button("Delete Selected Customer", key="cust_del_btn"):
            delete_customer(int(del_id))
            st.success(f"Customer {del_id} deleted")
            do_rerun()
        # Export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", csv, file_name="customers.csv", mime="text/csv")
    else:
        st.info("No customers to display.")
# -------------------------
elif page == "Orders":
    st.title("📝 Orders")
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_orders"):
            st._rerun()
    # === MAIN LAYOUT ===
    main_col, filter_col = st.columns([3, 1])
    customers = get_customers()
    suppliers = get_suppliers()
    dent_categories = get_dent_categories()
    if not dent_categories:
        dent_categories = [
            "Zirconia Implant", "Zirconia Crown", "Laminate (Emax)",
            "Glass Ceramic (Crown & Laminate)", "Inlay / Onlay / 2-unit Crown (Zirconia)",
            "Inlay / Onlay / 2-unit Crown (Emax)", "PFM Bridge", "PFM Crown",
            "Ni.Cr Bridge", "NPG Bridge", "Full Zirconia Crown (Single Unit)",
            "ZIR Bridge", "Full Zirconia Crown (Multi-unit, Anterior)",
            "Full Zirconia Crown (Multi-unit, Posterior)", "PMMA", "Resin",
            "Full Arch Cast Framework", "Mock-up", "Partial Cast Framework",
            "Full Arch Cast Framework (Zirconia)", "Gingival Mask", "Base & Wax",
            "Metal-Ceramic Crown & Bridge (Full Arch)", "Metal-Ceramic Crown & Bridge (Partial Arch)",
            "Metal-Ceramic Crown & Bridge (14 Units)", "European Company Abutment",
            "European Company Abutment (Full Arch)"
        ]
    # === FILTERS (NO NESTED COLUMNS) ===
    with filter_col:
        with st.expander("🔍 Filters", expanded=True):
            st.markdown("### 📅 Date Filter")
            filter_type = st.radio("Type", ["All", "From", "Range"], key="date_filter_type", label_visibility="collapsed")
            if filter_type != "All":
                st.write("**From**")
                from_day = st.number_input("Day", 1, 30, 1, key="from_day")
                from_month = st.number_input("Month", 1, 12, 1, key="from_month")
                from_year = st.number_input("Year", 1300, 1500, 1404, key="from_year")
                if filter_type == "Range":
                    st.write("**To**")
                    to_day = st.number_input("Day", 1, 30, 30, key="to_day")
                    to_month = st.number_input("Month", 1, 12, 12, key="to_month")
                    to_year = st.number_input("Year", 1300, 1500, 1404, key="to_year")
            st.markdown("### 🔍 Text Filters")
            id_filter = st.text_input("Order ID", key="order_filter_id")
            cust_filter = st.text_input("Customer", key="order_filter_customer")
            doctor_filter = st.text_input("Doctor", key="order_filter_doc")
            status_filter = st.text_input("Status", key="order_filter_status")
            st.markdown("")
            apply_filter = st.button("Apply Filters", use_container_width=True, key="apply_filters_btn")
    # === ADD ORDER FORM (NO COLUMNS INSIDE FORM) ===
    with main_col:
        with st.expander("➕ Add New Order", expanded=True):
            with st.form("add_order_form"):
                # Customer
                cust_display = [f"{c[0]} - {c[1]}" for c in customers] if customers else []
                if cust_display:
                    sel_customer = st.selectbox("Customer", cust_display, key="add_o_customer")
                    sel_c_id = int(sel_customer.split(" - ")[0])
                else:
                    st.warning("No customers available.")
                    sel_c_id = None
                # Arrival Dates (FLAT - NO COLUMNS)
                st.markdown("### 📅 Arrival (Lunar Calendar)")
                day_arrival = st.number_input("Day", 1, 30, 1, key="add_o_day_arr")
                month_arrival = st.number_input("Month", 1, 12, 1, key="add_o_month_arr")
                year_arrival = st.number_input("Year", 1300, 1500, 1404, key="add_o_year_arr")
                # Departure Dates
                st.markdown("### 📅 Departure (Lunar Calendar)")
                not_departed = st.checkbox("Not departed yet", key="add_not_departed")
                if not not_departed:
                    day_departure = st.number_input("Day", 1, 30, 1, key="add_o_day_dep")
                    month_departure = st.number_input("Month", 1, 12, 1, key="add_o_month_dep")
                    year_departure = st.number_input("Year", 1300, 1500, 1404, key="add_o_year_dep")
                else:
                    day_departure = month_departure = year_departure = None
                # Order Details
                st.markdown("### 📋 Order Details")
                doctor = st.text_input("Doctor Name", key="add_o_doc")
                patient = st.text_input("Patient Name", key="add_o_pat")
                # Dent Categories (FLAT LIST - NO COLUMNS)
                st.markdown("### 🦷 Dent Categories")
                dent_cat_with_qty = []
                total_units = 0
                for i, cat in enumerate(dent_categories):
                    qty = st.number_input(
                        cat,
                        min_value=0,
                        max_value=100,
                        value=0,
                        key=f"add_o_qty_{i}"
                    )
                    if qty > 0:
                        dent_cat_with_qty.append(f"{cat}:{qty}")
                        total_units += qty
                dent_cat = ", ".join(dent_cat_with_qty) if dent_cat_with_qty else ""
                # Rest of form
                sup_choices_list = [f"{s[0]} - {s[1]}" for s in suppliers] if suppliers else []
                sup_select = st.multiselect("Co-Workers", sup_choices_list, key="add_o_sup")
                co_worker_ids_str = ",".join([s.split(" - ")[0] for s in sup_select]) if sup_select else ""
                color = st.selectbox("Color", [
                    'A1','A2','A3','A3.5','A4','B1','B2','B3','B4',
                    'C1','C2','C3','C4','D2','D3','D4','OM1','OM2','OM3','BW',
                    'BL1','BL2','BL3','BL4'
                ], key="add_o_color")
                status = st.text_input("Status", key="add_o_stat")
                total_price = calculate_total_price(dent_cat)
                st.info(f"💰 Total: {total_price:,.0f} IRR | 📦 Units: {total_units}")
                # ✅ SUBMIT BUTTON - DIRECT CHILD OF FORM
                submitted = st.form_submit_button("Add Order", use_container_width=True)
                if submitted:
                    if sel_c_id is None:
                        st.warning("Add a customer first.")
                    else:
                        new_id = add_order(
                            sel_c_id,
                            int(day_arrival), int(month_arrival), int(year_arrival),
                            day_departure, month_departure, year_departure,
                            doctor.strip(), patient.strip(), dent_cat,
                            co_worker_ids_str, total_units, color, float(total_price), status.strip()
                        )
                        st.success(f"✅ Order {new_id} added")
                        do_rerun()
        # === ORDERS TABLE ===
        st.subheader("📋 All Orders")
        orders_list = get_orders()
        df = pd.DataFrame(orders_list, columns=[
            "ID", "Customer_ID", "Day_Arrival_Number", "Month_Arrival_Number", "Year_Arrival_Number",
            "Day_Departure_Number", "Month_Departure_Number", "Year_Departure_Number", "Doctor_Name",
            "Patient_Name", "Dent_Category", "Co_Worker_Owns", "No_Units", "Color", "Price", "Status"
        ])
        # Apply filters
        if apply_filter or filter_type != "All":
            if filter_type != "All":
                def is_date_in_range(row):
                    day, month, year = row["Day_Arrival_Number"], row["Month_Arrival_Number"], row["Year_Arrival_Number"]
                    if pd.isna(day) or pd.isna(month) or pd.isna(year):
                        return False
                    current = (int(year), int(month), int(day))
                    from_tuple = (from_year, from_month, from_day)
                    to_tuple = (to_year, to_month, to_day)
                    if filter_type == "From":
                        return current >= from_tuple
                    elif filter_type == "Range":
                        return from_tuple <= current <= to_tuple
                    return True
                df = df[df.apply(is_date_in_range, axis=1)]
            if id_filter.strip().isdigit():
                df = df[df["ID"] == int(id_filter.strip())]
            if cust_filter.strip():
                df = df[df["Customer"].str.contains(cust_filter.strip(), case=False, na=False)]
            if doctor_filter.strip():
                df = df[df["Doctor_Name"].str.contains(doctor_filter.strip(), case=False, na=False)]
            if status_filter.strip():
                df = df[df["Status"].str.contains(status_filter.strip(), case=False, na=False)]
        # Map customer names
        id_to_name = {str(c[0]): c[1] for c in customers}
        sup_id_name_map = {str(s[0]): s[1] for s in suppliers}
        def co_names_field(s):
            if not s or pd.isna(s):
                return ""
            ids = [i.strip() for i in str(s).split(",") if i.strip()]
            return ", ".join([sup_id_name_map.get(i, f"ID {i}") for i in ids])
        if not df.empty:
            df["Customer"] = df["Customer_ID"].astype(str).map(id_to_name).fillna("⚠️ Deleted")
            df["Co_Worker_Names"] = df["Co_Worker_Owns"].apply(co_names_field)
            # Display table with departure status
            df["Departure_Status"] = df.apply(
                lambda row: "✅ Departed" if pd.notna(row["Day_Departure_Number"]) else "⏳ Not Departed",
                axis=1
            )
            display_cols = [
                "ID", "Customer", "Patient_Name", "Doctor_Name", "Dent_Category",
                "Co_Worker_Names", "No_Units", "Color", "Price", "Status",
                "Day_Arrival_Number", "Month_Arrival_Number", "Year_Arrival_Number",
                "Departure_Status",
                "Day_Departure_Number", "Month_Departure_Number", "Year_Departure_Number"
            ]
            st.dataframe(df[display_cols], use_container_width=True)
            csv = df[display_cols].to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Orders", csv, "orders.csv", "text/csv", use_container_width=True)
            # === EDIT/DELETE SECTION ===
            st.markdown("### ✏️ Edit / 🗑️ Delete Order")
            edit_del_col1, edit_del_col2 = st.columns(2)
            with edit_del_col1:
                edit_id = st.selectbox("Edit Order ID", [""] + df["ID"].tolist(), key="order_edit_select")
                if edit_id != "":
                    sel = df[df["ID"] == edit_id].iloc[0]
                    # ✅ EDIT FORM (NO COLUMNS INSIDE FORM)
                    with st.form(f"order_edit_form_{edit_id}"):
                        cust_display = [f"{c[0]} - {c[1]}" for c in customers] if customers else []
                        if cust_display:
                            sel_c_pref = f"{sel['Customer_ID']} - {id_to_name.get(str(sel['Customer_ID']), '')}"
                            try:
                                idx_pref = cust_display.index(sel_c_pref)
                            except ValueError:
                                idx_pref = 0
                            new_cust = st.selectbox("Customer", cust_display, index=idx_pref, key=f"order_e_cust_{edit_id}")
                            new_cust_id = int(new_cust.split(" - ")[0])
                        else:
                            new_cust_id = sel["Customer_ID"]
                        # Arrival Dates (FLAT)
                        st.markdown("### 📅 Arrival (Lunar Calendar)")
                        new_day_arrival = st.number_input("Day", 1, 30, int(sel["Day_Arrival_Number"]), key=f"order_e_day_arr_{edit_id}")
                        new_month_arrival = st.number_input("Month", 1, 12, int(sel["Month_Arrival_Number"]), key=f"order_e_month_arr_{edit_id}")
                        new_year_arrival = st.number_input("Year", 1300, 1500, int(sel["Year_Arrival_Number"]), key=f"order_e_year_arr_{edit_id}")
                        # Departure Dates
                        st.markdown("### 📅 Departure (Lunar Calendar)")
                        current_departed = not (pd.isna(sel["Day_Departure_Number"]) or sel["Day_Departure_Number"] is None)
                        not_departed = st.checkbox(
                            "Not departed yet",
                            value=not current_departed,
                            key=f"edit_not_departed_{edit_id}"
                        )
                        if not not_departed:
                            new_day_departure = st.number_input("Day", 1, 30, 
                                int(sel["Day_Departure_Number"]) if current_departed else 1, key=f"order_e_day_dep_{edit_id}")
                            new_month_departure = st.number_input("Month", 1, 12, 
                                int(sel["Month_Departure_Number"]) if current_departed else 1, key=f"order_e_month_dep_{edit_id}")
                            new_year_departure = st.number_input("Year", 1300, 1500, 
                                int(sel["Year_Departure_Number"]) if current_departed else 1404, key=f"order_e_year_dep_{edit_id}")
                        else:
                            new_day_departure = new_month_departure = new_year_departure = None
                        # Order Details
                        new_doc = st.text_input("Doctor Name", value=sel["Doctor_Name"] or "", key=f"order_e_doc_{edit_id}")
                        new_pat = st.text_input("Patient Name", value=sel["Patient_Name"] or "", key=f"order_e_pat_{edit_id}")
                        # Dent Categories (FLAT LIST)
                        existing_dict = {}
                        if sel["Dent_Category"]:
                            for item in sel["Dent_Category"].split(","):
                                item = item.strip()
                                if ":" in item:
                                    cat, qty = item.rsplit(":", 1)
                                    existing_dict[cat.strip()] = int(qty.strip())
                                else:
                                    existing_dict[item] = 1
                        st.markdown("### 🦷 Dent Categories")
                        dent_cat_with_qty = []
                        total_units = 0
                        for i, cat in enumerate(dent_categories):
                            current_qty = existing_dict.get(cat, 0)
                            qty = st.number_input(
                                cat,
                                min_value=0,
                                max_value=100,
                                value=current_qty,
                                key=f"edit_o_qty_{edit_id}_{i}"
                            )
                            if qty > 0:
                                dent_cat_with_qty.append(f"{cat}:{qty}")
                                total_units += qty
                        new_dent_cat_str = ", ".join(dent_cat_with_qty) if dent_cat_with_qty else ""
                        # Rest of form
                        sup_choices_list = [f"{s[0]} - {s[1]}" for s in suppliers] if suppliers else []
                        current_ids = sel["Co_Worker_Owns"] or ""
                        current_sel = []
                        if current_ids:
                            for sid in str(current_ids).split(","):
                                sid = sid.strip()
                                if sid and sid in sup_id_name_map:
                                    current_sel.append(f"{sid} - {sup_id_name_map[sid]}")
                        new_sup = st.multiselect("Co-Workers", sup_choices_list, default=current_sel, key=f"order_e_sup_{edit_id}")
                        new_co_worker_ids = ",".join([s.split(" - ")[0] for s in new_sup]) if new_sup else ""
                        color_options = ['A1','A2','A3','A3.5','A4','B1','B2','B3','B4','C1','C2','C3','C4','D2','D3','D4','OM1','OM2','OM3','BW','BL1','BL2','BL3','BL4']
                        try:
                            default_color_index = color_options.index(sel["Color"])
                        except (ValueError, TypeError):
                            default_color_index = 0
                        new_color = st.selectbox("Color", color_options, index=default_color_index, key=f"order_e_color_{edit_id}")
                        new_total_price = calculate_total_price(new_dent_cat_str)
                        st.info(f"💰 Total: {new_total_price:,.0f} IRR | 📦 Units: {total_units}")
                        new_status = st.text_input("Status", value=sel["Status"] or "", key=f"order_e_stat_{edit_id}")
                        # ✅ SUBMIT BUTTON
                        if st.form_submit_button("Update Order", use_container_width=True):
                            edit_order(
                                int(edit_id),
                                int(new_cust_id),
                                int(new_day_arrival), int(new_month_arrival), int(new_year_arrival),
                                new_day_departure, new_month_departure, new_year_departure,
                                new_doc.strip(),
                                new_pat.strip(),
                                new_dent_cat_str,
                                new_co_worker_ids,
                                total_units,
                                new_color,
                                float(new_total_price),
                                new_status.strip()
                            )
                            st.success(f"✅ Order {edit_id} updated")
                            do_rerun()
            with edit_del_col2:
                del_id = st.selectbox("Delete Order ID", [""] + df["ID"].tolist(), key="order_del_select")
                if del_id != "":
                    if st.button("🗑️ Delete Order", use_container_width=True, key="order_del_btn"):
                        delete_order(int(del_id))
                        st.success(f"🗑️ Order {del_id} deleted")
                        do_rerun()
        else:
            st.info("📭 No orders match your filters. Try adjusting them or add a new order.")
# -------------------------
# Suppliers Page
# -------------------------
elif page == "Suppliers":
    st.title("🏭 Suppliers")
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_suppliers"):
            st._rerun()
    c_main, c_filters = st.columns([3,1])
    # Add supplier
    with c_main.expander("➕ Add Supplier", expanded=True):
        with st.form("add_supplier_form"):
            name = st.text_input("Name", key="add_s_name")
            s_type = st.selectbox("Type", ["Porcelain", "Laminate", "PFM", "Post NPG", "Milling", "Customize Abutment"], key="add_s_type")
            add_sub = st.form_submit_button("Add Supplier")
            if add_sub:
                if not name.strip():
                    st.warning("Name required")
                else:
                    new_id = add_supplier(name.strip(), s_type)
                    st.success(f"Supplier added (ID {new_id})")
                    do_rerun()
    # Filters
    with c_filters.expander("🔍 Filters", expanded=True):
        name_filter = st.text_input("Name contains", key="sup_filter_name")
        type_filter = st.selectbox("Type", ["All","Porcelain","Laminate","PFM","Post NPG","Milling","Customize Abutment"], key="sup_filter_type")
        apply_filter = st.button("Apply Filters", key="sup_filter_btn")
    suppliers_list = get_suppliers()
    df = pd.DataFrame(suppliers_list, columns=["ID","Name","Type"])
    if apply_filter:
        if name_filter.strip():
            df = df[df["Name"].str.contains(name_filter.strip(), case=False, na=False)]
        if type_filter != "All":
            df = df[df["Type"] == type_filter]
    st.subheader("All Suppliers")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        ids = df["ID"].tolist()
        st.markdown("### ✏️ Edit Supplier")
        edit_id = st.selectbox("Select Supplier ID to edit", [""] + ids, key="sup_edit_select")
        if edit_id != "":
            sel = df[df["ID"] == int(edit_id)].iloc[0]
            with st.form(f"sup_edit_form_{edit_id}"):
                new_name = st.text_input("Name", value=sel["Name"], key=f"sup_e_name_{edit_id}")
                new_type = st.selectbox("Type", ["Porcelain","Laminate","PFM","Post NPG","Milling","Customize Abutment"],
                                        index=["Porcelain","Laminate","PFM","Post NPG","Milling","Customize Abutment"].index(sel["Type"]),
                                        key=f"sup_e_type_{edit_id}")
                if st.form_submit_button("Update Supplier"):
                    edit_supplier(int(edit_id), new_name.strip(), new_type)
                    st.success(f"Supplier {edit_id} updated")
                    do_rerun()
        st.markdown("### 🗑 Delete Supplier")
        del_id = st.selectbox("Select Supplier ID to delete", [""] + ids, key="sup_del_select")
        if del_id != "" and st.button("Delete Selected Supplier", key="sup_del_btn"):
            delete_supplier(int(del_id))
            st.success(f"Supplier {del_id} deleted")
            do_rerun()
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", csv, file_name="suppliers.csv", mime="text/csv")
    else:
        st.info("No suppliers to display.")
# -------------------------
# Reminders Page
# -------------------------
elif page == "Reminders":
    st.title("⏰ Reminders")
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_reminders"):
            st._rerun()
    c_main, c_filters = st.columns([3,1])
    customers = get_customers()
    cust_display = [f"{c[0]} - {c[1]}" for c in customers] if customers else []
    with c_main.expander("➕ Add Reminder", expanded=True):
        with st.form("add_reminder_form"):
            if cust_display:
                sel_c = st.selectbox("Customer", cust_display, key="add_r_cust")
                sel_c_id = int(sel_c.split(" - ")[0])
            else:
                st.warning("No customers available.")
                sel_c_id = None
            r_date = st.date_input("Reminder Date", value=date.today(), key="add_r_date")
            note = st.text_area("Note", key="add_r_note")
            add_sub = st.form_submit_button("Add Reminder")
            if add_sub:
                if sel_c_id is None:
                    st.warning("No customers available")
                else:
                    new_id = add_reminder(sel_c_id, r_date.strftime("%Y-%m-%d"), note.strip())
                    st.success(f"Reminder added (ID {new_id})")
                    do_rerun()
    # Filters
    with c_filters.expander("🔍 Filters", expanded=True):
        cust_filter = st.text_input("Customer Name contains", key="rem_filter_cust")
        date_filter = st.date_input("Reminder Date", value=None, key="rem_filter_date")
        apply_filter = st.button("Apply Filters", key="rem_filter_btn")
    reminders_list = get_reminders()
    df = pd.DataFrame(reminders_list, columns=["ID","Customer_ID","Reminder_Date","Note"])
    id_to_name = {str(c[0]): c[1] for c in customers}
    if not df.empty:
        df["Customer"] = df["Customer_ID"].astype(str).map(id_to_name).fillna("⚠️ Deleted")
    else:
        df["Customer"] = pd.Series([], dtype="object")
    if apply_filter:
        if cust_filter.strip():
            df = df[df["Customer"].str.contains(cust_filter.strip(), case=False, na=False)]
        if date_filter:
            df = df[df["Reminder_Date"] == date_filter.strftime("%Y-%m-%d")]
    st.subheader("All Reminders")
    if not df.empty:
        st.dataframe(df[["ID","Customer","Reminder_Date","Note"]], use_container_width=True)
        ids = df["ID"].tolist()
        st.markdown("### ✏️ Edit Reminder")
        edit_id = st.selectbox("Select Reminder ID to edit", [""] + ids, key="rem_edit_select")
        if edit_id != "":
            sel = df[df["ID"] == int(edit_id)].iloc[0]
            with st.form(f"rem_edit_form_{edit_id}"):
                if cust_display:
                    try:
                        idx = [i for i,v in enumerate(cust_display) if v.startswith(str(sel["Customer_ID"]))][0]
                    except Exception:
                        idx = 0
                    new_cust = st.selectbox("Customer", cust_display, index=idx, key=f"rem_e_cust_{edit_id}")
                    new_cust_id = int(new_cust.split(" - ")[0])
                else:
                    new_cust_id = None
                # Handle possible NaT or None dates
                try:
                    default_date = pd.to_datetime(sel["Reminder_Date"]).date()
                except:
                    default_date = date.today()
                new_date = st.date_input("Reminder Date", value=default_date, key=f"rem_e_date_{edit_id}")
                new_note = st.text_area("Note", value=sel["Note"] or "", key=f"rem_e_note_{edit_id}")
                if st.form_submit_button("Update Reminder"):
                    if new_cust_id is None:
                        st.warning("No customers available for reminder")
                    else:
                        edit_reminder(int(edit_id), new_cust_id, new_date.strftime("%Y-%m-%d"), new_note.strip())
                        st.success(f"Reminder {edit_id} updated")
                        do_rerun()
        st.markdown("### 🗑 Delete Reminder")
        del_id = st.selectbox("Select Reminder ID to delete", [""] + ids, key="rem_del_select")
        if del_id != "" and st.button("Delete Selected Reminder", key="rem_del_btn"):
            delete_reminder(int(del_id))
            st.success(f"Reminder {del_id} deleted")
            do_rerun()
        csv = df[["ID","Customer","Reminder_Date","Note"]].to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", csv, file_name="reminders.csv", mime="text/csv")
    else:
        st.info("No reminders to display.")
# -------------------------
# Price List Page (NEW)
# -------------------------
elif page == "Price List":
    st.title("💰 Price List")
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_price_list"):
            st.rerun()
    c_main, c_filters = st.columns([3, 1])
    # Get current price list
    price_items = get_price_list()
    df = pd.DataFrame(price_items, columns=["ID", "Dent_Category", "Price_Per_Unit"])
    # Add new price item - FREE TEXT INPUT
    with c_main.expander("➕ Add Price Item", expanded=False):
        with st.form("add_price_form"):
            st.markdown("#### Enter Dent Category and Price")
            category = st.text_input("Dent Category", key="add_price_cat", placeholder="e.g., Zirconia Implant")
            price = st.number_input("Price per Unit (IRR)", min_value=0.0, step=1000.0, key="add_price_val")
            submitted = st.form_submit_button("Add Price Item")
            if submitted:
                if not category.strip():
                    st.error("❌ Dent category cannot be empty")
                else:
                    try:
                        new_id = add_price_item(category.strip(), price)
                        st.success(f"✅ Price added for '{category}' (ID {new_id})")
                        do_rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"❌ '{category}' already exists in the price list!")
    # Display price list
    st.subheader("Current Prices")
    if not df.empty:
        # Show actual database IDs
        display_df = df[["ID", "Dent_Category", "Price_Per_Unit"]].rename(columns={
            "ID": "Database ID",
            "Dent_Category": "Dent Category",
            "Price_Per_Unit": "Price (IRR)"
        })
        st.dataframe(display_df, use_container_width=True)
        # Edit section - USE DATABASE ID
        st.markdown("### ✏️ Edit Price Item")
        edit_id = st.selectbox(
            "Select item to edit", 
            options=[""] + df["ID"].tolist(),
            key="price_edit_id"
        )
        if edit_id != "":
            sel = df[df["ID"] == edit_id].iloc[0]  # ← Filter by DATABASE ID
            with st.form(f"edit_price_{edit_id}"):
                new_cat = st.text_input("Dent Category", value=sel["Dent_Category"], key=f"price_e_cat_{edit_id}")
                new_price = st.number_input("Price per Unit (IRR)", min_value=0.0, value=float(sel["Price_Per_Unit"]), step=1000.0, key=f"price_e_price_{edit_id}")
                if st.form_submit_button("Update Price"):
                    if not new_cat.strip():
                        st.error("❌ Dent category cannot be empty")
                    else:
                        try:
                            edit_price_item(edit_id, new_cat.strip(), new_price)  # ← PASS DATABASE ID
                            st.success(f"✅ Price updated for '{new_cat}'")
                            do_rerun()
                        except sqlite3.IntegrityError:
                            st.error(f"❌ Another item already uses the category '{new_cat}'!")
        # Delete section - USE DATABASE ID
        st.markdown("### 🗑️ Delete Price Item")
        del_id = st.selectbox(
            "Select item to delete", 
            options=[""] + df["ID"].tolist(),
            key="price_del_id"
        )
        if del_id != "":
            if st.button("Delete Selected Item", key="price_del_btn", use_container_width=True):
                delete_price_item(del_id)  # ← PASS DATABASE ID
                st.success("🗑️ Price item deleted")
                do_rerun()
        # Export
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export Price List", csv, file_name="price_list.csv", mime="text/csv", use_container_width=True)
    else:
        st.info("ostringstream empty. Add your first item using the form above!")
# -------------------------
# Reports Page 
# -------------------------
elif page == "Reports":
    st.title("📈 Advanced Analytics Dashboard")
    # === TIME FILTER ===
    st.sidebar.markdown("### 📅 Time Filter (Lunar Calendar)")
    # Fetch data to get year range
    orders_list = get_orders()
    if not orders_list:
        st.info("ostringstream No order data yet. Add orders to unlock insights!")
        st.stop()
    orders_temp = pd.DataFrame(orders_list, columns=[
        "ID", "Customer_ID", "Day_Arrival_Number", "Month_Arrival_Number", "Year_Arrival_Number",
        "Day_Departure_Number", "Month_Departure_Number", "Year_Departure_Number", "Doctor_Name",
        "Patient_Name", "Dent_Category", "Co_Worker_Owns", "No_Units", "Color", "Price", "Status"
    ])
    min_year = int(orders_temp["Year_Arrival_Number"].min()) if not orders_temp.empty else 1400
    max_year = int(orders_temp["Year_Arrival_Number"].max()) if not orders_temp.empty else 1403
    selected_years = st.sidebar.multiselect(
        "Select Lunar Years",
        options=list(range(min_year, max_year + 1)),
        default=[max_year] if max_year else []
    )
    all_months = list(range(1, 13))
    selected_months = st.sidebar.multiselect(
        "Select Lunar Months",
        options=all_months,
        default=all_months,
        format_func=lambda x: f"Month {x}"
    )
    # === DATA PREPARATION ===
    orders_df = orders_temp.copy()
    # Apply filters
    if selected_years:
        orders_df = orders_df[orders_df["Year_Arrival_Number"].isin(selected_years)]
    if selected_months:
        orders_df = orders_df[orders_df["Month_Arrival_Number"].isin(selected_months)]
    if orders_df.empty:
        st.warning("No orders match the selected filters.")
        st.stop()
    customers_df = pd.DataFrame(get_customers(), columns=["ID", "Name", "Phone", "Category", "Notes"])
    id_to_name = {row["ID"]: row["Name"] for _, row in customers_df.iterrows()}
    orders_df["Customer"] = orders_df["Customer_ID"].map(id_to_name).fillna("⚠️ Deleted")
    # Parse dent categories with quantities
    def parse_dent_categories(dent_str):
        items = []
        if not dent_str:
            return items
        for part in dent_str.split(","):
            part = part.strip()
            if ":" in part:
                cat, qty = part.rsplit(":", 1)
                try:
                    items.append((cat.strip(), int(qty)))
                except:
                    items.append((part, 1))
            else:
                items.append((part, 1))
        return items
    orders_df["Parsed_Dent"] = orders_df["Dent_Category"].apply(parse_dent_categories)
    # === CONTEXT BANNER ===
    year_str = f"Years: {', '.join(map(str, sorted(selected_years)))}" if selected_years else "All Years"
    month_str = f"Months: {', '.join(map(str, sorted(selected_months)))}" if len(selected_months) < 12 else "All Months"
    st.info(f"📊 Showing analytics for {year_str}, {month_str}")
    # === OVERALL METRICS (MODERN CARD LAYOUT) ===
    st.markdown("---")
    st.subheader("📊 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="background-color:#1E2A38; padding:20px; border-radius:10px; text-align:center;">
            <h3>💰 Total Revenue</h3>
            <p style="font-size:24px; font-weight:bold; color:#D4AF37;">{revenue}</p>
        </div>
        """.format(revenue=f"{orders_df['Price'].sum():,.0f} IRR"), unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background-color:#1E2A38; padding:20px; border-radius:10px; text-align:center;">
            <h3>🎯 Avg Order Value</h3>
            <p style="font-size:24px; font-weight:bold; color:#D4AF37;">{avg_price}</p>
        </div>
        """.format(avg_price=f"{orders_df['Price'].mean():,.0f} IRR"), unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background-color:#1E2A38; padding:20px; border-radius:10px; text-align:center;">
            <h3>📦 Total Orders</h3>
            <p style="font-size:24px; font-weight:bold; color:#D4AF37;">{total_orders}</p>
        </div>
        """.format(total_orders=len(orders_df)), unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="background-color:#1E2A38; padding:20px; border-radius:10px; text-align:center;">
            <h3>🔢 Total Units</h3>
            <p style="font-size:24px; font-weight:bold; color:#D4AF37;">{total_units}</p>
        </div>
        """.format(total_units=orders_df["No_Units"].sum()), unsafe_allow_html=True)
    # === SECTION 1: FINANCIAL PERFORMANCE ===
    st.markdown("---")
    st.subheader("💰 Financial Performance")
    # Revenue by Year-Month (with clean labels)
    if len(selected_years) > 1 or len(selected_months) > 1:
        orders_df["YearMonth"] = orders_df["Year_Arrival_Number"].astype(str) + "-" + orders_df["Month_Arrival_Number"].astype(str).str.zfill(2)
        orders_df["YearMonth_Label"] = orders_df["Year_Arrival_Number"].astype(str) + " - Month " + orders_df["Month_Arrival_Number"].astype(str)
        revenue_by_ym = orders_df.groupby("YearMonth").agg({
            "Price": "sum",
            "YearMonth_Label": "first"
        }).reset_index()
        import plotly.express as px
        fig = px.bar(
            revenue_by_ym,
            x="YearMonth_Label",
            y="Price",
            title="Revenue by Lunar Year-Month",
            labels={"Price": "Revenue (IRR)"},
            color_discrete_sequence=["#D4AF37"]
        )
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Lunar Year-Month",
            yaxis_title="Revenue (IRR)",
            plot_bgcolor="#152A46",
            paper_bgcolor="#152A46",
            font=dict(color="white"),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    # Top 5 Highest Value Orders
    top_orders = orders_df.nlargest(5, "Price")[["ID", "Customer", "Dent_Category", "Price"]]
    st.write("#### 🥇 Top 5 Highest-Value Orders")
    st.dataframe(top_orders, use_container_width=True)
    st.markdown("---")
    # === SECTION 2: OPERATIONAL FLOW ===
    st.subheader("📅 Operational Flow")
    # Completion Rate
    completed = orders_df["Day_Departure_Number"].notna().sum()
    completion_rate = completed / len(orders_df) * 100
    st.metric("Order Completion Rate", f"{completion_rate:.1f}%")
    # Average Units per Order
    avg_units = orders_df["No_Units"].mean()
    st.metric("Avg Units per Order", f"{avg_units:.1f}")
    st.markdown("---")
    # === SECTION 3: CUSTOMER & PARTNER DYNAMICS ===
    st.subheader("👥 Customer & Partner Insights")
    # Top 5 Customers by Revenue
    top_customers = orders_df.groupby("Customer")["Price"].sum().nlargest(5)
    if not top_customers.empty:
        customer_df = top_customers.reset_index()
        customer_df.columns = ["Customer", "Revenue"]
        fig = px.bar(
            customer_df,
            x="Customer",
            y="Revenue",
            title="Top 5 Customers by Revenue",
            labels={"Revenue": "Revenue (IRR)"},
            color_discrete_sequence=["#D4AF37"]
        )
        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Customer",
            yaxis_title="Revenue (IRR)",
            plot_bgcolor="#152A46",
            paper_bgcolor="#152A46",
            font=dict(color="white"),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    # Supplier Load
    if orders_df["Co_Worker_Owns"].notna().any() and not orders_df["Co_Worker_Owns"].eq("").all():
        supplier_load = {}
        sup_id_name_map = {str(s[0]): s[1] for s in get_suppliers()}
        for co_workers in orders_df["Co_Worker_Owns"].dropna():
            if co_workers:
                for sid in co_workers.split(","):
                    sid = sid.strip()
                    name = sup_id_name_map.get(sid, f"ID {sid}")
                    supplier_load[name] = supplier_load.get(name, 0) + 1
        if supplier_load:
            supplier_df = pd.DataFrame(list(supplier_load.items()), columns=["Supplier", "Orders Assigned"])
            fig = px.bar(
                supplier_df,
                x="Supplier",
                y="Orders Assigned",
                title="Supplier Workload (Orders Assigned)",
                color_discrete_sequence=["#D4AF37"]
            )
            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Supplier",
                yaxis_title="Orders Assigned",
                plot_bgcolor="#152A46",
                paper_bgcolor="#152A46",
                font=dict(color="white"),
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    # === SECTION 4: PRODUCT MIX & TRENDS ===
    st.subheader("🦷 Product Mix & Trends")
    # Expand dent categories
    dent_expanded = []
    for _, row in orders_df.iterrows():
        for cat, qty in row["Parsed_Dent"]:
            dent_expanded.append({
                "Category": cat,
                "Quantity": qty,
                "Revenue": row["Price"] * qty / row["No_Units"] if row["No_Units"] > 0 else 0
            })
    dent_df = pd.DataFrame(dent_expanded)
    if not dent_df.empty:
        # Top 10 Categories by Units Sold
        top_cats_qty = dent_df.groupby("Category")["Quantity"].sum().nlargest(10).reset_index()
        fig1 = px.bar(
            top_cats_qty,
            x="Category",
            y="Quantity",
            title="Top 10 Categories by Units Sold",
            color_discrete_sequence=["#D4AF37"]
        )
        fig1.update_layout(
            template="plotly_dark",
            xaxis_title="Category",
            yaxis_title="Total Units",
            plot_bgcolor="#152A46",
            paper_bgcolor="#152A46",
            font=dict(color="white"),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
        # === NEW: Revenue per Unit by Category ===
        # Calculate revenue per unit for each category
        revenue_per_unit = dent_df.groupby("Category").apply(
            lambda x: x["Revenue"].sum() / x["Quantity"].sum()
        ).reset_index(name="Revenue_Per_Unit")
        # Sort by revenue per unit (descending)
        revenue_per_unit = revenue_per_unit.sort_values("Revenue_Per_Unit", ascending=False).head(10)
        fig2 = px.bar(
            revenue_per_unit,
            x="Category",
            y="Revenue_Per_Unit",
            title="Top 10 Categories by Revenue per Unit",
            color_discrete_sequence=["#D4AF37"],
            labels={"Revenue_Per_Unit": "Revenue per Unit (IRR)"}
        )
        fig2.update_layout(
            template="plotly_dark",
            xaxis_title="Category",
            yaxis_title="Revenue per Unit (IRR)",
            plot_bgcolor="#152A46",
            paper_bgcolor="#152A46",
            font=dict(color="white"),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
        # === BONUS: Profitability Matrix (Optional) ===
        st.markdown("### 💡 Profitability Matrix")
        st.write("Categories with high units AND high revenue per unit are your **star performers**.")
        # Create a scatter plot: Units vs Revenue per Unit
        scatter_data = dent_df.groupby("Category").agg({
            "Quantity": "sum",
            "Revenue": "sum"
        }).reset_index()
        scatter_data["Revenue_Per_Unit"] = scatter_data["Revenue"] / scatter_data["Quantity"]
        fig3 = px.scatter(
            scatter_data,
            x="Quantity",
            y="Revenue_Per_Unit",
            size="Revenue",
            color="Category",
            title="Product Profitability Matrix",
            labels={
                "Quantity": "Total Units Sold",
                "Revenue_Per_Unit": "Revenue per Unit (IRR)",
                "Revenue": "Total Revenue"
            },
            hover_data=["Category", "Quantity", "Revenue_Per_Unit", "Revenue"]
        )
        fig3.update_layout(
            template="plotly_dark",
            plot_bgcolor="#152A46",
            paper_bgcolor="#152A46",
            font=dict(color="white"),
            height=400
        )
        st.plotly_chart(fig3, use_container_width=True)
    # Color Preferences
    if "Color" in orders_df.columns and orders_df["Color"].notna().any():
        color_counts = orders_df["Color"].value_counts().head(10).reset_index()
        color_counts.columns = ["Color", "Count"]
        fig = px.pie(
            color_counts,
            names="Color",
            values="Count",
            title="Most Popular Colors",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="#152A46",
            paper_bgcolor="#152A46",
            font=dict(color="white"),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    # === ACTIONABLE INSIGHTS ===
    st.markdown("---")
    st.subheader("💡 Key Business Insights")
    insights = []
    if not orders_df.empty:
        avg_order = orders_df['Price'].mean()
        high_value_threshold = avg_order * 1.5
        high_value_orders = len(orders_df[orders_df['Price'] > high_value_threshold])
        if high_value_orders > 0:
            insights.append(f"🔥 **{high_value_orders} high-value orders** (>{high_value_threshold:,.0f} IRR) represent key revenue opportunities.")
        if completion_rate < 90:
            insights.append(f"⚠️ **Completion rate is {completion_rate:.1f}%** — investigate bottlenecks in order fulfillment.")
        if not orders_df.empty:
            top_customer_rev = top_customers.iloc[0] if not top_customers.empty else 0
            total_rev = orders_df['Price'].sum()
            if top_customer_rev / total_rev > 0.2:
                top_customer_name = top_customers.index[0]
                insights.append(f"🎯 **Top customer '{top_customer_name}' drives {(top_customer_rev/total_rev)*100:.1f}% of revenue** — consider loyalty program.")
        if not dent_df.empty:
            top_category = dent_df.groupby("Category")["Quantity"].sum().idxmax()
            insights.append(f"🦷 **'{top_category}' is your bestseller** — ensure sufficient inventory and technician capacity.")
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.info("✅ All metrics look healthy! Continue monitoring for trends.")