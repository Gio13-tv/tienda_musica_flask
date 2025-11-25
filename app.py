import os
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from decimal import Decimal

from config import STORAGE_ENGINE, SQLSERVER_CONFIG, MYSQL_CONFIG
from dao.dao_sqlserver import SQLServerDAO
from dao.dao_mysql import MySQLDAO

app = Flask(__name__)
app.secret_key = "clave_secreta_musica_2024"

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# DAO DINÁMICO
if STORAGE_ENGINE == "sqlserver":
    dao = SQLServerDAO(SQLSERVER_CONFIG)
else:
    dao = MySQLDAO(MYSQL_CONFIG)

# HELPERS
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    row = dao.get_user_by_id(uid)
    if not row:
        return None
    return {
        "id": row[0],
        "nombre": row[1],
        "email": row[2],
        "rol": row[4]
    }


def login_required(role=None):
    from functools import wraps
    def deco(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            user = current_user()
            if not user:
                return redirect(url_for("login"))
            if role and user["rol"] != role:
                return "No autorizado", 403
            return fn(*args, **kwargs)
        return inner
    return deco

# RUTAS PÚBLICAS
@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/productos")
def productos():
    raw = dao.get_all_products()
    productos = [(p[0], p[1], float(p[2]), p[3]) for p in raw]
    return render_template("productos.html", productos=productos)


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/contacto")
def contacto():
    return render_template("contacto.html")


@app.route("/resenas")
def resenas():
    return render_template("resenas.html")

# LOGIN / REGISTRO
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        row = dao.get_user_by_email(email)

        if not row or not check_password_hash(row[3], password):
            flash("Usuario o contraseña incorrectos", "error")
            return render_template("login.html")

        session["user_id"] = row[0]
        session["user_role"] = row[4]

        return redirect(url_for("admin_dashboard" if row[4] == "admin" else "inicio"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        rol = "cliente"

        dao.create_user(nombre, email, password, rol)
        flash("Cuenta creada exitosamente", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# CARRITO

@app.route('/ajax/agregar_carrito', methods=['POST'])
def agregar_carrito():
    data = request.get_json()
    producto_id = int(data.get('producto_id'))
    cantidad = int(data.get('cantidad', 1))

    producto = dao.get_product_by_id(producto_id)
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado'})

    if 'carrito' not in session:
        session['carrito'] = []

    carrito = session['carrito']
    encontrado = False

    for item in carrito:
        if item['id'] == producto_id:
            item['cantidad'] += cantidad
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            'id': producto[0],
            'nombre': producto[1],
            'precio': float(producto[2]),
            'cantidad': cantidad,
            'imagen': producto[3]
        })

    session['carrito'] = carrito
    session.modified = True

    total_items = sum(item['cantidad'] for item in carrito)

    return jsonify({
        'success': True,
        'message': 'Producto agregado correctamente',
        'total_items': total_items
    })


@app.route("/ajax/obtener_carrito", methods=["GET"])
def obtener_carrito():
    carrito = session.get("carrito", [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    total_items = sum(item['cantidad'] for item in carrito)

    return jsonify({
        "success": True,
        "carrito": carrito,
        "total": total,
        "total_items": total_items
    })


@app.route("/ajax/eliminar_carrito", methods=["POST"])
def eliminar_carrito():
    data = request.get_json()
    pid = int(data["producto_id"])

    carrito = session.get("carrito", [])
    carrito = [item for item in carrito if item["id"] != pid]

    session["carrito"] = carrito
    session.modified = True

    return jsonify({"success": True})

# REALIZAR COMPRA
@app.route("/comprar", methods=["POST"])
@login_required()
def comprar():
    user = current_user()
    carrito = session.get("carrito", [])

    if not carrito:
        flash("Tu carrito está vacío", "error")
        return redirect(url_for("ver_carrito"))

    total = sum(i["precio"] * i["cantidad"] for i in carrito)
    orden_id = dao.create_order(user["id"], total)

    for i in carrito:
        dao.add_order_detail(orden_id, i["id"], i["cantidad"], i["precio"])

    session["carrito"] = []
    session.modified = True

    return render_template("compra_confirmada.html", orden_id=orden_id)

# VISTA DEL CARRITO
@app.route("/carrito")
def ver_carrito():
    return render_template("carrito.html")

# ADMIN
@app.route("/admin")
@login_required(role="admin")
def admin_dashboard():
    return render_template("admin_dashboard.html", user=current_user())


@app.route("/admin/ordenes")
@login_required(role="admin")
def admin_ordenes():
    return render_template("admin_ordenes.html", ordenes=dao.get_all_orders())


@app.route("/admin/ordenes/<int:orden_id>")
@login_required(role="admin")
def admin_orden_detalle(orden_id):
    detalles = dao.get_order_details(orden_id)
    return render_template("admin_orden_detalle.html",
                           detalles=detalles, orden_id=orden_id)

# CRUD PRODUCTOS
@app.route("/admin/productos")
@login_required(role="admin")
def admin_productos():
    raw = dao.get_all_products()
    productos = [(p[0], p[1], float(p[2]), p[3]) for p in raw]
    return render_template("admin_productos.html", productos=productos)


@app.route("/admin/productos/nuevo", methods=["GET", "POST"])
@login_required(role="admin")
def admin_producto_nuevo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])

        archivo = request.files.get("imagen_archivo")
        filename = None

        if archivo and archivo.filename != "":
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(UPLOAD_FOLDER, filename))

        dao.create_product(nombre, precio, filename)
        return redirect(url_for("admin_productos"))

    return render_template("admin_producto_form.html", modo="nuevo")


@app.route("/admin/productos/<int:producto_id>/editar", methods=["GET", "POST"])
@login_required(role="admin")
def admin_producto_editar(producto_id):
    p = dao.get_product_by_id(producto_id)

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])

        archivo = request.files.get("imagen_archivo")
        imagen = p[3]

        if archivo and archivo.filename != "":
            imagen = secure_filename(archivo.filename)
            archivo.save(os.path.join(UPLOAD_FOLDER, imagen))

        dao.update_product(producto_id, nombre, precio, imagen)
        return redirect(url_for("admin_productos"))

    producto = {
        "id": p[0],
        "nombre": p[1],
        "precio": float(p[2]),
        "imagen": p[3]
    }
    return render_template("admin_producto_form.html",
                           modo="editar", producto=producto)


@app.route("/admin/productos/<int:producto_id>/eliminar", methods=["POST"])
@login_required(role="admin")
def admin_producto_eliminar(producto_id):
    dao.delete_product(producto_id)
    return redirect(url_for("admin_productos"))

# RUN
if __name__ == "__main__":
    app.run(debug=True, port=5000)
