from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from django.http import HttpResponse
from datetime import datetime
from .models import Cotizacion, DetalleCotizacion
from inventario.models import Producto
from .forms import CotizacionForm, DetalleCotizacionFormSet

class CotizacionListView(LoginRequiredMixin, ListView):
    model = Cotizacion
    template_name = 'cotizaciones/lista_cotizaciones.html'
    context_object_name = 'cotizaciones'
    paginate_by = 10
    
    def get_queryset(self):
        # Si es admin, ver todas; si es cliente, solo las propias
        if self.request.user.es_admin:
            return Cotizacion.objects.all()
        return Cotizacion.objects.filter(cliente=self.request.user)

class CotizacionDetailView(LoginRequiredMixin, DetailView):
    model = Cotizacion
    template_name = 'cotizaciones/detalle_cotizacion.html'
    context_object_name = 'cotizacion'
    
    def get_object(self):
        obj = super().get_object()
        # Verificar que el usuario puede ver esta cotización
        if not self.request.user.es_admin and obj.cliente != self.request.user:
            raise HttpResponseForbidden("No tienes permiso para ver esta cotización.")
        return obj

@login_required
def nueva_cotizacion(request):
    """Vista para crear una nueva cotización"""
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        formset = DetalleCotizacionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # Guardar la cotización
            cotizacion = form.save(commit=False)
            cotizacion.cliente = request.user
            cotizacion.save()
            
            # Guardar los detalles
            for form_detalle in formset:
                if form_detalle.cleaned_data and not form_detalle.cleaned_data.get('DELETE', False):
                    detalle = form_detalle.save(commit=False)
                    detalle.cotizacion = cotizacion
                    detalle.save()
            
            messages.success(request, "Tu cotización ha sido enviada con éxito. Pronto nos pondremos en contacto contigo.")
            return redirect('cotizaciones:lista_cotizaciones')
    else:
        # Si se viene del catálogo con un producto específico
        producto_id = request.GET.get('producto_id')
        
        form = CotizacionForm()
        formset = DetalleCotizacionFormSet()
        
        if producto_id:
            # Pre-cargar el producto en el formulario
            try:
                producto = Producto.objects.get(id=producto_id)
                initial = [{'producto': producto, 'cantidad': 1}]
                formset = DetalleCotizacionFormSet(initial=initial)
            except Producto.DoesNotExist:
                pass
    
    return render(request, 'cotizaciones/crear_cotizacion.html', {
        'form': form,
        'formset': formset
    })

