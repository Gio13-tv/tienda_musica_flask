import mysql.connector

class MySQLDAO:
    def __init__(self, config):
        self.conn = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )

    # USUARIOS
    def get_user_by_email(self, email):
        cur = self.conn.cursor()
        cur.execute("SELECT id, nombre, email, password_hash, rol FROM usuarios WHERE email=%s", (email,))
        return cur.fetchone()

    def get_user_by_id(self, user_id):
        cur = self.conn.cursor()
        cur.execute("SELECT id, nombre, email, password_hash, rol FROM usuarios WHERE id=%s", (user_id,))
        return cur.fetchone()

    def create_user(self, nombre, email, password_hash, rol):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, %s)",
            (nombre, email, password_hash, rol)
        )
        self.conn.commit()

    # PRODUCTOS
    def get_all_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, nombre, precio, imagen FROM productos")
        return cur.fetchall()

    def get_product_by_id(self, pid):
        cur = self.conn.cursor()
        cur.execute("SELECT id, nombre, precio, imagen FROM productos WHERE id=%s", (pid,))
        return cur.fetchone()


    def create_product(self, nombre, precio, imagen):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO productos (nombre, precio, imagen) VALUES (%s, %s, %s)",
            (nombre, precio, imagen)
        )
        self.conn.commit()

    def update_product(self, pid, nombre, precio, imagen):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE productos SET nombre=%s, precio=%s, imagen=%s WHERE id=%s",
            (nombre, precio, imagen, pid)
        )
        self.conn.commit()

    def delete_product(self, pid):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM productos WHERE id=%s", (pid,))
        self.conn.commit()

    # ÓRDENES
    def create_order(self, user_id, total):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO ordenes (usuario_id, total) VALUES (%s, %s)",
            (user_id, total)
        )
        self.conn.commit()
        return cur.lastrowid

    def add_order_detail(self, orden_id, producto_id, cantidad, precio_unitario):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO orden_detalle (orden_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            (orden_id, producto_id, cantidad, precio_unitario)
        )
        self.conn.commit()

    def get_all_orders(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, usuario_id, fecha, total FROM ordenes")
        return cur.fetchall()

    def get_order_details(self, oid):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT producto_id, cantidad, precio_unitario FROM orden_detalle WHERE orden_id=%s",
            (oid,)
        )
        return cur.fetchall()
