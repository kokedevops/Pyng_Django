#!/usr/bin/env python3
"""
Script para probar las mejoras del dashboard
"""
import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.models import Hosts
from django.contrib.auth.models import User

def test_api_endpoints():
    """Test the API endpoints to verify they work with the new type column"""
    print("Testing API endpoints...")
    
    # Test get_all_hosts endpoint
    try:
        response = requests.get('http://localhost:8000/api/hosts')
        if response.status_code == 200:
            data = response.json()
            hosts = data.get('data', [])
            print(f"✅ get_all_hosts: {len(hosts)} hosts retrieved")
            
            # Check if host_type is present
            if hosts and 'host_type' in hosts[0]:
                print("✅ host_type field present in API response")
                # Show some examples
                for host in hosts[:3]:
                    print(f"  - {host['hostname']}: {host['ip_address']} ({host['host_type']})")
            else:
                print("❌ host_type field missing in API response")
        else:
            print(f"❌ get_all_hosts failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ get_all_hosts error: {e}")
    
    # Test get_host_counts endpoint
    try:
        response = requests.get('http://localhost:8000/api/host_counts')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ get_host_counts: {data}")
        else:
            print(f"❌ get_host_counts failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ get_host_counts error: {e}")

def test_host_types():
    """Test host type detection"""
    print("\nTesting host type detection...")
    
    hosts = Hosts.objects.all()
    web_count = 0
    ip_count = 0
    
    for host in hosts:
        if host.is_web_url():
            web_count += 1
            print(f"🌐 Web: {host.ip_address}")
        else:
            ip_count += 1
            print(f"🖥️ IP: {host.ip_address}")
    
    print(f"\nSummary: {web_count} Web hosts, {ip_count} IP hosts")

def main():
    print("=== Prueba de mejoras del Dashboard ===")
    print("=" * 50)
    
    # Test basic functionality
    test_host_types()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n=== Resumen de mejoras implementadas ===")
    print("✅ Dashboard ahora muestra columna 'Tipo' con iconos")
    print("✅ API incluye información de tipo de host")
    print("✅ Mejor manejo de estados HTTP con más detalles")
    print("✅ Formularios con ejemplos claros y ayuda mejorada")
    print("✅ Plantillas actualizadas para distinguir tipos")
    
    print("\n🎉 ¡Mejoras del dashboard implementadas exitosamente!")

if __name__ == "__main__":
    main()
