from flask import Flask, render_template, request, jsonify, session
import pyodbc
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'clave_secreta_musica_2024'

# ========== CONFIGURACIÓN SQL SERVER ==========
DB_CONFIG = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost',
    'database': 'tienda_musica',
    'username': 'sa',
    'password': '123'
}

def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# ========== RUTAS PRINCIPALES ==========
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/productos')
def productos():
    try:
        conn = get_db_connection()
        if conn is None:
            return "Error: No se pudo conectar a la base de datos"
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, precio, imagen FROM productos")
        
        raw_productos = cursor.fetchall()
        conn.close()

        productos = []
        for row in raw_productos:
            producto_id, nombre, precio_decimal, imagen = row
            precio_float = float(precio_decimal) if isinstance(precio_decimal, Decimal) else precio_decimal
            productos.append((producto_id, nombre, precio_float, imagen))
        
        return render_template('productos.html', productos=productos)
    except Exception as e:
        return f"Error al cargar productos: {str(e)}", 500

# ========== API PARA EL CARRITO ==========
@app.route('/ajax/agregar_carrito', methods=['POST'])
def agregar_carrito():
    try:
        data = request.get_json()
        producto_id = int(data.get('producto_id'))
        cantidad = int(data.get('cantidad', 1))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, precio, imagen FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        conn.close()
        
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
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
            precio = float(producto[2])
            carrito.append({
                'id': producto[0], 
                'nombre': producto[1], 
                'precio': precio, 
                'cantidad': cantidad,
                'imagen': producto[3]
            })
        
        session['carrito'] = carrito
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Producto agregado al carrito',
            'total_items': sum(item['cantidad'] for item in carrito)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error interno'}), 500

@app.route('/ajax/obtener_carrito', methods=['GET'])
def obtener_carrito():
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito) 
    return jsonify({
        'success': True,
        'carrito': carrito,
        'total': total,
        'total_items': sum(item['cantidad'] for item in carrito)
    })

@app.route('/ajax/eliminar_carrito', methods=['POST'])
def eliminar_carrito():
    try:
        data = request.get_json()
        producto_id = int(data.get('producto_id'))
        
        if 'carrito' in session:
            session['carrito'] = [item for item in session['carrito'] if item['id'] != producto_id]
            session.modified = True
            return jsonify({'success': True, 'message': 'Producto eliminado'})
        return jsonify({'success': False, 'message': 'Carrito vacío'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/resenas')
def resenas():
    return render_template('resenas.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/carrito')
def ver_carrito():
    return render_template('carrito.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)