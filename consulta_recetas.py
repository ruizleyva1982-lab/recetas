import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Consulta de Recetas", layout="wide")

# Cargar datos usando ruta relativa (compatible con la nube)
@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), "recetas.xlsx")
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()
    st.title("📋 Consulta de Recetas de Producción")

    # Crear columna combinada
    df["display_name"] = df["CÓDIGO RECETA"].astype(str) + " - " + df["PRODUCTO"]

    # Lista de opciones con primera opción vacía
    opciones = [""] + df["display_name"].tolist()

    # Inicializar session_state para el selectbox
    if "producto_select" not in st.session_state:
        st.session_state.producto_select = ""

    # Sidebar
    st.sidebar.header("Filtros de Búsqueda")
    seleccion = st.sidebar.selectbox(
        "🔎 Selecciona o busca un producto",
        opciones,
        index=opciones.index(st.session_state.producto_select),
        key="producto_select"
    )

    if st.sidebar.button("🧹 Limpiar selección"):
        st.session_state.producto_select = ""
        st.rerun()  # Reemplaza st.experimental_rerun() que ya está deprecado

    # Número de cantidad
    rendimiento_deseado = st.sidebar.number_input(
        "⚖️ Cantidad a producir",
        min_value=0.01,
        step=1.0,
        value=1.0
    )

    # Botón calcular
    if st.sidebar.button("🧮 Calcular Insumos"):
        if seleccion == "":
            st.info("🧹 No hay producto seleccionado. Elige un producto para calcular.")
        else:
            codigo_id = seleccion.split(" - ")[0]
            receta = df[df["CÓDIGO RECETA"] == codigo_id].copy()

            if receta.empty:
                st.error("❌ Producto no encontrado")
            else:
                rendimiento_base = receta["RENDIMIENTO"].iloc[0]
                unidad_medida_receta = receta["UMR"].iloc[0]
                nombre_producto = receta["PRODUCTO"].iloc[0]

                receta["CANTIDAD A USAR"] = (
                    rendimiento_deseado / rendimiento_base
                ) * receta["CANTIDAD"]

                st.info(
                    f"**Producto:** {nombre_producto} | "
                    f"**Rendimiento Base:** {rendimiento_base} {unidad_medida_receta}"
                )

                st.subheader(f"🧂 Insumos para producir {rendimiento_deseado} {unidad_medida_receta}")

                resultado = receta[["INSUMO", "CANTIDAD A USAR", "UMI"]].rename(columns={
                    "INSUMO": "Nombre del Insumo",
                    "CANTIDAD A USAR": "Cantidad Requerida",
                    "UMI": "Unidad"
                })

                st.table(resultado)

except FileNotFoundError:
    st.error("❌ No se encontró el archivo recetas.xlsx. Asegúrate de que está en la misma carpeta que la app.")

except Exception as e:
    st.error(f"Ocurrió un error: {e}")
