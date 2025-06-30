from django import forms

PASSWORD_POLICY_HELP = 'Politica de contraseña: Longitud mínima (8), Mínimo de mayúsculas (1), Mínimo de caracteres especiales (2).'

class FirstTimeSetupForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Clave', widget=forms.PasswordInput, help_text=PASSWORD_POLICY_HELP, required=True)
    verify_password = forms.CharField(label='Verificar clave', widget=forms.PasswordInput, required=True)
    
    poll_interval = forms.IntegerField(label='Intervalo de revision (segundos)', initial=60, required=True)
    retention_days = forms.IntegerField(label='Tiempo de retencion de historial (dias)', initial=10, required=True)
    
    smtp_server = forms.CharField(label='Servidor', max_length=100, required=False)
    smtp_port = forms.IntegerField(label='Puerto', required=False)
    smtp_sender = forms.EmailField(label='Direccion de envio', required=False)


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=100)
    password = forms.CharField(label='Clave', widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, label='Recuerdame')


class UpdatePasswordForm(forms.Form):
    current_password = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput, help_text=PASSWORD_POLICY_HELP, required=True)
    verify_password = forms.CharField(label='Verificar contraseña', widget=forms.PasswordInput, required=True)


class UpdateEmailForm(forms.Form):
    email = forms.EmailField(label='Nueva dirección de correo electrónico', required=True)
    email_verify = forms.EmailField(label='Confirme su dirección de correo electrónico', required=True)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=True)


class SmtpConfigForm(forms.Form):
    server = forms.CharField(label='Servidor', max_length=100, required=True)
    port = forms.IntegerField(label='Puerto', required=True)
    sender = forms.EmailField(label='Dirección del remitente', required=True)


class AddHostsForm(forms.Form):
    ip_address = forms.CharField(
        label='Direccion IP',
        widget=forms.Textarea(attrs={'rows': 10, 'class': 'textarea is-medium'}),
        help_text='Una direccion IP por linea'
    )


class UpdateHostForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    hostname = forms.CharField(max_length=100, required=False)
    ip_address = forms.CharField(max_length=15, required=False)
    alerts = forms.ChoiceField(choices=[(True, 'Yes'), (False, 'No')], widget=forms.RadioSelect, label="Alerts Activadas")


class DeleteHostForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    hostname = forms.CharField(widget=forms.HiddenInput())


class SelectThemeForm(forms.Form):
    id = forms.ChoiceField(label="Tema", choices=[])

    def __init__(self, *args, **kwargs):
        themes = kwargs.pop('themes', None)
        super().__init__(*args, **kwargs)
        if themes:
            theme_choices = [(theme['id'], theme['theme_name']) for theme in themes]
            self.fields['id'].choices = theme_choices


class PollingConfigForm(forms.Form):
    interval = forms.IntegerField(label='Intervalo de revision', required=False)
    retention_days = forms.IntegerField(label='Días de retención del historial de monitoreo', required=False)


class SmtpTestForm(forms.Form):
    recipient = forms.EmailField(label='Direccion Email Recepcion', required=True)