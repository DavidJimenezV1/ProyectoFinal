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

# ----------------- UI: lista y edición de pedidos (añadido por feat/pedidos/ui-bootstrap) -----------------
def lista_pedidos(request):
    from django.shortcuts import render
    from django.core.paginator import Paginator
    from django.db.models import Q

    q = request.GET.get('q', '').strip()
    pedidos_qs = Pedido.objects.select_related('cliente').all().order_by('-fecha_pedido')
    if q:
        pedidos_qs = pedidos_qs.filter(
            Q(cliente__nombre__icontains=q) |
            Q(cliente__apellido__icontains=q) |
            Q(cliente__email__icontains=q)
        )
    paginator = Paginator(pedidos_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pedidos/lista_pedidos.html', {'pedidos': page_obj, 'q': q})


def editar_pedido(request, pk):
    from django.shortcuts import render, redirect, get_object_or_404
    from django.http import HttpResponseForbidden
    from django.db import transaction
    from .forms import PedidoForm, PedidoLineaFormSet

    if not request.user.is_staff:
        return HttpResponseForbidden("Necesitas permisos de staff para editar pedidos.")

    pedido = get_object_or_404(Pedido, pk=pk)
    FormSet = PedidoLineaFormSet

    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        formset = FormSet(request.POST, instance=pedido)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('pedidos:detalle_pedido', pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)
        formset = FormSet(instance=pedido)

    return render(request, 'pedidos/pedido_form.html', {'form': form, 'formset': formset, 'pedido': pedido})
# ----------------- fin de cambios UI -----------------

