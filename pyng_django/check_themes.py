#!/usr/bin/env python
"""
Script para verificar y configurar temas por defecto
"""
import os
import sys
import django

# Setup Django
sys.path.append('C:\\NEWPYNG\\pyng\\pyng_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.models import WebThemes

def check_themes():
    print("Verificando temas existentes...")
    themes = WebThemes.objects.all()
    
    if themes.exists():
        print(f"Se encontraron {themes.count()} temas:")
        for theme in themes:
            print(f"  - ID: {theme.id}, Nombre: {theme.theme_name}, Ruta: {theme.theme_path}, Activo: {theme.active}")
    else:
        print("No se encontraron temas. Creando temas por defecto...")
        create_default_themes()
    
    # También verificar el tema activo actual
    active_theme = WebThemes.objects.filter(active=True).first()
    if active_theme:
        print(f"\nTema activo actual: {active_theme.theme_name} -> {active_theme.theme_path}")
    else:
        print("\n¡ADVERTENCIA! No hay ningún tema marcado como activo.")

def create_default_themes():
    """Crear algunos temas por defecto basados en los CSS que veo en static"""
    default_themes = [
        {'theme_name': 'Flatly (Claro)', 'theme_path': 'css/flatly.min.css', 'active': True},
        {'theme_name': 'Darkly (Oscuro)', 'theme_path': 'css/darkly.min.css', 'active': False},
    ]
    
    for theme_data in default_themes:
        theme, created = WebThemes.objects.get_or_create(
            theme_name=theme_data['theme_name'],
            defaults=theme_data
        )
        if created:
            print(f"Tema creado: {theme.theme_name}")
        else:
            print(f"Tema ya existe: {theme.theme_name}")

if __name__ == '__main__':
    check_themes()
