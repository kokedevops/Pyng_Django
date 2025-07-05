import smtplib
import time
from concurrent.futures import ThreadPoolExecutor # Keep this import
from email.mime.text import MIMEText

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.db import transaction # For setup_view
from django.urls import reverse
from django.views.decorators.http import require_POST
from password_strength import PasswordPolicy
from django.contrib.auth import views as auth_views

from .forms import (AddHostsForm, DeleteHostForm, FirstTimeSetupForm,
                    PollingConfigForm, SelectThemeForm, SmtpConfigForm,
                    SmtpTestForm, UpdateEmailForm, UpdateHostForm,
                    UpdatePasswordForm, CreateUserForm)
from .models import (HostAlerts, Hosts, PollHistory, Polling, Profile,
                     SmtpServer, WebThemes)

from .utils import get_hostname, poll_host_ip, validate_ip_port, poll_host_smart, validate_web_or_ip, poll_host_universal # Import from new utils file
# --- Constantes y Helpers ---

PASSWORD_POLICY = {
    'Length': 8,
    'Uppercase': 1,
    'Nonletters': 2
}

WEB_THEMES_DEFAULT = {
    'Darkly (Dark/Dark Blue)': 'css/darkly.min.css',
    'Flatly (Light/Dark Blue)': 'css/flatly.min.css'
}

def database_configured():
    """Verifica si la base de datos está configurada buscando algún usuario."""
    return User.objects.exists()

def test_password(password):
    """Verifica que una contraseña cumpla con la política definida."""
    policy = PasswordPolicy.from_names(
        length=PASSWORD_POLICY['Length'],
        uppercase=PASSWORD_POLICY['Uppercase'],
        nonletters=PASSWORD_POLICY['Nonletters']
    )
    return policy.test(password)

def get_active_theme():
    """Obtiene el tema activo de la base de datos."""
    if not database_configured():
        return {'theme_path': 'css/darkly.min.css'}
    theme = WebThemes.objects.filter(active=True).first()
    if not theme:
        theme = WebThemes.objects.first()
        if theme:
            theme.active = True
            theme.save()
        else:
            return {'theme_path': 'css/darkly.min.css'}
    return theme

def add_context(context=None):
    """Agrega contexto global a todas las plantillas."""
    if context is None:
        context = {}
    context['db_configured'] = database_configured()
    context['active_theme'] = get_active_theme()
    return context

# --- Vistas Principales ---

def index(request):
    """Página de índice."""
    if not database_configured():
        return redirect(reverse('monitor:setup'))

    polling_config = Polling.objects.first()
    refresh_interval = polling_config.poll_interval * 1000 if polling_config else 60000

    context = add_context({'refresh_interval': refresh_interval})
    return render(request, 'monitor/index.html', context)

@login_required
def account(request):
    """Cuenta de usuario."""
    password_form = UpdatePasswordForm()
    email_form = UpdateEmailForm()
    context = add_context({
        'password_form': password_form,
        'email_form': email_form
    })
    return render(request, 'monitor/account.html', context)

@login_required
def set_theme(request):
    """Establecer tema."""
    if request.method == 'POST':
        form = SelectThemeForm(request.POST)
        if form.is_valid():
            theme_id = form.cleaned_data['id'].id  # Get the ID from the model instance
            try:
                WebThemes.objects.update(active=False)
                theme_to_activate = WebThemes.objects.get(id=theme_id)
                theme_to_activate.active = True
                theme_to_activate.save()
                messages.success(request, 'Tema actualizado correctamente')
            except WebThemes.DoesNotExist:
                messages.error(request, 'Tema seleccionado no encontrado.')
            except Exception as e:
                messages.error(request, f'Fallo al actualizar el tema: {str(e)}')
        else:
            messages.error(request, 'Formulario no válido')
        return redirect(reverse('monitor:set_theme'))
    else:
        themes = WebThemes.objects.order_by('-active').values('id', 'theme_name', 'active')
        form = SelectThemeForm()

        context = add_context({'form': form, 'themes': themes})
        return render(request, 'monitor/setTheme.html', context)

