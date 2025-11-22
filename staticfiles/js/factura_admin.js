function updatePrecioUnitario(selectElement) {
    // Función para actualizar el precio unitario al seleccionar un producto
    const productId = selectElement.value;
    if (!productId) return;
    
    // Obtener la fila actual del formulario
    const row = selectElement.closest('tr');
    const precioInput = row.querySelector('input[name$="-precio_unitario"]');
    
    // Hacer una solicitud AJAX para obtener el precio del producto
    fetch(`/api/productos/${productId}/precio/`)
        .then(response => response.json())
        .then(data => {
            precioInput.value = data.precio;
        })
        .catch(error => console.error('Error al obtener el precio:', error));
}

// Inicializar después de cargar la página
document.addEventListener('DOMContentLoaded', function() {
    // Añadir manejador para cambiar estado de IVA
    const conIvaCheckbox = document.querySelector('#id_con_iva');
    const porcentajeIvaInput = document.querySelector('#id_porcentaje_iva');
    
    if (conIvaCheckbox && porcentajeIvaInput) {
        conIvaCheckbox.addEventListener('change', function() {
            porcentajeIvaInput.disabled = !this.checked;
            if (!this.checked) {
                porcentajeIvaInput.setAttribute('data-old-value', porcentajeIvaInput.value);
                porcentajeIvaInput.value = '0.00';
            } else {
                const oldValue = porcentajeIvaInput.getAttribute('data-old-value') || '19.00';
                porcentajeIvaInput.value = oldValue;
            }
        });
        
        // Inicializar estado
        porcentajeIvaInput.disabled = !conIvaCheckbox.checked;
    }
});