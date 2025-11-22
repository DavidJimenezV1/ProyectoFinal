from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from .forms import RegistroClienteForm, LoginForm
from .models import Usuario

class RegistroClienteView(CreateView):
    model = Usuario
    form_class = RegistroClienteForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.tipo_usuario = Usuario.CLIENTE
        user.save()
        messages.success(self.request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
        return super().form_valid(form)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenido, {user.first_name}!")
            return redirect('home')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    """Vista para cerrar sesión - Funciona con GET y POST"""
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return HttpResponseRedirect('/')

def perfil_usuario(request):
    return render(request, 'usuarios/perfil.html')