@login_required
def configure_polling(request):
    """Configurar intervalo de sondeo."""
    polling_config = Polling.objects.first()
    if request.method == 'POST':
        form = PollingConfigForm(request.POST, instance=polling_config)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Configuración de sondeo actualizada correctamente.')
            except Exception as e:
                messages.error(request, f'Fallo al actualizar la configuración de sondeo: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        return redirect(reverse('monitor:configure_polling'))
    else:
        form = PollingConfigForm(instance=polling_config)
        context = add_context({'form': form, 'polling_config': polling_config})
        return render(request, 'monitor/pollingConfig.html', context)

# --- Vista de Configuración ---

def setup_view(request):
    """Página de configuración inicial."""
    if database_configured():
        return redirect(reverse('monitor:index'))

    if request.method == 'POST':
        form = FirstTimeSetupForm(request.POST)
        if form.is_valid():
            with transaction.atomic(): # Ensure all or nothing for setup
                if form.cleaned_data['password'] != form.cleaned_data['verify_password']:
                    messages.error(request, 'Las contraseñas no coinciden.')
                elif test_password(form.cleaned_data['password']):
                    messages.error(request, f"La contraseña no cumplió los requisitos: {form.fields['password'].help_text}")
                else:
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password']
                    )
                    Profile.objects.create(user=user, alerts_enabled=True)
                    Polling.objects.create(
                        poll_interval=form.cleaned_data['poll_interval'],
                        history_truncate_days=form.cleaned_data['retention_days']
                    )
                    SmtpServer.objects.create(
                        smtp_server=form.cleaned_data.get('smtp_server', ''),
                        smtp_port=form.cleaned_data.get('smtp_port') or 0,
                        smtp_sender=form.cleaned_data.get('smtp_sender', '')
                    )
                    for i, (name, path) in enumerate(WEB_THEMES_DEFAULT.items()):
                        WebThemes.objects.create(theme_name=name, theme_path=path, active=(i == 0))
                    
                    messages.success(request, '¡Configuración completa! Por favor, inicie sesión.')
                    return redirect(reverse('monitor:login'))
    else:
        form = FirstTimeSetupForm()
    
    return render(request, 'monitor/setup.html', add_context({'form': form}))

# --- Vistas de Autenticación ---

@login_required
@require_POST
def update_password(request):
    form = UpdatePasswordForm(request.POST)
    if form.is_valid():
        user = request.user
        if not user.check_password(form.cleaned_data['current_password']):
            messages.error(request, 'La contraseña actual no es válida.')
        elif form.cleaned_data['new_password'] != form.cleaned_data['verify_password']:
            messages.error(request, 'Las contraseñas no coinciden.')
        else:
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada correctamente.')
    return redirect(reverse('monitor:account'))

@login_required
@require_POST
def update_email(request):
    form = UpdateEmailForm(request.POST)
    if form.is_valid():
        user = request.user
        if not user.check_password(form.cleaned_data['password']):
            messages.error(request, 'La contraseña actual no es válida.')
        elif form.cleaned_data['email'] != form.cleaned_data['email_verify']:
            messages.error(request, 'Las direcciones de correo electrónico no coinciden.')
        else:
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, 'Correo electrónico actualizado correctamente.')
    return redirect(reverse('monitor:account'))

# --- Vistas de Hosts ---

