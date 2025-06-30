#!/usr/bin/env python
"""
Script para corregir la ruta del tema Flatly
"""
import os
import sys
import django

# Setup Django
sys.path.append('C:\\NEWPYNG\\pyng\\pyng_django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.models import WebThemes

def fix_theme_paths():
    print("Corrigiendo rutas de temas...")
    
    # Corregir el tema Flatly
    flatly_theme = WebThemes.objects.filter(theme_name__icontains='Flatly').first()
    if flatly_theme:
        old_path = flatly_theme.theme_path
        flatly_theme.theme_path = 'css/flatly.min.css'
        flatly_theme.save()
        print(f"Tema Flatly corregido: {old_path} -> {flatly_theme.theme_path}")
    
    # Verificar que el tema Darkly también tenga la ruta correcta
    darkly_theme = WebThemes.objects.filter(theme_name__icontains='Darkly').first()
    if darkly_theme:
        if darkly_theme.theme_path != 'css/darkly.min.css':
            darkly_theme.theme_path = 'css/darkly.min.css'
            darkly_theme.save()
            print(f"Tema Darkly corregido: -> {darkly_theme.theme_path}")
        else:
            print(f"Tema Darkly ya tiene la ruta correcta: {darkly_theme.theme_path}")

if __name__ == '__main__':
    fix_theme_paths()
