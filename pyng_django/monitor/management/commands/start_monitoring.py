from django.core.management.base import BaseCommand
from django.utils import timezone
import time
import threading
import signal
import sys
from datetime import datetime

from monitor.models import Polling
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Ejecutar monitoreo continuo de hosts'
    
    def __init__(self):
        super().__init__()
        self.monitoring_active = True
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            help='Intervalo en segundos (sobrescribe configuración de DB)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Ejecutar solo una vez',
        )
    
    def signal_handler(self, signum, frame):
        """Manejar señales para parada limpia"""
        self.stdout.write(
            self.style.WARNING(f'\n🛑 Recibida señal {signum}. Deteniendo monitoreo...')
        )
        self.monitoring_active = False
    
    def get_polling_interval(self, override_interval=None):
        """Obtener el intervalo de monitoreo"""
        if override_interval:
            return override_interval
        
        try:
            polling_config = Polling.objects.first()
            return polling_config.poll_interval if polling_config else 60
        except Exception:
            return 60
    
    def handle(self, *args, **options):
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        interval = self.get_polling_interval(options.get('interval'))
        
        if options['once']:
            self.stdout.write('🧪 Ejecutando monitoreo una vez...')
            call_command('poll_hosts')
            self.stdout.write(self.style.SUCCESS('✅ Monitoreo completado'))
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 Iniciando monitoreo automático (Intervalo: {interval}s)')
        )
        self.stdout.write('📋 Presiona Ctrl+C para detener')
        
        while self.monitoring_active:
            try:
                # Actualizar intervalo desde la base de datos
                current_interval = self.get_polling_interval(options.get('interval'))
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.stdout.write(f"⏰ [{timestamp}] Ejecutando monitoreo...")
                
                # Ejecutar el comando de monitoreo
                call_command('poll_hosts', verbosity=0)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ [{timestamp}] Monitoreo completado")
                )
                
                # Esperar el intervalo configurado
                for i in range(current_interval):
                    if not self.monitoring_active:
                        break
                    time.sleep(1)
                
            except KeyboardInterrupt:
                self.signal_handler(signal.SIGINT, None)
                break
            except Exception as e:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.stdout.write(
                    self.style.ERROR(f"❌ [{timestamp}] Error en monitoreo: {e}")
                )
                # Esperar 30 segundos antes de reintentar
                time.sleep(30)
        
        self.stdout.write(self.style.WARNING('🔚 Servicio de monitoreo detenido.'))