@login_required
def add_hosts(request):
    if request.method == 'POST':
        form = AddHostsForm(request.POST)
        if form.is_valid():
            address_list = form.cleaned_data['ip_address'].splitlines()
            
            # Helper function to be executed in threads
            def _process_single_address(address_str):
                # Usar la nueva función universal para verificar IP, IP:Puerto o URL
                status = poll_host_universal(address_str)
                current_time = time.strftime('%Y-%m-%d %T')
                
                # Para el hostname, determinar según el tipo de dirección
                from .utils import is_web_url
                if is_web_url(address_str):
                    # Es una URL web, usar la parte del dominio como hostname
                    hostname = address_str.replace('https://', '').replace('http://', '').split('/')[0]
                else:
                    # Es IP o IP:Puerto, obtener hostname por DNS
                    ip_only = address_str.split(':')[0] if ':' in address_str else address_str
                    hostname = get_hostname(ip_only)
                
                return Hosts(ip_address=address_str, hostname=hostname, status=status, last_poll=current_time)

            with ThreadPoolExecutor(max_workers=100) as pool:
                for addr_str in address_list:
                    addr_str = addr_str.strip()
                    if not addr_str: continue
                    try:
                        # Usar la nueva función de validación universal
                        validated_address, address_type = validate_web_or_ip(addr_str)
                        
                        if Hosts.objects.filter(ip_address=addr_str).exists():
                            messages.warning(request, f'Dirección {addr_str} ya existe.')
                        else:
                            # Submit the task to the thread pool
                            future = pool.submit(_process_single_address, addr_str)
                            new_host = future.result()
                            new_host.save()
                            
                            if address_type == 'web':
                                messages.success(request, f"Agregado correctamente {new_host.ip_address} ({new_host.hostname}) - Sitio Web")
                            elif ':' in addr_str:
                                port = addr_str.split(':')[1]
                                messages.success(request, f"Agregado correctamente {new_host.ip_address} ({new_host.hostname}) - Puerto: {port}")
                            else:
                                messages.success(request, f"Agregado correctamente {new_host.ip_address} ({new_host.hostname})")
                                
                    except ValueError as e:
                        messages.error(request, f'{addr_str}: {str(e)}')
                    except Exception as e:
                        messages.error(request, f"Fallo al agregar {addr_str}: {e}")
        return redirect(reverse('monitor:add_hosts'))
    else:
        form = AddHostsForm()
        return render(request, 'monitor/addHosts.html', add_context({'form': form}))

