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
    '''Hosts'''
    ip_address = models.CharField(max_length=15, unique=True, null=False)
    hostname = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    last_poll = models.CharField(max_length=20, blank=True, null=True)
    previous_status = models.CharField(max_length=10, blank=True, null=True)
    alerts_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.hostname or self.ip_address

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

