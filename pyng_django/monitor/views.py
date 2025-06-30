import smtplib
import time
from concurrent.futures import ThreadPoolExecutor # Keep this import
from email.mime.text import MIMEText
from ipaddress import AddressValueError
from ipaddress import ip_address as ip_address_validator

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
                    UpdatePasswordForm)
from .models import (HostAlerts, Hosts, PollHistory, Polling, Profile,
                     SmtpServer, WebThemes)

from .utils import get_hostname, poll_host_ip # Import from new utils file
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
        form = PollingConfigForm(request.POST)
        if form.is_valid() and polling_config:
            try:
                if form.cleaned_data.get('interval'):
                    polling_config.poll_interval = form.cleaned_data['interval']
                if form.cleaned_data.get('retention_days'):
                    polling_config.history_truncate_days = form.cleaned_data['retention_days']
                polling_config.save()
                messages.success(request, 'Configuración de sondeo actualizada correctamente.')
            except Exception:
                messages.error(request, 'Fallo al actualizar la configuración de sondeo.')
        return redirect(reverse('monitor:configure_polling'))
    else:
        initial_data = {}
        if polling_config:
            initial_data = {
                'interval': polling_config.poll_interval,
                'retention_days': polling_config.history_truncate_days
            }
        form = PollingConfigForm(initial=initial_data)
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
            ip_list = form.cleaned_data['ip_address'].splitlines()
            
            # Helper function to be executed in threads
            def _process_single_ip(ip_address_str):
                status = poll_host_ip(ip_address_str)
                current_time = time.strftime('%Y-%m-%d %T')
                hostname = get_hostname(ip_address_str)
                return Hosts(ip_address=ip_address_str, hostname=hostname, status=status, last_poll=current_time)

            with ThreadPoolExecutor(max_workers=100) as pool:
                for ip_str in ip_list:
                    ip_str = ip_str.strip()
                    if not ip_str: continue
                    try:
                        ip_address_validator(ip_str)
                        if Hosts.objects.filter(ip_address=ip_str).exists():
                            messages.warning(request, f'Direccion IP {ip_str} ya existe.')
                        else:
                            # Submit the task to the thread pool
                            future = pool.submit(_process_single_ip, ip_str)
                            new_host = future.result()
                            new_host.save()
                            messages.success(request, f"Agregado correctamente {new_host.ip_address} ({new_host.hostname})")
                    except AddressValueError:
                        messages.error(request, f'{ip_str} No es una IP valida')
                    except Exception as e:
                        messages.error(request, f"Fallo al agregar {ip_str}: {e}")
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
                host.hostname = form.cleaned_data.get('hostname', host.hostname)
                host.ip_address = form.cleaned_data.get('ip_address', host.ip_address)
                host.alerts_enabled = form.cleaned_data['alerts'] == 'True'
                host.save()
                messages.success(request, f'Successfully updated host {host.hostname}')
            except Hosts.DoesNotExist:
                messages.error(request, 'Host not found.')
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
            host = Hosts.objects.get(id=form.cleaned_data['id'])
            hostname = host.hostname
            host.delete()
            messages.success(request, f'Successfully deleted {hostname}')
        except Hosts.DoesNotExist:
            messages.error(request, 'Host not found.')
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
