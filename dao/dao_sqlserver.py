import pyodbc

class SQLServerDAO:
    def __init__(self, config):
        conn_str = (
            f"DRIVER={config['driver']};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
        )
        self.conn = pyodbc.connect(conn_str)

    
# USUARIOS
    def get_user_by_email(self, email: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nombre, email, password_hash, rol FROM usuarios WHERE email = ?",
            (email,)
        )
        return cursor.fetchone()

    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nombre, email, password_hash, rol FROM usuarios WHERE id = ?",
            (user_id,)
        )
        return cursor.fetchone()

    def create_user(self, nombre, email, password_hash, rol):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password_hash, rol)
            VALUES (?, ?, ?, ?)
        """, (nombre, email, password_hash, rol))
        self.conn.commit()
        return True

    # PRODUCTOS
    def get_all_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nombre, precio, imagen FROM productos")
        return cursor.fetchall()

    def get_product_by_id(self, producto_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, nombre, precio, imagen FROM productos WHERE id = ?",
            (producto_id,)
        )
        return cursor.fetchone()

    def create_product(self, nombre, precio, imagen):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, precio, imagen)
            VALUES (?, ?, ?)
        """, (nombre, precio, imagen))
        self.conn.commit()

    def update_product(self, producto_id, nombre, precio, imagen):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre = ?, precio = ?, imagen = ?
            WHERE id = ?
        """, (nombre, precio, imagen, producto_id))
        self.conn.commit()

    def delete_product(self, producto_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
        self.conn.commit()

    # ORDENES
    def create_order(self, usuario_id, total):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ordenes (usuario_id, total)
            OUTPUT INSERTED.id
            VALUES (?, ?)
        """, (usuario_id, total))

        orden_id = cursor.fetchone()[0]
        self.conn.commit()
        return orden_id

    def add_order_detail(self, orden_id, producto_id, cantidad, precio_unitario):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO orden_detalle (orden_id, producto_id, cantidad, precio_unitario)
            VALUES (?, ?, ?, ?)
        """, (orden_id, producto_id, cantidad, precio_unitario))
        self.conn.commit()

    def get_all_orders(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT o.id, u.nombre, o.fecha, o.total
            FROM ordenes o
            JOIN usuarios u ON u.id = o.usuario_id
            ORDER BY o.id DESC
        """)
        return cursor.fetchall()

    def get_order_details(self, orden_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.nombre, d.cantidad, d.precio_unitario
            FROM orden_detalle d
            JOIN productos p ON p.id = d.producto_id
            WHERE d.orden_id = ?
        """, (orden_id,))
        return cursor.fetchall()
