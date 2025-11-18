// Agregar producto al carrito
function agregarAlCarrito(productoId) {
    console.log('Agregando producto ID:', productoId);
    
    fetch('/ajax/agregar_carrito', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            producto_id: productoId,
            cantidad: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ ' + data.message);
            actualizarContadorCarrito();
        } else {
            alert('❌ Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Error al agregar al carrito');
    });
}

// Actualizar contador del carrito
function actualizarContadorCarrito() {
    fetch('/ajax/obtener_carrito')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const cartCount = document.getElementById('cart-count');
                if (cartCount) {
                    cartCount.textContent = data.total_items;
                }
            }
        })
        .catch(error => {
            console.error('Error al obtener carrito:', error);
        });
}

// Cargar carrito completo
function cargarCarrito() {
    fetch('/ajax/obtener_carrito')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('carrito-items');
            if (!container) return;
            
            if (!data.success || data.carrito.length === 0) {
                container.innerHTML = '<p>Tu carrito está vacío</p>';
                if (document.getElementById('total')) {
                    document.getElementById('total').textContent = '0.00';
                }
                if (document.getElementById('cart-count')) {
                    document.getElementById('cart-count').textContent = '0';
                }
                return;
            }
            
            let html = '';
            data.carrito.forEach(item => {
                const subtotal = item.precio * item.cantidad;
                html += `
                    <div class="carrito-item">
                        <div class="item-info">
                            <h4>${item.nombre}</h4>
                            <p>Precio: $${item.precio.toFixed(2)}</p>
                            <p>Cantidad: ${item.cantidad}</p>
                            <p>Subtotal: $${subtotal.toFixed(2)}</p>
                        </div>
                        <div class="item-controls">
                            <button class="btn-eliminar" onclick="eliminarDelCarrito(${item.id})">
                                Eliminar
                            </button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
            
            if (document.getElementById('total')) {
                document.getElementById('total').textContent = data.total.toFixed(2);
            }
            if (document.getElementById('cart-count')) {
                document.getElementById('cart-count').textContent = data.total_items;
            }
        })
        .catch(error => {
            console.error('Error al cargar carrito:', error);
            const container = document.getElementById('carrito-items');
            if (container) {
                container.innerHTML = '<p>Error al cargar el carrito</p>';
            }
        });
}

// Eliminar del carrito
function eliminarDelCarrito(productoId) {
    if (!confirm('¿Estás seguro de eliminar este producto del carrito?')) {
        return;
    }

    fetch('/ajax/eliminar_carrito', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ producto_id: productoId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cargarCarrito();
            actualizarContadorCarrito();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al eliminar del carrito');
    });
}

// Cargar contador al inicio de cada página
document.addEventListener('DOMContentLoaded', function() {
    actualizarContadorCarrito();
});