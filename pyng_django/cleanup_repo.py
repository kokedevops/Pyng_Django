#!/usr/bin/env python3
"""
Script para limpiar y organizar el repositorio PYNG
Elimina archivos innecesarios y reorganiza la estructura
"""
import os
import shutil
from pathlib import Path

def main():
    print("🧹 LIMPIEZA Y ORGANIZACIÓN DEL REPOSITORIO PYNG")
    print("=" * 60)
    
    project_root = Path("c:/PYNG-PROYECTO/pyng_django")
    
    # Archivos de prueba que se pueden eliminar
    test_files = [
        "test_add_host.py",
        "test_dashboard_improvements.py", 
        "test_form.py",
        "test_smart_monitoring.py",
        "test_validation.py",
        "test_add_website.py",
        "test_web_monitoring.py",
        "test_delete.py",
        "check_data.py",
        "check_hosts.py",
        "improve_dashboard.py"
    ]
    
    # Archivos temporales y de desarrollo
    temp_files = [
        "pyng.sqlite",  # Base de datos SQLite antigua
        ".monitoring_pid",
        ".pyng_main_pid", 
        ".web_pid",
        "check_themes.py",
        "fix_themes.py"
    ]
    
    # Archivos duplicados o innecesarios en monitor/
    monitor_cleanup = [
        "from django import forms.py",  # Archivo mal nombrado
        "from django.py",  # Archivo mal nombrado
        "tests.py"  # Archivo Django por defecto vacío
    ]
    
    # Directorios temporales
    temp_dirs = [
        "templates/database",  # Contiene bases de datos SQLite viejas
        "__pycache__",
        "monitor/__pycache__",
        "pyng_django/__pycache__"
    ]
    
    print("📁 Eliminando archivos de prueba...")
    for file_name in test_files:
        file_path = project_root / file_name
        if file_path.exists():
            file_path.unlink()
            print(f"  ✅ Eliminado: {file_name}")
    
    print("\n🗑️ Eliminando archivos temporales...")
    for file_name in temp_files:
        file_path = project_root / file_name
        if file_path.exists():
            file_path.unlink()
            print(f"  ✅ Eliminado: {file_name}")
    
    print("\n🧼 Limpiando directorio monitor/...")
    monitor_dir = project_root / "monitor"
    for file_name in monitor_cleanup:
        file_path = monitor_dir / file_name
        if file_path.exists():
            file_path.unlink()
            print(f"  ✅ Eliminado: monitor/{file_name}")
    
    print("\n📂 Eliminando directorios temporales...")
    for dir_name in temp_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)
            print(f"  ✅ Eliminado: {dir_name}/")
    
    # Crear directorio docs/ y mover documentación
    print("\n📚 Organizando documentación...")
    docs_dir = project_root / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    doc_files = ["POSTGRESQL_MIGRATION.md"]
    for doc_file in doc_files:
        src = project_root / doc_file
        dst = docs_dir / doc_file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"  ✅ Movido: {doc_file} -> docs/")
    
    # Crear directorio scripts/ y mover scripts de administración
    print("\n🔧 Organizando scripts...")
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    admin_scripts = [
        "admin.py",
        "migrate_data.py", 
        "setup_postgresql.py"
    ]
    
    for script_file in admin_scripts:
        src = project_root / script_file
        dst = scripts_dir / script_file
        if src.exists():
            shutil.move(str(src), str(dst))
            print(f"  ✅ Movido: {script_file} -> scripts/")
    
    # Consolidar launchers
    print("\n🚀 Organizando launchers...")
    launcher_files = ["pyng_launcher.py", "start_monitoring.py"]
    for launcher_file in launcher_files:
        launcher_path = project_root / launcher_file
        if launcher_path.exists():
            launcher_path.unlink()
            print(f"  ✅ Eliminado: {launcher_file} (usar launch_pyng.py)")
    
    print("\n✅ LIMPIEZA COMPLETADA")
    print("\n📋 ESTRUCTURA FINAL RECOMENDADA:")
    print("pyng_django/")
    print("├── docs/                    # Documentación")
    print("├── scripts/                 # Scripts de administración")
    print("├── monitor/                 # Aplicación Django principal")
    print("├── pyng_django/            # Configuración Django")
    print("├── static/                 # Archivos estáticos")
    print("├── templates/              # Templates HTML")
    print("├── requirements.txt        # Dependencias")
    print("├── manage.py              # Comando Django")
    print("├── launch_pyng.py         # Launcher principal")
    print("├── start_pyng.py          # Launcher con servicios")
    print("└── .env                   # Configuración")
    
    print("\n🎯 ARCHIVOS PRINCIPALES MANTENIDOS:")
    print("✅ manage.py - Comando principal de Django")
    print("✅ launch_pyng.py - Launcher simple")
    print("✅ start_pyng.py - Launcher con servicios completos")
    print("✅ requirements.txt - Dependencias")
    print("✅ .env - Configuración de base de datos")
    
    print("\n🔥 SIGUIENTES PASOS:")
    print("1. Revisar que todo funcione: python manage.py runserver")
    print("2. Usar launch_pyng.py para inicio simple")
    print("3. Usar start_pyng.py para inicio con monitoreo")
    print("4. Los scripts de admin están en scripts/")

if __name__ == "__main__":
    main()
