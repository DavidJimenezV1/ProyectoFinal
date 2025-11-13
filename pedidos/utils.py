from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generar_pdf_pedido(pedido):
    """
    Genera un archivo PDF para un objeto de Pedido.
    Retorna un BytesIO con el contenido del PDF.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    elements = []
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'TituloPedido',
        parent=styles['h1'],
        fontSize=22,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['h2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
    )

    elements.append(Paragraph(f"Detalle del Pedido #{pedido.id}", titulo_style))

    info_data = [
        ['Fecha del Pedido:', pedido.fecha_pedido.strftime('%d/%m/%Y')],
        ['Cliente:', str(pedido.cliente)],
        ['Email:', pedido.cliente.email],
        ['Estado:', pedido.get_estado_display()],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    elements.append(Paragraph("Artículos del Pedido", subtitulo_style))
    
    items_data = [['Producto', 'Cantidad', 'Precio Unit.', 'Subtotal']]
    
# LÍNEA CORREGIDA
    for item in pedido.detallepedido_set.all():
        items_data.append([
            item.producto.nombre,
            item.cantidad,
            f"${item.precio_unitario:,.2f}",
	    f"${item.subtotal():.2f}"
        ])
       
    items_data.append(['', '', 'TOTAL', f'${pedido.get_total():,.2f}'])
    
    items_table = Table(items_data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('ALIGN', (2, -1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (2, -1), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(items_table)
    
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
