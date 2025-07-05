from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Extendemos el usuario de Django para agregar el campo 'alerts_enabled'
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    alerts_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Hosts(models.Model):
    '''Hosts - Puede monitorear IPs, IP:Puerto, o URLs web'''
    ip_address = models.CharField(max_length=255, unique=True, null=False)  # Aumentado para URLs
    hostname = models.CharField(max_length=100, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)  # Puerto opcional para monitoreo de servicios
    status = models.CharField(max_length=50, blank=True, null=True)  # Aumentado para mensajes de error HTTP
    last_poll = models.CharField(max_length=20, blank=True, null=True)
    previous_status = models.CharField(max_length=50, blank=True, null=True)
    alerts_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.hostname or self.ip_address

    def is_web_url(self):
        """Determina si este host es una URL web"""
        from .utils import is_web_url
        return is_web_url(self.ip_address)

    def get_ip_only(self):
        """Obtener solo la IP sin el puerto (para hosts IP)"""
        if self.is_web_url():
            return self.ip_address  # Para URLs, devolver la URL completa
        return self.ip_address.split(':')[0] if ':' in self.ip_address else self.ip_address
    
    def get_port(self):
        """Obtener el puerto de la IP:Puerto o None"""
        if self.is_web_url():
            return None  # URLs no tienen puerto separado
        if ':' in self.ip_address:
            try:
                return int(self.ip_address.split(':')[1])
            except (ValueError, IndexError):
                return None
        return self.port

    def get_display_name(self):
        """Obtener nombre para mostrar (hostname o dirección)"""
        if self.hostname:
            return self.hostname
        elif self.is_web_url():
            return self.ip_address.replace('https://', '').replace('http://', '')
        else:
            return self.ip_address

    class Meta:
        verbose_name_plural = "Hosts"


class PollHistory(models.Model):
    '''Poll history for hosts'''
    poll_time = models.CharField(max_length=20, blank=True, null=True)
    poll_status = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateField(default=timezone.now)
    host = models.ForeignKey(Hosts, on_delete=models.CASCADE, related_name="poll_history")

    def __str__(self):
        return f"{self.host.hostname} - {self.poll_time}"

    class Meta:
        verbose_name_plural = "Poll Histories"


class HostAlerts(models.Model):
    '''Alerts For Host Status Change'''
    hostname = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.CharField(max_length=15, blank=True, null=True)
    host_status = models.CharField(max_length=20, blank=True, null=True)
    poll_time = models.CharField(max_length=20, blank=True, null=True)
    alert_cleared = models.BooleanField(default=False)
    date_created = models.DateField(default=timezone.now)
    host = models.ForeignKey(Hosts, on_delete=models.CASCADE, related_name="alerts")

    def __str__(self):
        return f"Alert for {self.hostname} at {self.poll_time}"

    class Meta:
        verbose_name_plural = "Host Alerts"


class Polling(models.Model):
    '''Polling Config'''
    poll_interval = models.IntegerField(default=60, null=False)
    history_truncate_days = models.IntegerField(default=10, null=False)

    class Meta:
        verbose_name_plural = "Polling"


class SmtpServer(models.Model):
    '''SMTP Server'''
    smtp_server = models.CharField(max_length=100, null=False)
    smtp_port = models.IntegerField(null=False)
    smtp_sender = models.CharField(max_length=100, null=False)


class WebThemes(models.Model):
    '''Web CSS Themes'''
    theme_name = models.CharField(max_length=100, null=False)
    theme_path = models.CharField(max_length=100, null=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.theme_name

    class Meta:
        verbose_name_plural = "Web Themes"

