#!/usr/bin/env python3
"""
Script para verificar los hosts existentes en la base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.models import Hosts

def main():
    hosts = Hosts.objects.all()
    print(f"Total hosts: {hosts.count()}")
    print("\nHosts existentes:")
    print("-" * 70)
    
    for host in hosts:
        host_type = "Web" if host.is_web_url() else "IP"
        print(f"Host: {host.hostname or 'N/A'}")
        print(f"  Dirección: {host.ip_address}")
        print(f"  Tipo: {host_type}")
        print(f"  Estado: {host.status}")
        print(f"  Última verificación: {host.last_poll}")
        print()

if __name__ == "__main__":
    main()
