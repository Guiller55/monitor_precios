import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from src.scraper import obtener_precio, detectar_tienda
from src.notificador import enviar_alerta
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Monitor de Precios", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS personalizados
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

# Título y descripción
st.title("📊 Monitor de Precios")
st.markdown("Rastrea precios en Mercado Libre y Amazon automáticamente")

# Sidebar para navegación
with st.sidebar:
    st.header("🧭 Navegación")
    opcion = st.radio("Selecciona una opción:", 
                      ["Dashboard", "Agregar Producto", "Historial", "Configuración"])

DB_PATH = 'monitor_precios.db'

# ============= DASHBOARD =============
if opcion == "Dashboard":
    st.subheader("Estado actual de productos")
    
    try:
        # Cargar productos activos
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id_producto, nombre, url, precio_objetivo, tienda FROM Producto WHERE activo = 1")
            productos = cursor.fetchall()
        
        if not productos:
            st.warning("⚠️ No hay productos activos. Agrega uno en la sección 'Agregar Producto'")
        else:
            st.markdown(f"**Total de productos activos:** {len(productos)}")
            
            # Crear grid de productos
            cols = st.columns(min(3, len(productos)))
            
            for idx, producto in enumerate(productos):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"### {producto['nombre']}")
                        st.caption(f"🏪 {producto['tienda'].upper()}")
                        
                        col_precio, col_btn = st.columns([2, 1])
                        
                        with col_precio:
                            st.metric("Precio objetivo", f"${producto['precio_objetivo']:.2f}")
                        
                        # Botón para actualizar precio
                        with col_btn:
                            if st.button("🔄", key=f"btn_{producto['id_producto']}", help="Actualizar precio"):
                                with st.spinner("Obteniendo precio..."):
                                    precio = obtener_precio(producto['url'])
                                    
                                    if precio:
                                        # Guardar en historial
                                        with sqlite3.connect(DB_PATH) as conn:
                                            cursor = conn.cursor()
                                            cursor.execute(
                                                "INSERT INTO Historial_Precio (id_producto, precio_registrado, disponible) VALUES (?, ?, 1)",
                                                (producto['id_producto'], precio)
                                            )
                                            conn.commit()
                                        
                                        st.success(f"✅ ${precio:.2f}")
                                        
                                        if precio <= producto['precio_objetivo']:
                                            st.balloons()
                                            st.info("🎉 ¡Precio objetivo alcanzado!")
                                    else:
                                        st.error("❌ No disponible")
    
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")

