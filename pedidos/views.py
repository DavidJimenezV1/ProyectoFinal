# ========= INICIO DEL CÓDIGO PARA views.py =========

# --- Importaciones para la API (las que ya tenías) ---
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import ClienteSerializer, PedidoSerializer, DetallePedidoSerializer

# --- Importaciones de Django y para la descarga PDF ---
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

# --- ¡NUEVAS IMPORTACIONES PARA LA PÁGINA VISUAL! ---
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

# --- Importaciones de tus modelos y utilidades ---
from .models import Cliente, Pedido, DetallePedido
from .utils import generar_pdf_pedido


# ========= Vistas para la API (las que ya tenías) =========

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated]


# ========= Vista para la descarga PDF (la que ya tenías) =========

@login_required
def descargar_pedido_pdf(request, pk):
    """
    Genera y sirve la descarga de un pedido en formato PDF.
    """
    pedido = get_object_or_404(Pedido, pk=pk)

    if not request.user.is_staff and pedido.cliente != request.user:
        return HttpResponseForbidden("No tienes permiso para acceder a este documento.")

    # Corregido aquí para usar fecha_pedido
    pdf_buffer = generar_pdf_pedido(pedido)

    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Pedido_{pedido.id}.pdf"'

    return response


# ========= ¡NUEVA VISTA PARA LA PÁGINA DE DETALLE VISUAL! =========

class PedidoDetailView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/detalle_pedido.html'  # El archivo HTML que crearemos
    context_object_name = 'pedido'  # El nombre que usaremos en la plantilla

# ========= FIN DEL CÓDIGO PARA views.py =========
