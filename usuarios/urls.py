from django.urls import path
from .views import RegistroClienteView, login_view, logout_view, perfil_usuario

urlpatterns = [
    path('registro/', RegistroClienteView.as_view(), name='registro'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('perfil/', perfil_usuario, name='perfil'),
]