@login_required
def responder_cotizacion(request, pk):
    """Vista para que los administradores respondan a una cotización"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    
    if not request.user.es_admin:
        return HttpResponseForbidden("No tienes permiso para responder cotizaciones.")
        
    if request.method == 'POST':
        # Procesar la respuesta
        estado = request.POST.get('estado')
        notas_admin = request.POST.get('notas_admin')
        
        # Actualizar precios individuales
        for item in cotizacion.items.all():
            precio_str = request.POST.get(f'precio_{item.id}')
            if precio_str:
                try:
                    precio = float(precio_str)
                    item.precio_unitario = precio
                    item.save()
                except ValueError:
                    pass
        
        # Actualizar la cotización
        cotizacion.estado = estado
        cotizacion.notas_admin = notas_admin
        cotizacion.fecha_respuesta = timezone.now()
        cotizacion.save()
        
        messages.success(request, "La cotización ha sido actualizada correctamente.")
        return redirect('cotizaciones:detalle_cotizacion', pk=cotizacion.pk)
        
    return render(request, 'cotizaciones/responder_cotizacion.html', {
        'cotizacion': cotizacion
    })

@login_required
def nueva_cotizacion_desde_carrito(request):
    """Crear una cotización a partir del carrito actual"""
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.warning(request, 'Tu carrito de cotización está vacío')
        return redirect('catalogo:lista_productos')
    
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        
        if form.is_valid():
            # Guardar la cotización
            cotizacion = form.save(commit=False)
            cotizacion.cliente = request.user
            cotizacion.save()
            
            # Transferir productos del carrito a la cotización
            for producto_id, cantidad in carrito.items():
                try:
                    producto = Producto.objects.get(id=producto_id)
                    DetalleCotizacion.objects.create(
                        cotizacion=cotizacion,
                        producto=producto,
                        cantidad=cantidad,
                    )
                except Producto.DoesNotExist:
                    continue
            
            # Vaciar el carrito
            request.session['carrito'] = {}
            
            messages.success(request, "Tu cotización ha sido enviada con éxito. Pronto nos pondremos en contacto contigo.")
            return redirect('cotizaciones:lista_cotizaciones')
    else:
        form = CotizacionForm()
    
    # Obtener productos del carrito para mostrarlos
    items = []
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            items.append({
                'producto': producto,
                'cantidad': cantidad,
		'precio_unitario': producto.precio,
                'subtotal': producto.precio * cantidad
            })
        except Producto.DoesNotExist:
            continue
    
    return render(request, 'cotizaciones/crear_desde_carrito.html', {
        'form': form,
        'items': items,
        'total': sum(item['subtotal'] for item in items)
    })
@login_required
def descargar_cotizacion_pdf(request, pk):
    """Descargar cotización en PDF"""
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    
    # Verificar permisos
    if not request.user.es_admin and cotizacion.cliente != request.user:
        return HttpResponseForbidden("No tienes permiso para descargar esta cotización.")
    
    # Crear la respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Cotizacion_{pk}_{datetime.now().strftime("%d-%m-%Y")}.pdf"'
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=10,
        alignment=1  # Centro
    )
    elements.append(Paragraph(f"<b>COTIZACIÓN #{cotizacion.id}</b>", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información General
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )
    
    elements.append(Paragraph(f"<b>Cliente:</b> {cotizacion.cliente.get_full_name() or cotizacion.cliente.username}", info_style))
    elements.append(Paragraph(f"<b>Email:</b> {cotizacion.cliente.email}", info_style))
    elements.append(Paragraph(f"<b>Fecha de Solicitud:</b> {cotizacion.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}", info_style))
    elements.append(Paragraph(f"<b>Estado:</b> {cotizacion.get_estado_display()}", info_style))
    elements.append(Paragraph(f"<b>Vigencia:</b> {cotizacion.vigencia} días", info_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Tabla de productos
    data = [
        ['Producto', 'Cantidad', 'Precio Unitario', 'Precio Cotizado', 'Subtotal']
    ]

    for item in cotizacion.items.all():
        precio_unitario = item.precio_unitario if item.precio_unitario else 0
        subtotal = (precio_unitario * item.cantidad) if precio_unitario else 0

        data.append([
            item.producto.nombre,
            str(item.cantidad),
            f"${precio_unitario:,.2f}" if precio_unitario else "---",
            f"${precio_unitario:,.2f}" if precio_unitario else "---",
            f"${subtotal:,.2f}" if subtotal else "---"
        ])
    
    table = Table(data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.2*inch, 1.1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Total
    total_style = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#0066cc'),
        alignment=2  # Derecha
    )
    
        # Mostrar subtotal, IVA y total
    elements.append(Paragraph(f"<b>Subtotal:</b> ${cotizacion.subtotal_sin_iva:,.2f}", info_style))
    if cotizacion.incluir_iva:
        elements.append(Paragraph(f"<b>IVA (19%):</b> ${cotizacion.iva:,.2f}", info_style))
    elements.append(Paragraph(f"<b>TOTAL: ${cotizacion.total:,.2f}</b>", total_style))
    
    # Notas
    if cotizacion.notas_cliente:
        elements.append(Paragraph(f"<b>Notas del Cliente:</b> {cotizacion.notas_cliente}", info_style))
    
    if cotizacion.notas_admin:
        elements.append(Paragraph(f"<b>Notas de Administración:</b> {cotizacion.notas_admin}", info_style))
    
    # Pie de página
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("Tejos Olímpica - Todos los derechos reservados © 2025", footer_style))
    
    # Generar PDF
    doc.build(elements)
    return response
