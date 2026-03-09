import sqlite3

#Inicializa la base de datos si se ejecuta solo

def inicializar_bd():
    conexion = sqlite3.connect('monitor_precios.db')
    cursor = conexion.cursor()

    #Habilitar soporte para llaves foraneas en SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Crear tabla Producto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Producto (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            url TEXT NOT NULL,
            precio_objetivo REAL NOT NULL,
            tienda TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
    ''')

    # Crear tabla Historial_Precio
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Historial_Precio (
            id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            precio_registrado REAL NOT NULL,
            disponible INTEGER DEFAULT 1,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_producto) REFERENCES Producto (id_producto) ON DELETE CASCADE        
        )
    ''')

    # Guardar y cerrar conexion
    conexion.commit()
    conexion.close()
    print("Base de datos y tablas creadas con exito")

if __name__ == "__main__":
    inicializar_bd()