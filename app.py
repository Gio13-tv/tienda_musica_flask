from flask import Flask, render_template, request, jsonify, session
import pyodbc

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
    """Conecta a SQL Server"""
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
        productos = cursor.fetchall()
        conn.close()
        
        print(f"Productos encontrados: {len(productos)}")
        return render_template('productos.html', productos=productos)
    except Exception as e:
        return f"Error al cargar productos: {str(e)}"

@app.route('/resenas')
def resenas():
    return render_template('resenas.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/carrito')
def ver_carrito():
    return render_template('carrito.html')

# ========== API PARA EL CARRITO ==========
@app.route('/ajax/agregar_carrito', methods=['POST'])
def agregar_carrito():
    try:
        data = request.get_json()
        producto_id = int(data.get('producto_id'))
        cantidad = int(data.get('cantidad', 1))
        
        # Obtener producto de la BD
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, precio, imagen FROM productos WHERE id = ?", (producto_id,))
        producto = cursor.fetchone()
        conn.close()
        
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'}), 404
        
        # Inicializar carrito en sesión
        if 'carrito' not in session:
            session['carrito'] = []
        
        carrito = session['carrito']
        encontrado = False
        
        # Buscar si el producto ya está en el carrito
        for item in carrito:
            if item['id'] == producto_id:
                item['cantidad'] += cantidad
                encontrado = True
                break
        
        # Si no está, agregarlo
        if not encontrado:
            carrito.append({
                'id': producto[0],  # id
                'nombre': producto[1],  # nombre
                'precio': float(producto[2]),  # precio
                'cantidad': cantidad,
                'imagen': producto[3]  # imagen
            })
        
        session['carrito'] = carrito
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': 'Producto agregado al carrito',
            'total_items': sum(item['cantidad'] for item in carrito)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
            return jsonify({'success': True, 'message': 'Producto eliminado del carrito'})
        return jsonify({'success': False, 'message': 'Carrito vacío'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)