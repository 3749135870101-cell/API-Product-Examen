import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Productos API", layout="wide")
st.title("Catálogo de Productos")

API_URL = "http://localhost:3000/api"

# Menú lateral con cuatro opciones distintas
opcion = st.sidebar.radio(
    "Acción",
    ["Ver productos", "Crear producto", "Editar producto", "Eliminar producto"]
)

# Función para obtener productos (con límite máximo de 50)
def obtener_productos():
    try:
        params = {"page": 1, "limit": 50}  # Límite máximo permitido por la API
        response = requests.get(f"{API_URL}/products", params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data["data"]["data"]
            else:
                st.error(f"Error de API: {data.get('error')}")
        else:
            st.error(f"Error HTTP {response.status_code}")
            st.write("Detalle:", response.text)
    except requests.exceptions.ConnectionError:
        st.error("No se pudo conectar con la API. ¿El servidor está corriendo?")
    except Exception as e:
        st.error(f"Error inesperado: {e}")
    return []

# -------------------------------------------------------------------
# Opción 1: Ver productos
# -------------------------------------------------------------------
if opcion == "Ver productos":
    st.header("Lista de productos")

    col1, col2, col3 = st.columns(3)
    with col1:
        page = st.number_input("Página", min_value=1, value=1, step=1)
    with col2:
        limit = st.number_input("Productos por página", min_value=1, max_value=50, value=10, step=1)
    with col3:
        q = st.text_input("Buscar por nombre", placeholder="ej. mouse")

    params = {"page": page, "limit": limit}
    if q:
        params["q"] = q

    with st.spinner("Cargando productos..."):
        response = requests.get(f"{API_URL}/products", params=params)

    if response.status_code == 200:
        data = response.json()
        if data["ok"]:
            productos = data["data"]["data"]
            meta = data["data"]["meta"]

            st.info(f"Total: {meta['total']} productos | Página {meta['page']} de {meta['totalPages']}")

            if productos:
                df = pd.DataFrame(productos)
                df_mostrar = df[["id", "name", "price", "stock"]].copy()
                df_mostrar.columns = ["ID", "Nombre", "Precio", "Stock"]
                st.dataframe(df_mostrar, use_container_width=True)

                st.subheader("Detalle del producto")
                ids_disponibles = df["id"].tolist()
                prod_id = st.selectbox("Selecciona un ID para ver detalles", ids_disponibles)

                if prod_id:
                    producto = df[df["id"] == prod_id].iloc[0].to_dict()
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        st.markdown("**ID**")
                        st.write(producto["id"])
                    with col_b:
                        st.markdown("**Nombre**")
                        st.write(producto["name"])
                    with col_c:
                        st.markdown("**Precio**")
                        st.write(f"${producto['price']}")
                    with col_d:
                        st.markdown("**Stock**")
                        st.write(producto["stock"])

                    st.markdown("**Descripción**")
                    st.write(producto.get("description", "Sin descripción"))

                    st.markdown("**Fechas**")
                    st.write(f"Creado: {producto['created_at'][:10]} {producto['created_at'][11:19]}")
                    st.write(f"Actualizado: {producto['updated_at'][:10]} {producto['updated_at'][11:19]}")
            else:
                st.info("No hay productos que coincidan con la búsqueda.")
        else:
            st.error("La API respondió con error.")
    else:
        st.error(f"Error al conectar con la API: {response.status_code}")

# -------------------------------------------------------------------
# Opción 2: Crear producto
# -------------------------------------------------------------------
elif opcion == "Crear producto":
    st.header("Crear nuevo producto")

    with st.form("form_crear"):
        nombre = st.text_input("Nombre del producto", max_chars=100)
        descripcion = st.text_area("Descripción", max_chars=500)
        precio = st.number_input("Precio", min_value=0.01, step=0.01, format="%.2f")
        stock = st.number_input("Stock", min_value=0, step=1)

        submitted = st.form_submit_button("Crear producto")

        if submitted:
            if not nombre:
                st.error("El nombre es obligatorio.")
            else:
                payload = {
                    "name": nombre,
                    "description": descripcion,
                    "price": precio,
                    "stock": stock
                }
                with st.spinner("Enviando..."):
                    response = requests.post(f"{API_URL}/products", json=payload)

                if response.status_code == 201:
                    st.success("Producto creado correctamente")
                    st.json(response.json())
                else:
                    st.error(f"Error {response.status_code}: no se pudo crear el producto.")

# -------------------------------------------------------------------
# Opción 3: Editar producto
# -------------------------------------------------------------------
elif opcion == "Editar producto":
    st.header("Editar producto")
    productos = obtener_productos()
    if not productos:
        st.warning("No hay productos disponibles para editar.")
    else:
        opciones = {p["id"]: f"{p['id']} - {p['name']}" for p in productos}
        prod_id = st.selectbox(
            "Selecciona un producto para editar",
            options=list(opciones.keys()),
            format_func=lambda x: opciones[x]
        )

        if prod_id:
            producto = next(p for p in productos if p["id"] == prod_id)
            with st.form("form_editar"):
                nombre = st.text_input("Nombre", value=producto["name"])
                descripcion = st.text_area("Descripción", value=producto.get("description", ""))
                precio = st.number_input(
                    "Precio",
                    min_value=0.01,
                    step=0.01,
                    format="%.2f",
                    value=float(producto["price"])
                )
                stock = st.number_input("Stock", min_value=0, step=1, value=producto["stock"])
                submitted = st.form_submit_button("Actualizar producto")

                if submitted:
                    payload = {
                        "name": nombre,
                        "description": descripcion,
                        "price": precio,
                        "stock": stock
                    }
                    with st.spinner("Actualizando..."):
                        response = requests.put(f"{API_URL}/products/{prod_id}", json=payload)

                    if response.status_code == 200:
                        st.success("Producto actualizado correctamente")
                        st.json(response.json())
                    else:
                        error_msg = response.json().get("error", {}).get("message", "Error desconocido")
                        st.error(f"Error {response.status_code}: {error_msg}")

# -------------------------------------------------------------------
# Opción 4: Eliminar producto
# -------------------------------------------------------------------
elif opcion == "Eliminar producto":
    st.header("Eliminar producto")
    productos = obtener_productos()
    if not productos:
        st.warning("No hay productos disponibles para eliminar.")
    else:
        opciones = {p["id"]: f"{p['id']} - {p['name']}" for p in productos}
        prod_id = st.selectbox(
            "Selecciona un producto para eliminar",
            options=list(opciones.keys()),
            format_func=lambda x: opciones[x]
        )

        if prod_id:
            producto = next(p for p in productos if p["id"] == prod_id)
            st.warning(f"¿Estás seguro de que deseas eliminar el producto **{producto['name']}** (ID: {prod_id})?")
            if st.button("Eliminar producto", type="primary"):
                with st.spinner("Eliminando..."):
                    response = requests.delete(f"{API_URL}/products/{prod_id}")

                if response.status_code == 200:
                    st.success("Producto eliminado correctamente")
                else:
                    error_msg = response.json().get("error", {}).get("message", "Error desconocido")
                    st.error(f"Error {response.status_code}: {error_msg}")