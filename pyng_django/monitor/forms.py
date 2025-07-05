from django import forms
from django.contrib.auth.models import User
from .models import SmtpServer, Polling, Hosts, WebThemes


class SmtpConfigForm(forms.ModelForm):
    class Meta:
        model = SmtpServer
        fields = ['smtp_server', 'smtp_port', 'smtp_sender']
        widgets = {
            'smtp_server': forms.TextInput(attrs={'class': 'input is-large'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'input is-large'}),
            'smtp_sender': forms.EmailInput(attrs={'class': 'input is-large'}),
        }
        labels = {
            'smtp_server': 'Servidor SMTP',
            'smtp_port': 'Puerto SMTP',
            'smtp_sender': 'Direccion de envio SMTP',
        }


class PollingConfigForm(forms.ModelForm):
    class Meta:
        model = Polling
        fields = ['poll_interval', 'history_truncate_days']
        widgets = {
            'poll_interval': forms.NumberInput(attrs={'class': 'input is-large'}),
            'history_truncate_days': forms.NumberInput(attrs={'class': 'input is-large'}),
        }
        labels = {
            'poll_interval': 'Intervalo de monitoreo',
            'history_truncate_days': 'Dias de retencion del registro',
        }


class AddHostsForm(forms.Form):
    # This field is not on the model, so we define it here.
    # It will be used to process multiple addresses in the view.
    ip_address = forms.CharField(
        label='Direcciones a monitorear (una por línea)',
        widget=forms.Textarea(attrs={'class': 'textarea is-medium', 'rows': 10}),
        help_text='Puede agregar: IPs (192.168.1.1), IP:Puerto (192.168.1.1:8080), o URLs web (https://ejemplo.com)'
    )


class DeleteHostForm(forms.Form):
    host_id = forms.IntegerField(widget=forms.HiddenInput())


class FirstTimeSetupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'input is-large'}),
        label='Nombre de usuario'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input is-large'}),
        label='Correo electrónico'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Contraseña',
        help_text='Mínimo 8 caracteres, 1 mayúscula, 2 caracteres especiales'
    )
    verify_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Confirmar contraseña'
    )
    poll_interval = forms.IntegerField(
        initial=60,
        widget=forms.NumberInput(attrs={'class': 'input is-large'}),
        label='Intervalo de monitoreo (segundos)'
    )
    retention_days = forms.IntegerField(
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'input is-large'}),
        label='Días de retención del historial'
    )
    smtp_server = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input is-large'}),
        label='Servidor SMTP (opcional)'
    )
    smtp_port = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'input is-large'}),
        label='Puerto SMTP (opcional)'
    )
    smtp_sender = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'input is-large'}),
        label='Email del remitente (opcional)'
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        verify_password = cleaned_data.get('verify_password')

        if password and verify_password:
            if password != verify_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")


class SelectThemeForm(forms.Form):
    id = forms.ModelChoiceField(
        queryset=WebThemes.objects.all(),
        widget=forms.Select(attrs={'class': 'select is-large'}),
        label='Seleccionar tema',
        empty_label=None
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the initial value to the currently active theme
        active_theme = WebThemes.objects.filter(active=True).first()
        if active_theme:
            self.fields['id'].initial = active_theme


class SmtpTestForm(forms.Form):
    test_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input is-large'}),
        label='Email de prueba'
    )


class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input is-large'}),
        }
        labels = {
            'email': 'Dirección de correo electrónico',
        }


class UpdateHostForm(forms.ModelForm):
    class Meta:
        model = Hosts
        fields = ['ip_address', 'hostname', 'alerts_enabled']
        widgets = {
            'ip_address': forms.TextInput(attrs={'class': 'input is-large'}),
            'hostname': forms.TextInput(attrs={'class': 'input is-large'}),
            'alerts_enabled': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
        labels = {
            'ip_address': 'Dirección (IP, IP:Puerto, o URL web)',
            'hostname': 'Nombre del host',
            'alerts_enabled': 'Alertas habilitadas',
        }
    
    def clean_ip_address(self):
        address = self.cleaned_data['ip_address']
        
        # Usar la función de validación universal
        from .utils import validate_web_or_ip
        try:
            validated_address, address_type = validate_web_or_ip(address)
            return address  # Retornar el formato original si es válido
        except ValueError as e:
            raise forms.ValidationError(str(e))


class UpdatePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Contraseña actual'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Nueva contraseña'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Confirmar nueva contraseña'
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Las nuevas contraseñas no coinciden.")


class CreateUserForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'input is-large'}),
        label='Nombre de usuario'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input is-large'}),
        label='Correo electrónico',
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Contraseña'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input is-large'}),
        label='Confirmar contraseña'
    )
    
    USER_TYPE_CHOICES = [
        ('regular', 'Usuario regular (solo visualización)'),
        ('staff', 'Usuario staff (acceso al admin)'),
        ('superuser', 'Superusuario (control total)'),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'select is-large'}),
        label='Tipo de usuario',
        initial='regular'
    )
    
    alerts_enabled = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'checkbox'}),
        label='Habilitar alertas',
        required=False,
        initial=True
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe.")
        return username