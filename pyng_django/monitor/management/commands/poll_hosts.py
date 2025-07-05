import platform
import socket
import subprocess
import time
import requests
import json
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor

from monitor.models import Hosts, Polling, PollHistory, HostAlerts, Profile
from monitor.utils import poll_host_universal
from monitor.utils import poll_host_smart  # Importar la nueva función


def get_hostname(ip_address):
    '''Gets the FQDN from an IP Address'''
    try:
        hostname = socket.getfqdn(ip_address)
    except socket.error:
        hostname = 'Unknown'
    return hostname


def poll_host_ip(host_ip, count=3):
    '''Poll host via ICMP ping to see if it is up/down'''
    if platform.system().lower() == 'windows':
        command = ['ping', '-n', str(count), '-w', '1000', host_ip]
    else:
        command = ['ping', '-c', str(count), '-W', '1', host_ip]

    response = subprocess.call(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return '🟢 Up 🟢' if response == 0 else '🔴 Down 🔴'


def poll_host_task(host):
    # Usar la función universal que maneja IP, IP:Puerto y URLs web
    status = poll_host_universal(host.ip_address)
    poll_time = time.strftime('%Y-%m-%d %T')

    # Crear historial SIEMPRE
    PollHistory.objects.create(
        host=host,
        poll_time=poll_time,
        poll_status=status
    )

    # Actualizar SIEMPRE el last_poll y el status actual
    host.last_poll = poll_time
    status_changed = host.status != status
    
    if status_changed:
        host.previous_status = host.status
        host.status = status
        host.save()

        # Crear alerta si están habilitadas
        if host.alerts_enabled:
            alert = HostAlerts.objects.create(
                host=host,
                hostname=host.hostname,
                ip_address=host.ip_address,
                host_status=status,
                poll_time=poll_time,
                alert_cleared=False # Marcar como no enviada
            )
            # Enviar alerta a Telegram
            message = f'El host {host.hostname} [IP: {host.ip_address}]: cambio su estado a {host.status} a las {host.last_poll}'
            try:
                # Reemplaza con tu BOT_TOKEN y CHAT_ID
                r = requests.post(
                    'https://api.telegram.org/bot<BOT_TOKEN>/sendMessage',
                    data={'chat_id': '<CHAT_ID>', 'text': message}
                )
                if r.status_code == 200:
                    alert.alert_cleared = True # Marcar como enviada
                    alert.save()
            except Exception as e:
                print(f"Error sending Telegram alert: {e}")
    else:
        # Si no cambió el estado, solo actualizar el last_poll
        host.status = status  # Asegurar que esté sincronizado
        host.save()


class Command(BaseCommand):
    help = 'Polls all hosts to check their status.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting host polling...')
        start_time = time.perf_counter()

        hosts_to_poll = Hosts.objects.all()
        
        # Usamos ThreadPoolExecutor para concurrencia
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(poll_host_task, hosts_to_poll)

        # Limpieza del historial
        polling_config = Polling.objects.first()
        if polling_config:
            retention_days = polling_config.history_truncate_days
            cutoff_date = timezone.now().date() - timedelta(days=retention_days)
            PollHistory.objects.filter(date_created__lt=cutoff_date).delete()
            self.stdout.write('Poll history cleanup complete.')

        end_time = time.perf_counter()
        self.stdout.write(self.style.SUCCESS(f'Host polling finished in {end_time - start_time:.2f} seconds.'))

