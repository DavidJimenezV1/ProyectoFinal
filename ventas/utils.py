from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from decimal import Decimal
from io import BytesIO
from datetime import datetime

def generar_pdf_factura(factura):
    """
    Genera un PDF de la factura
    Retorna un BytesIO con el contenido del PDF
    """
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch,
    )
    
    # Contenedor de elementos
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#417690'),
        spaceAfter=10,
        alignment=TA_CENTER,
    )
    
    encabezado_style = ParagraphStyle(
        'Encabezado',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=4,
    )
    
    # Título
    elements.append(Paragraph("FACTURA", titulo_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información de factura
    info_factura = [
        ['Número de Factura:', factura.numero],
        ['Fecha de Emisión:', factura.fecha_emision.strftime('%d de %B de %Y a las %H:%M')],
        ['Estado:', factura.get_estado_display()],
    ]
    
    table_info = Table(info_factura, colWidths=[2*inch, 4*inch])
    table_info.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#417690')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(table_info)
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del cliente
    elements.append(Paragraph("INFORMACIÓN DEL CLIENTE", encabezado_style))
    
    cliente_data = [
        ['Nombre:', factura.nombre_cliente],
        ['Documento:', factura.documento_cliente or '---'],
        ['Dirección:', factura.direccion_cliente or '---'],
        ['Teléfono:', factura.telefono_cliente or '---'],
        ['Email:', factura.email_cliente or '---'],
    ]
    
    table_cliente = Table(cliente_data, colWidths=[1.5*inch, 4.5*inch])
    table_cliente.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#417690')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table_cliente)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de items
    elements.append(Paragraph("ITEMS DE FACTURA", encabezado_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # Encabezados de tabla
    items_data = [
        ['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal'],
    ]
    
    # Agregar items
    for item in factura.items.all():
        items_data.append([
            str(item.producto.nombre)[:40],
            str(item.cantidad),
            f"${item.precio_unitario:,.2f}",
            f"${item.subtotal:,.2f}",
        ])
    
    table_items = Table(items_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    table_items.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#417690')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    elements.append(table_items)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totales
    totales_data = [
        ['', 'Subtotal:', f"${factura.subtotal:,.2f}"],
        ['', 'IVA ({:.0f}%):'.format(factura.porcentaje_iva), f"${factura.valor_iva:,.2f}"],
        ['', 'TOTAL:', f"${factura.total:,.2f}"],
    ]
    
    table_totales = Table(totales_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    table_totales.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -2), 'Helvetica', 10),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#28a745')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f9f0')),
        ('GRID', (0, -1), (-1, -1), 1, colors.HexColor('#28a745')),
    ]))
    elements.append(table_totales)
    
    # Notas
    if factura.notas:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("NOTAS:", encabezado_style))
        elements.append(Paragraph(factura.notas, styles['Normal']))
    
    # Pie de página
    elements.append(Spacer(1, 0.3*inch))
    pie_style = ParagraphStyle(
        'Pie',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER,
    )
    elements.append(Paragraph("Tejos Olímpica - Generado automáticamente", pie_style))
    elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d de %B de %Y a las %H:%M')}", pie_style))
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
