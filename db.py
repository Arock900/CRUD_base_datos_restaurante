import sqlite3
import json

# ===========================
# CONEXIÓN A LA BASE DE DATOS
# ===========================
def get_connection():
    return sqlite3.connect('restaurante.db')


# ===========================
# CREAR TABLAS
# ===========================
def crear_tablas():
    conexion = get_connection()
    cursor = conexion.cursor()

    # Crear tabla menu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT NOT NULL UNIQUE,
        precio REAL NOT NULL
    );
    """)

    # Crear tabla pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        total REAL NOT NULL,
        FOREIGN KEY (producto_id) REFERENCES menu (id)
    );
    """)

    conexion.commit()
    conexion.close()
    print("Tablas creadas correctamente.")


# ===========================
# INSERTAR DATOS DEL JSON
# ===========================
def insertar_menu():
    """Lee datos.json y carga los productos en la tabla 'menu' usando INSERT OR IGNORE."""
    conexion = get_connection()
    cursor = conexion.cursor()

    # 1) Leer datos.json
    with open("datos.json", "r", encoding="utf-8") as f:
        datos = json.load(f)

    menu = datos.get("menu", {})  # {"pizza": 5000, "hamburguesa": 8000}

    # 2) Insertar cada producto en la tabla 'menu'
    for producto, precio in menu.items():
        nombre = producto.strip().lower()  # normalizamos el nombre
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO menu (producto, precio) VALUES (?, ?)",
                (nombre, float(precio))
            )
        except Exception as e:
            print(f"Error insertando {producto}: {e}")

    conexion.commit()

    # 3) Mostrar resultado
    cursor.execute("SELECT COUNT(*) FROM menu")
    total = cursor.fetchone()[0]
    conexion.close()
    print(f"Menú importado. Total de productos en la tabla 'menu': {total}")


# ===========================
# OBTENER TODOS LOS PRODUCTOS
# ===========================
def obtener_menu():
    """Obtiene todos los productos del menú desde la base de datos"""
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, producto, precio FROM menu ORDER BY id")
    menu = cursor.fetchall()

    conexion.close()
    return menu


# ===========================
# AGREGAR PRODUCTO
# ===========================
def agregar_producto(producto, precio):
    """Inserta un nuevo producto en el menú"""
    conexion = get_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO menu (producto, precio) VALUES (?, ?)",
            (producto.lower().strip(), float(precio))
        )
        conexion.commit()
        print(f"Producto '{producto}' agregado con éxito.")
    except Exception as e:
        print("Error al agregar producto:", e)
    finally:
        conexion.close()


# ===========================
# OBTENER PRODUCTO POR ID
# ===========================
def obtener_producto_por_id(id):
    """Devuelve un producto específico por su ID"""
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM menu WHERE id = ?", (id,))
    producto = cursor.fetchone()
    conexion.close()
    return producto


# ===========================
# ACTUALIZAR PRODUCTO
# ===========================
def actualizar_producto(id, nuevo_producto, nuevo_precio):
    """Actualiza nombre y precio de un producto existente"""
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE menu
        SET producto = ?, precio = ?
        WHERE id = ?
    """, (nuevo_producto.lower().strip(), float(nuevo_precio), id))
    conexion.commit()
    conexion.close()
    print(f"Producto con ID {id} actualizado correctamente.")


# ===========================
# ELIMINAR PRODUCTO
# ===========================
def eliminar_producto_db(id):
    """Elimina un producto por su ID"""
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM menu WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    print(f"Producto con ID {id} eliminado correctamente.")


# ===========================
# PEDIDOS - AGREGAR PEDIDO
# ===========================
def insertar_pedido(nombre_producto, cantidad):
    """Inserta un pedido basado en un producto existente del menú"""
    conexion = get_connection()
    cursor = conexion.cursor()

    # Buscar producto
    cursor.execute("SELECT id, precio FROM menu WHERE producto = ?", (nombre_producto.lower().strip(),))
    resultado = cursor.fetchone()

    if resultado is None:
        print(f"Error: El producto '{nombre_producto}' no existe en el menú.")
        conexion.close()
        return

    producto_id, precio = resultado
    total = precio * cantidad

    cursor.execute(
        "INSERT INTO pedidos (producto_id, cantidad, total) VALUES (?, ?, ?)",
        (producto_id, cantidad, total)
    )

    conexion.commit()
    conexion.close()
    print(f"Pedido insertado: {nombre_producto} x{cantidad} = ${total}")


# ===========================
# VER PEDIDOS
# ===========================
def ver_pedidos():
    """Muestra todos los pedidos con el nombre del producto"""
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT p.id, m.producto, p.cantidad, p.total
    FROM pedidos p
    JOIN menu m ON p.producto_id = m.id
    """)
    
    pedidos = cursor.fetchall()
    conexion.close()

    if not pedidos:
        print("No hay pedidos registrados.")
        return

    print("\n--- Lista de pedidos ---")
    for pedido in pedidos:
        id_pedido, producto, cantidad, total = pedido
        print(f"ID: {id_pedido} | {producto} x{cantidad} = ${total}")


# ===========================
# ELIMINAR PEDIDO
# ===========================
def eliminar_pedido_por_id(pedido_id):
    """Elimina un pedido por su ID"""
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
    if cursor.rowcount == 0:
        print(f"No se encontró pedido con ID {pedido_id}.")
    else:
        conexion.commit()
        print(f"Pedido con ID {pedido_id} eliminado correctamente.")
    conexion.close()


# ===========================
# DEBUG - MOSTRAR TABLAS
# ===========================
def debug_ver_tablas():
    """Muestra el contenido de las tablas MENU y PEDIDOS"""
    conexion = get_connection()
    cursor = conexion.cursor()

    print("\n--- Tabla MENU ---")
    cursor.execute("SELECT * FROM menu")
    for fila in cursor.fetchall():
        print(fila)

    print("\n--- Tabla PEDIDOS ---")
    cursor.execute("SELECT * FROM pedidos")
    for fila in cursor.fetchall():
        print(fila)

    conexion.close()


# ===========================
# PRUEBAS DIRECTAS
# ===========================
if __name__ == "__main__":
    crear_tablas()
    insertar_menu()
    debug_ver_tablas()
