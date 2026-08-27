"""The Manual-mode screens: the insert forms, the list views, the joined
sales_detail view, and the CSV loader.

Every screen reads and writes through api_client, so nothing here knows the
database exists.
"""

from __future__ import annotations

from decimal import Decimal

import requests
import streamlit as st

import api_client
import components


def view_overview() -> None:
    components.section_header("Overview", "At a glance", "Live counts, read straight from the database.")

    try:
        customers = api_client.get("/customers").json()
        products = api_client.get("/products").json()
        sales = api_client.get("/sales/detail").json()
    except requests.RequestException:
        st.error(f"Can't reach the API at {api_client.API_BASE_URL}. Is it running?")
        return

    revenue = sum((Decimal(row["line_total"]) for row in sales), Decimal("0.00"))

    cols = st.columns(4)
    components.stat_card(cols[0], "Customers", str(len(customers)))
    components.stat_card(cols[1], "Products", str(len(products)))
    components.stat_card(cols[2], "Sales recorded", str(len(sales)))
    components.stat_card(cols[3], "Total revenue", f"${revenue:,.2f}")

    st.markdown("#### Most recent sales")
    recent = sorted(sales, key=lambda r: r["sold_at"], reverse=True)[:8]
    components.render_table(recent, "No sales recorded yet — try Record sale or CSV load.")


def view_add_customer() -> None:
    components.section_header("Add", "New customer", "Insert-only — nothing here can later be edited or removed.")
    with st.container(border=True):
        with st.form("customer_form", clear_on_submit=True, border=False):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full name", placeholder="Ava Mendez")
                city = st.text_input("City (optional)", placeholder="Austin")
            with col2:
                email = st.text_input("Email", placeholder="ava.mendez@example.com")
                country_code = st.text_input("Country code", placeholder="US", max_chars=2)
            submitted = st.form_submit_button("Add customer", type="primary")
        if submitted:
            response = api_client.post(
                "/customers",
                json={
                    "full_name": full_name,
                    "email": email,
                    "city": city or None,
                    "country_code": country_code.upper(),
                },
            )
            if response.status_code == 201:
                st.success(f"Added {email}.")
            else:
                st.error(api_client.error_detail(response))


def view_add_product() -> None:
    components.section_header("Add", "New product", "Insert-only — the current list price only, never a historic one.")
    with st.container(border=True):
        with st.form("product_form", clear_on_submit=True, border=False):
            col1, col2 = st.columns(2)
            with col1:
                sku = st.text_input("SKU", placeholder="KB-ERGO-01")
                category = st.text_input("Category", placeholder="Peripherals")
            with col2:
                name = st.text_input("Name", placeholder="Ergonomic Split Keyboard")
                unit_price = st.text_input("Unit price", placeholder="189.00")
            is_active = st.checkbox("Active", value=True)
            submitted = st.form_submit_button("Add product", type="primary")
        if submitted:
            response = api_client.post(
                "/products",
                json={
                    "sku": sku,
                    "name": name,
                    "category": category,
                    "unit_price": api_client.money(unit_price),
                    "is_active": is_active,
                },
            )
            if response.status_code == 201:
                st.success(f"Added {sku}.")
            else:
                st.error(api_client.error_detail(response))


def view_record_sale() -> None:
    components.section_header(
        "Add", "Record a sale",
        "The price and time are frozen exactly as entered — a later product-price change never rewrites this row.",
    )
    with st.container(border=True):
        with st.form("sale_form", clear_on_submit=True, border=False):
            col1, col2 = st.columns(2)
            with col1:
                customer_email = st.text_input("Customer email", placeholder="ava.mendez@example.com")
                quantity = st.number_input("Quantity", min_value=1, step=1)
            with col2:
                sku = st.text_input("Product SKU", placeholder="KB-ERGO-01")
                unit_price = st.text_input("Unit price at time of sale", placeholder="189.00")
            sold_at = st.text_input("Sold at (ISO timestamp)", placeholder="2026-01-05T10:15:00Z")
            st.caption("A sale with no timestamp is refused, never defaulted to the current time.")
            submitted = st.form_submit_button("Record sale", type="primary")
        if submitted:
            response = api_client.post(
                "/sales",
                json={
                    "customer_email": customer_email,
                    "sku": sku,
                    "quantity": int(quantity),
                    "unit_price": api_client.money(unit_price),
                    "sold_at": sold_at,
                },
            )
            if response.status_code == 201:
                st.success("Sale recorded.")
            else:
                st.error(api_client.error_detail(response))


def _list_view(title: str, help_text: str, path: str, empty_message: str) -> None:
    components.section_header("Browse", title, help_text)
    if st.button("↻ Refresh", key=f"refresh_{path}", type="secondary"):
        st.rerun()
    try:
        rows = api_client.get(path).json()
    except requests.RequestException:
        st.error(f"Can't reach the API at {api_client.API_BASE_URL}. Is it running?")
        return
    components.render_table(rows, empty_message)


def view_customers() -> None:
    _list_view("Customers", "Ordered by email.", "/customers", "No customers yet.")


def view_products() -> None:
    _list_view("Products", "Ordered by SKU.", "/products", "No products yet.")


def view_sales() -> None:
    _list_view("Sales", "Ordered by sale time.", "/sales", "No sales recorded yet.")


def view_sales_detail() -> None:
    _list_view(
        "Sales detail",
        "Customer, product, and sale, joined — ordered by sale time, then customer, then SKU.",
        "/sales/detail",
        "No sales recorded yet.",
    )


def view_csv_load() -> None:
    components.section_header(
        "Import", "Load sales from CSV",
        "Columns: customer_email, sku, quantity, unit_price, sold_at. Accepted and rejected rows are reported separately.",
    )
    with st.container(border=True):
        uploaded = st.file_uploader("CSV file", type="csv", label_visibility="collapsed")
        load = st.button("Load file", type="primary", disabled=uploaded is None)

    if uploaded is not None and load:
        response = api_client.post(
            "/sales/batch",
            files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
        )
        if response.status_code == 200:
            result = response.json()
            accepted, rejected = result["accepted"], result["rejected"]
            cols = st.columns(3)
            components.stat_card(cols[0], "Accepted", str(len(accepted)))
            components.stat_card(cols[1], "Rejected", str(len(rejected)))
            components.stat_card(cols[2], "Summed line total", f"${Decimal(result['summed_line_total']):,.2f}")
            st.markdown("#### Accepted")
            components.render_table(accepted, "Nothing accepted from this file.")
            st.markdown("#### Rejected")
            components.render_table(rejected, "Nothing rejected — every row was accepted.")
        else:
            st.error(api_client.error_detail(response))


VIEWS = {
    "overview": view_overview,
    "add_customer": view_add_customer,
    "add_product": view_add_product,
    "record_sale": view_record_sale,
    "customers": view_customers,
    "products": view_products,
    "sales": view_sales,
    "sales_detail": view_sales_detail,
    "csv_load": view_csv_load,
}
