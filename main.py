import sqlite3
from src.scraper import obtener_precio
from src.notificador import enviar_alerta
from datetime import datetime

#Configuracion
DB_PATH = 'monitor_precios.db'
CORREO_DESTINO = "guill3rmovalencia@gmail.com"

def obtener_productos_activos() -> list[tuple]:
    """
    Toma de la base de datos los articulos para monitorear.

    Args:
        DB_PATH (str): Cadena con el archivo .db
    Return:
        list[tuple]: Lista de tuplas
    """
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        #Toma las tuplas de la tabla Producto que tengan 1 en activo
        cursor.execute("SELECT id_producto, nombre, url, precio_objetivo FROM Producto WHERE activo = 1")
        return cursor.fetchall()

def guardar_historial(id_producto: int, precio: float, disponible: int) -> None:
    """
    Funcion que se conecta a la base de datos e inserta una tupla del registro en la tabla Historial_Precio

    Args:
        id_producto (int): id del producto a registrar
        precio (float): precio con el que se registra
        disponible (int): 0 si no esta disponible, 1 de lo contrario
    """
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO Historial_Precio (id_producto, precio_registrado, disponible)
            VALUES (?, ?, ?)
            """, (id_producto, precio, disponible)
        )
        conexion.commit()

def ejecutar_monitor():
    """
    Funcion que revisa los precios de los articulos activos en la base de datos y manda mensajes si ha bajado
    """
    print(f"Iniciando revision de precios: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Lista de tuplas con los productos activos
    productos = obtener_productos_activos()

    if not productos:
        print("No hay productos activos")
        return
    
    # Itera sobre la lista
    for producto in productos:
        # Define los atributos como variables
        id_prod, nombre, url, precio_objetivo = producto
        print(f"\nRevisando: {nombre}...")

        # Llama al scraper para obtener el precio
        precio_actual = obtener_precio(url)

        if precio_actual:
            print(f"Precio encontrado: {precio_actual}")
            guardar_historial(id_prod, precio_actual, 1)

            # Activacion de alertas
            if precio_actual <= precio_objetivo:
                print(f"SE DETECTO BAJADA DE PRECIO")
                print(f"El producto {nombre} bajó a {precio_actual}, se esperaba {precio_objetivo}")
                enviar_alerta(
                    CORREO_DESTINO,
                    nombre,
                    precio_actual,
                    url
                )
            else: print(f"Sigue estando por encima del precio deseado ({precio_objetivo})")
        
        #Si es None
        else:
            print("No se pudo obtener el precio. Se marcará como no disponible")
            guardar_historial(id_prod, 0.0, 0)

if __name__ == "__main__":
    ejecutar_monitor()