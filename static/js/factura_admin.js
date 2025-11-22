// ==================== ACTUALIZAR PRECIO UNITARIO ====================
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

// ==================== MOSTRAR BARRA DE PROGRESO CON STOCK ====================
document.addEventListener('DOMContentLoaded', function() {
    // Manejador para cambiar estado de IVA
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

    // ==================== BARRA DE PROGRESO DE STOCK ====================
    const productSelects = document.querySelectorAll('select[name*="producto"]');
    
    productSelects.forEach((select, index) => {
        // Crear contenedor para la barra de progreso
        const container = document.createElement('div');
        container.id = `stock-progress-${index}`;
        container.style.marginTop = '8px';
        container.style.padding = '8px';
        container.style.backgroundColor = '#f9fafb';
        container.style.borderRadius = '6px';
        container.style.display = 'none';
        
        const label = document.createElement('small');
        label.style.display = 'block';
        label.style.marginBottom = '5px';
        label.style.fontWeight = 'bold';
        label.style.color = '#333';
        
        const progressBar = document.createElement('div');
        progressBar.style.width = '100%';
        progressBar.style.height = '24px';
        progressBar.style.backgroundColor = '#e0e0e0';
        progressBar.style.borderRadius = '4px';
        progressBar.style.overflow = 'hidden';
        progressBar.style.border = '1px solid #ccc';
        
        const progressFill = document.createElement('div');
        progressFill.style.height = '100%';
        progressFill.style.backgroundColor = '#4CAF50';
        progressFill.style.width = '0%';
        progressFill.style.transition = 'width 0.3s ease';
        progressFill.style.display = 'flex';
        progressFill.style.alignItems = 'center';
        progressFill.style.justifyContent = 'center';
        progressFill.style.color = 'white';
        progressFill.style.fontSize = '12px';
        progressFill.style.fontWeight = 'bold';
        progressFill.style.textShadow = '0 1px 2px rgba(0,0,0,0.3)';
        
        progressBar.appendChild(progressFill);
        container.appendChild(label);
        container.appendChild(progressBar);
        select.parentNode.insertBefore(container, select.nextSibling);
        
        // Event listener para cambios en el select
        select.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const stockText = selectedOption.text.match(/\(Stock:\s*(\d+)\)/);
            
            if (stockText && stockText[1]) {
                const stock = parseInt(stockText[1]);
                const maxStock = 100;
                const percentage = Math.min((stock / maxStock) * 100, 100);
                
                // Cambiar color según stock
                let color = '#4CAF50'; // Verde
                if (stock < 10) color = '#f44336'; // Rojo
                else if (stock < 30) color = '#ff9800'; // Naranja
                
                progressFill.style.backgroundColor = color;
                progressFill.style.width = percentage + '%';
                progressFill.textContent = stock + ' unidades disponibles';
                label.textContent = 'Stock disponible:';
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        });
    });
});