import streamlit as st
import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime
from fpdf import FPDF
import os

# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(page_title="Panadería Boletas", layout="wide")
st.title("🛒 Punto de Venta Panadería")

# Cargar productos
products = pd.read_csv("products.csv")

# Inicializar carrito en la sesión
if "cart" not in st.session_state:
    st.session_state.cart = []

# =========================
# FUNCIÓN PARA GENERAR BOLETA PDF
# =========================
def generar_boleta_pdf(items, total):
    now = datetime.now().strftime("%d/%m/%Y %I:%M %p")

    base_height = 60
    item_height = 6
    num_items = len(items)
    final_height = base_height + (num_items * item_height)

    pdf = FPDF(orientation='P', unit='mm', format=(58, final_height))
    pdf.add_page()

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, "EUROPAN", ln=True, align='C')
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 4, "DIRECCION: CALLE ALEMANIA #842", ln=True, align='C')
    pdf.cell(0, 4, "VILLA EUROPA", ln=True, align='C')
    pdf.cell(0, 4, "COMUNA: RENGO", ln=True, align='C')
    pdf.ln(2)

    pdf.cell(0, 4, now, ln=True, align='C')
    pdf.ln(4)

    pdf.cell(30, 4, "TURNO #: 11", ln=False)
    pdf.cell(0, 4, "FOLIO: 7", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "B", 8)
    pdf.cell(8, 4, "CANT.", border=0)
    pdf.cell(30, 4, "DESCRIPCION", border=0)
    pdf.cell(0, 4, "IMPORTE", border=0, ln=True)
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 0, "-"*32, ln=True)
    pdf.ln(2)

    total_items = 0
    for product_name, quantity in items.items():
        price_per_unit = products.loc[products['name'] == product_name, 'price'].values[0]
        subtotal = price_per_unit * quantity
        pdf.cell(8, 4, str(quantity), border=0)
        pdf.cell(30, 4, product_name[:14], border=0)
        pdf.cell(0, 4, f"${subtotal}", border=0, ln=True)
        total_items += quantity

    pdf.ln(2)
    pdf.cell(0, 4, f"NO. DE ARTICULOS: {total_items}", ln=True)
    pdf.ln(2)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, f"TOTAL: ${total}", ln=True, align='R')

    pdf.ln(5)
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 4, "Gracias por su compra", ln=True, align='C')

    pdf.output("boleta.pdf")

# =========================
# FUNCIÓN PARA IMPRIMIR AUTOMÁTICO
# =========================
def imprimir_boleta(nombre_archivo):
    try:
        # Enviar archivo a impresión automática
        os.startfile(nombre_archivo, "print")
    except Exception as e:
        st.error(f"❌ Error al imprimir automáticamente: {e}")

# =========================
# SECCIÓN PRODUCTOS
# =========================
st.subheader("Selecciona productos:")

cols = st.columns(3)

for idx, product in products.iterrows():
    with cols[idx % 3]:
        image_path = Path(f"images/{product['name']}.jpg")
        
        if image_path.exists():
            st.image(str(image_path), width=200)
        
        st.markdown(f"### {product['name']}")
        st.markdown(f"**${product['price']}**")

        if st.button("Agregar", key=f"add_{product['id']}"):
            st.session_state.cart.append(product)

st.divider()

# =========================
# SECCIÓN CARRITO
# =========================
st.subheader("🧾 Detalle de Boleta:")

if st.session_state.cart:
    cart_items = [item['name'] for item in st.session_state.cart]
    grouped_items = Counter(cart_items)

    total = 0
    for product_name, quantity in grouped_items.items():
        price_per_unit = products.loc[products['name'] == product_name, 'price'].values[0]
        subtotal = price_per_unit * quantity
        st.write(f"{product_name} x{quantity} - ${subtotal}")
        total += subtotal

    st.markdown(f"## **Total: ${total}**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🖨️ Emitir Boleta"):
            generar_boleta_pdf(grouped_items, total)
            imprimir_boleta("boleta.pdf")
            st.success("✅ Boleta enviada directamente a impresión")
            st.session_state.cart = []
    with col2:
        if st.button("❌ Cancelar Venta"):
            st.session_state.cart = []
else:
    st.info("No hay productos en el carrito.")