@login_required
def update_hosts(request):
    if request.method == 'POST':
        form = UpdateHostForm(request.POST)
        if form.is_valid():
            try:
                host = Hosts.objects.get(id=form.cleaned_data['id'])
                
                # Validar la nueva dirección si se proporciona
                new_address = form.cleaned_data.get('ip_address')
                if new_address:
                    try:
                        # Usar nuestra función de validación universal
                        validated_address, address_type = validate_web_or_ip(new_address)
                        host.ip_address = new_address
                    except ValueError as e:
                        messages.error(request, f'Error en la dirección: {str(e)}')
                        return redirect(reverse('monitor:update_hosts'))
                
                host.hostname = form.cleaned_data.get('hostname', host.hostname)
                host.alerts_enabled = form.cleaned_data.get('alerts_enabled', host.alerts_enabled)
                host.save()
                messages.success(request, f'Host {host.hostname} actualizado exitosamente')
            except Hosts.DoesNotExist:
                messages.error(request, 'Host no encontrado.')
            except Exception as e:
                messages.error(request, f'Error al actualizar el host: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        return redirect(reverse('monitor:update_hosts'))
    else:
        hosts = Hosts.objects.all().order_by('hostname')
        return render(request, 'monitor/updateHosts.html', add_context({'hosts': hosts}))

@login_required
@require_POST
def delete_host(request):
    form = DeleteHostForm(request.POST)
    if form.is_valid():
        try:
            host = Hosts.objects.get(id=form.cleaned_data['host_id'])
            hostname = host.hostname
            host.delete()
            messages.success(request, f'Host {hostname} eliminado exitosamente')
        except Hosts.DoesNotExist:
            messages.error(request, 'Host no encontrado.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el host: {str(e)}')
    else:
        messages.error(request, 'Formulario inválido.')
    return redirect(reverse('monitor:update_hosts'))

# --- Vistas de SMTP ---

@login_required
def configure_smtp(request):
    smtp_config = SmtpServer.objects.first()
    if request.method == 'POST':
        form = SmtpConfigForm(request.POST)
        if form.is_valid():
            smtp_config, _ = SmtpServer.objects.get_or_create(id=1)
            smtp_config.smtp_server = form.cleaned_data['server']
            smtp_config.smtp_port = form.cleaned_data['port']
            smtp_config.smtp_sender = form.cleaned_data['sender']
            smtp_config.save()
            messages.success(request, 'Configuracion SMTP actualizada correctamente')
        return redirect(reverse('monitor:configure_smtp'))
    else:
        form = SmtpConfigForm(instance=smtp_config)
        test_form = SmtpTestForm()
        context = add_context({'form': form, 'test_form': test_form, 'smtp': smtp_config})
        return render(request, 'monitor/smtpConfig.html', context)

@login_required
@require_POST
def smtp_test(request):
    form = SmtpTestForm(request.POST)
    if form.is_valid():
        recipient = form.cleaned_data['recipient']
        smtp_config = SmtpServer.objects.first()
        if not (smtp_config and smtp_config.smtp_server):
            messages.error(request, 'SMTP no está configurado.')
        else:
            msg = MIMEText('MENSAJE DE PRUEBA PYNG', 'html')
            msg['Subject'] = 'PYNG SMTP PRUEBA'
            msg['From'] = smtp_config.smtp_sender
            msg['To'] = recipient
            try:
                with smtplib.SMTP(smtp_config.smtp_server, smtp_config.smtp_port, timeout=10) as server:
                    server.starttls()
                    server.sendmail(smtp_config.smtp_sender, [recipient], msg.as_string())
                messages.success(request, 'Successfully sent SMTP test message')
            except Exception as e:
                messages.error(request, f'Failed to send SMTP test message: {e}')
    return redirect(reverse('monitor:configure_smtp'))

# --- Vistas de Autenticación ---

class CustomLoginView(auth_views.LoginView):
    """Vista de login personalizada que incluye el contexto del tema."""
    template_name = 'monitor/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar nuestro contexto personalizado
        context = add_context(context)
        return context

# --- Vistas de Gestión de Usuarios ---

@login_required
def create_user_view(request):
    """Vista para crear nuevos usuarios (solo para administradores)"""
    # Verificar que el usuario actual sea superusuario
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para crear usuarios.')
        return redirect('monitor:index')
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            try:
                # Crear el usuario
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user_type = form.cleaned_data['user_type']
                alerts_enabled = form.cleaned_data['alerts_enabled']
                
                # Determinar permisos según el tipo de usuario
                is_staff = user_type in ['staff', 'superuser']
                is_superuser = user_type == 'superuser'
                
                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=is_staff,
                    is_superuser=is_superuser
                )
                
                # Crear perfil del usuario
                Profile.objects.create(
                    user=user,
                    alerts_enabled=alerts_enabled
                )
                
                # Mensaje de éxito
                user_type_display = {
                    'regular': 'Usuario regular',
                    'staff': 'Usuario staff', 
                    'superuser': 'Superusuario'
                }[user_type]
                
                messages.success(
                    request, 
                    f'Usuario "{username}" creado exitosamente como {user_type_display}.'
                )
                
                # Redirigir a la vista de crear usuario para crear más
                return redirect('monitor:create_user')
                
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
    else:
        form = CreateUserForm()
    
    context = add_context({
        'form': form,
        'page_title': 'Crear Usuario'
    })
    
    return render(request, 'monitor/createUser.html', context)

@login_required
def list_users_view(request):
    """Vista para listar todos los usuarios (solo para administradores)"""
    # Verificar que el usuario actual sea superusuario
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para ver la lista de usuarios.')
        return redirect('monitor:index')
    
    # Obtener todos los usuarios con sus perfiles
    users = User.objects.all().order_by('username')
    users_with_profiles = []
    
    for user in users:
        try:
            profile = Profile.objects.get(user=user)
            alerts_enabled = profile.alerts_enabled
        except Profile.DoesNotExist:
            alerts_enabled = False
        
        users_with_profiles.append({
            'user': user,
            'alerts_enabled': alerts_enabled
        })
    
    context = add_context({
        'users_with_profiles': users_with_profiles,
        'page_title': 'Lista de Usuarios'
    })
    
    return render(request, 'monitor/listUsers.html', context)
