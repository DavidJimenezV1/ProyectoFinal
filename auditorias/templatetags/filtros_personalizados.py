"""
Filtros personalizados para usar en plantillas Django
Incluye formatos de moneda colombiana
"""

from django import template
from decimal import Decimal

register = template.Library()


@register.filter(name='pesos')
def formato_pesos(valor):
    """
    Convierte un valor a formato de pesos colombianos
    Uso en plantillas: {{ valor|pesos }}
    """
    try:
        if valor is None:
            return "$0"
        
        valor_float = float(valor)
        # Formato: $1.234.567
        return f"${valor_float:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "N/A"


@register.filter(name='pesos_decimales')
def formato_pesos_decimales(valor):
    """
    Convierte un valor a formato de pesos colombianos con decimales
    Uso en plantillas: {{ valor|pesos_decimales }}
    """
    try:
        if valor is None:
            return "$0,00"
        
        valor_float = float(valor)
        # Formato: $1.234.567,89
        return f"${valor_float:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
    except (ValueError, TypeError):
        return "N/A"


@register.filter(name='moneda')
def formato_moneda(valor, simbolo='$'):
    """
    Convierte un valor a formato de moneda configurable
    Uso en plantillas: {{ valor|moneda:"$" }} o {{ valor|moneda:"COP" }}
    """
    try:
        if valor is None:
            return f"{simbolo}0"
        
        valor_float = float(valor)
        return f"{simbolo}{valor_float:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "N/A"