# ============= AGREGAR PRODUCTO =============
elif opcion == "Agregar Producto":
    st.subheader("➕ Agregar nuevo producto")
    
    with st.form("form_producto", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del producto", placeholder="Ej: Laptop Gamer")
        
        with col2:
            tienda = st.selectbox("Tienda", ["mercadolibre", "amazon"])
        
        url = st.text_input("URL del producto", placeholder="https://...")
        precio_objetivo = st.number_input("Precio objetivo ($)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("✅ Agregar producto", use_container_width=True):
            if not nombre or not url or precio_objetivo <= 0:
                st.error("❌ Completa todos los campos correctamente")
            else:
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO Producto (nombre, url, precio_objetivo, tienda, activo) VALUES (?, ?, ?, ?, 1)",
                            (nombre, url, precio_objetivo, tienda)
                        )
                        conn.commit()
                    st.success(f"✅ Producto '{nombre}' agregado exitosamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ============= HISTORIAL =============
elif opcion == "Historial":
    st.subheader("📈 Historial de precios")
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Selector de producto
            df_productos = pd.read_sql_query(
                "SELECT id_producto, nombre FROM Producto WHERE activo = 1 ORDER BY nombre",
                conn
            )
            
            if df_productos.empty:
                st.warning("⚠️ No hay productos activos")
            else:
                producto_seleccionado = st.selectbox(
                    "Selecciona un producto:",
                    df_productos['nombre'].tolist()
                )
                
                id_prod = df_productos[df_productos['nombre'] == producto_seleccionado]['id_producto'].values[0]
                
                # Gráfico de historial
                df_historial = pd.read_sql_query(
                    f"""SELECT precio_registrado, fecha_hora 
                       FROM Historial_Precio 
                       WHERE id_producto = {id_prod} 
                       ORDER BY fecha_hora DESC""",
                    conn
                )
                
                if not df_historial.empty:
                    col_chart, col_stats = st.columns([3, 1])
                    
                    with col_chart:
                        df_historial_sorted = df_historial.sort_values('fecha_hora')
                        df_historial_sorted['fecha_hora'] = pd.to_datetime(df_historial_sorted['fecha_hora'])
                        st.line_chart(data=df_historial_sorted.set_index('fecha_hora')['precio_registrado'], use_container_width=True)
                    
                    with col_stats:
                        st.metric("Precio mín.", f"${df_historial['precio_registrado'].min():.2f}")
                        st.metric("Precio máx.", f"${df_historial['precio_registrado'].max():.2f}")
                        st.metric("Precio promedio", f"${df_historial['precio_registrado'].mean():.2f}")
                    
                    st.markdown("### Registro detallado")
                    df_display = df_historial.rename(columns={'precio_registrado': 'Precio', 'fecha_hora': 'Fecha/Hora'})
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("📊 Sin historial aún. Actualiza el precio para ver datos")
    
    except Exception as e:
        st.error(f"Error al cargar historial: {e}")

# ============= CONFIGURACIÓN =============
elif opcion == "Configuración":
    st.subheader("⚙️ Configuración")
    
    tab1, tab2 = st.tabs(["Administración de productos", "Información del sistema"])
    
    with tab1:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                df_todos = pd.read_sql_query(
                    "SELECT id_producto, nombre, activo, precio_objetivo FROM Producto ORDER BY nombre",
                    conn
                )
            
            if df_todos.empty:
                st.info("ℹ️ No hay productos registrados")
            else:
                for _, producto in df_todos.iterrows():
                    col_nombre, col_precio, col_estado, col_acciones = st.columns([2, 1.5, 1, 1.5])
                    
                    with col_nombre:
                        st.write(f"**{producto['nombre']}**")
                    
                    with col_precio:
                        st.caption(f"Objetivo: ${producto['precio_objetivo']:.2f}")
                    
                    with col_estado:
                        nuevo_estado = st.toggle(
                            "Activo",
                            value=bool(producto['activo']),
                            key=f"toggle_{producto['id_producto']}",
                            label_visibility="collapsed"
                        )
                        
                        if nuevo_estado != bool(producto['activo']):
                            with sqlite3.connect(DB_PATH) as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE Producto SET activo = ? WHERE id_producto = ?",
                                    (int(nuevo_estado), producto['id_producto'])
                                )
                                conn.commit()
                            st.success("✅ Actualizado")
                            st.rerun()
                    
                    with col_acciones:
                        if st.button("🗑️ Eliminar", key=f"delete_{producto['id_producto']}", use_container_width=True):
                            with sqlite3.connect(DB_PATH) as conn:
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM Producto WHERE id_producto = ?", (producto['id_producto'],))
                                conn.commit()
                            st.success("✅ Producto eliminado")
                            st.rerun()
        
        except Exception as e:
            st.error(f"Error: {e}")
    
    with tab2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fecha/Hora actual", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        with col2:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM Producto")
                    total_productos = cursor.fetchone()[0]
                st.metric("Total de productos", total_productos)
            except:
                st.metric("Total de productos", "Error")
        
        with col3:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM Historial_Precio")
                    total_registros = cursor.fetchone()[0]
                st.metric("Registros en historial", total_registros)
            except:
                st.metric("Registros en historial", "Error")
        
        st.divider()
        
        st.markdown("### Variables de entorno")
        email_usuario = os.getenv("EMAIL_USUARIO")
        st.caption(f"✉️ Email: {'Configurado ✅' if email_usuario else 'No configurado ❌'}")
        
        st.info("💡 Asegúrate de tener un archivo `.env` con las credenciales de email para las notificaciones")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center;">
        <p>Monitor de Precios © 2026 - @cdagmora, @guiller55</p>
        <small>Rastrea tus productos favoritos automáticamente</small>
    </div>
""", unsafe_allow_html=True)
