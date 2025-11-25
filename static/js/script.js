function agregarCarrito(productoId) {
    fetch("/ajax/agregar_carrito", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            producto_id: productoId,
            cantidad: 1
        })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert("Producto agregado al carrito");
        } else {
            alert("Error al agregar el producto");
        }
    })
    .catch(err => console.error("Error AJAX:", err));
}
