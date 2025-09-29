from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Ruta principal
@app.route("/")
def index():
    return render_template("index.html")

# Panel de administración
@app.route("/admin")
def admin_dashboard():
    return render_template("admin/dashboard.html")

# Agregar producto
@app.route("/admin/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form['nombre']
        precio = request.form['precio']
        try:
            conn = sqlite3.connect("restaurante.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO menu (producto, precio) VALUES (?, ?)", (nombre, precio))
            conn.commit()
            conn.close()
            flash(f"Producto '{nombre}' agregado correctamente", "success")
            return redirect(url_for("menu"))
        except sqlite3.IntegrityError:
            flash(f"Error: El producto '{nombre}' ya existe", "error")
            return redirect(url_for("agregar"))
    return render_template("admin/agregar.html")

# Eliminar producto
@app.route("/admin/eliminar", methods=["GET", "POST"])
def eliminar():
    conn = sqlite3.connect("restaurante.db")
    cursor = conn.cursor()
    
    if request.method == "POST":
        producto_id = request.form.get("producto_id")
        cursor.execute("DELETE FROM menu WHERE id = ?", (producto_id,))
        conn.commit()
        flash("Producto eliminado correctamente", "success")
        return redirect(url_for("eliminar"))

    cursor.execute("SELECT * FROM menu")
    productos = cursor.fetchall()
    conn.close()
    return render_template("admin/eliminar.html", productos=productos)
@app.route("/admin/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    try:
        conn = sqlite3.connect("restaurante.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        print(f"Producto con ID {id} eliminado correctamente.")
    except Exception as e:
        print("Error al eliminar producto:", e)
    
    return redirect(url_for('eliminar'))  # Regresamos a la lista de productos

# Menú público
@app.route("/menu")
def menu():
    conn = sqlite3.connect("restaurante.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    productos = cursor.fetchall()
    conn.close()
    return render_template("menu.html", productos=productos)
# Editar producto
@app.route("/admin/editar", methods=["GET", "POST"])
def editar():
    conn = sqlite3.connect("restaurante.db")
    cursor = conn.cursor()

    if request.method == "POST":
        producto_id = request.form.get("producto_id")
        nuevo_nombre = request.form.get("nombre")
        nuevo_precio = request.form.get("precio")

        cursor.execute("UPDATE menu SET producto = ?, precio = ? WHERE id = ?", 
                       (nuevo_nombre, nuevo_precio, producto_id))
        conn.commit()
        conn.close()
        flash("Producto actualizado correctamente", "success")
        return redirect(url_for("editar"))

    # Para mostrar todos los productos disponibles para editar
    cursor.execute("SELECT * FROM menu")
    productos = cursor.fetchall()
    conn.close()

    return render_template("admin/editar.html", productos=productos)



if __name__ == "__main__":
    app.run(debug=True)