import sqlite3

#Inserta un articulo a Producto para hacer pruebas
def agregar_prueba():
    conexion = sqlite3.connect('monitor_precios.db')
    cursor = conexion.cursor()

    # Datos del producto
    nombre = "Cargador de Pilas Duracell"
    url = "https://www.mercadolibre.com.mx/cargador-pilas-recargables-duracell-cef-7-aa-aaa-c-4-aa-baterias/p/MLM28200091#polycard_client=search-desktop&search_layout=grid&position=5&type=product&tracking_id=2bfa2cc1-f036-48f9-bcc2-8cafe96982d6&wid=MLM2319150661&sid=search"
    precio_objetivo = 500.0
    tienda = "mercadolibre"

    try:
        cursor.execute("""
            INSERT INTO Producto (nombre, url, precio_objetivo, tienda, activo)
            VALUES (?, ?, ?, ?, 1)        
        """, (nombre, url, precio_objetivo, tienda))

        conexion.commit()
        print(f"Producto '{nombre}' agregado exitosamente.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    agregar_prueba()