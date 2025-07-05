# PYNG - Sistema de Monitoreo de Red

PYNG es un sistema de monitoreo de red desarrollado en Django que permite supervisar hosts IP, servicios TCP y sitios web HTTP/HTTPS en tiempo real.

## 🚀 Características

- **Monitoreo Universal**: Soporta IPs (192.168.1.1), IP:Puerto (192.168.1.1:8080) y URLs web (https://ejemplo.com)
- **Dashboard en Tiempo Real**: Visualización actualizada automáticamente del estado de hosts
- **Historial de Monitoreo**: Registro completo de cambios de estado
- **Sistema de Alertas**: Notificaciones por cambios de estado
- **Gestión de Usuarios**: Sistema completo de usuarios y permisos
- **Base de Datos PostgreSQL**: Configuración robusta para producción
- **API REST**: Endpoints para integración con otros sistemas

## 📋 Requisitos

- Python 3.8+
- PostgreSQL 12+
- Git

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd pyng_django
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar PostgreSQL
```bash
python scripts/setup_postgresql.py
```

### 5. Ejecutar migraciones
```bash
python manage.py migrate
```

### 6. Crear usuario administrador
```bash
python scripts/admin.py create-admin
```

### 7. Iniciar la aplicación
```bash
# Opción 1: Solo servidor web
python manage.py runserver

# Opción 2: Servidor web + monitoreo automático
python start_pyng.py

# Opción 3: Launcher simple
python launch_pyng.py
```

## 🔧 Configuración

### Variables de Entorno (.env)
```bash
DB_NAME=pyng_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
```

### Configuración de Monitoreo
- **Intervalo de monitoreo**: Configurable desde la interfaz web
- **Retención de historial**: Configurable (días)
- **Notificaciones SMTP**: Opcional

## 📱 Uso

### Acceso Web
- URL: http://localhost:8000
- Usuario: admin (creado durante la instalación)

### Agregar Hosts
La aplicación soporta tres tipos de monitoreo:

1. **IPs**: `192.168.1.1, 8.8.8.8`
2. **IP:Puerto**: `192.168.1.1:8080, 127.0.0.1:3000`
3. **URLs Web**: `https://google.com, devopsdayschile.cl`

### Dashboard
- **🖥️ IP**: Monitoreo ICMP ping
- **🌐 Web**: Monitoreo HTTP/HTTPS
- **Tiempo Real**: Actualización automática cada 60 segundos

## 🛠️ Scripts de Administración

### scripts/admin.py
```bash
# Crear usuario administrador
python scripts/admin.py create-admin

# Listar usuarios
python scripts/admin.py list-users

# Estado del sistema
python scripts/admin.py status

# Iniciar servicios
python scripts/admin.py start-all

# Detener servicios
python scripts/admin.py stop-all
```

### scripts/setup_postgresql.py
```bash
# Configuración inicial de PostgreSQL
python scripts/setup_postgresql.py
```

### scripts/migrate_data.py
```bash
# Migrar datos desde SQLite (si aplica)
python scripts/migrate_data.py
```

## 📁 Estructura del Proyecto

```
pyng_django/
├── docs/                    # Documentación
│   └── POSTGRESQL_MIGRATION.md
├── scripts/                 # Scripts de administración
│   ├── admin.py
│   ├── setup_postgresql.py
│   └── migrate_data.py
├── monitor/                 # Aplicación Django principal
│   ├── management/commands/ # Comandos personalizados
│   ├── migrations/         # Migraciones de BD
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas web
│   ├── api_views.py       # API REST
│   ├── forms.py           # Formularios
│   ├── utils.py           # Utilidades de monitoreo
│   └── urls.py            # URLs
├── pyng_django/           # Configuración Django
│   ├── settings.py        # Configuración principal
│   └── urls.py            # URLs principales
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── templates/             # Templates HTML
├── requirements.txt       # Dependencias Python
├── manage.py             # Comando Django
├── launch_pyng.py        # Launcher simple
├── start_pyng.py         # Launcher con servicios
└── .env                  # Configuración de entorno
```

## 🔄 API REST

### Endpoints Disponibles
- `GET /api/hosts` - Lista todos los hosts
- `GET /api/host-counts` - Contadores de hosts
- `GET /api/host-alerts` - Alertas activas
- `GET /pollHistory/{id}/` - Historial de un host

### Ejemplo de Respuesta
```json
{
  "data": [
    {
      "id": 1,
      "hostname": "Google DNS",
      "ip_address": "8.8.8.8",
      "host_type": "🖥️ IP",
      "status": "🟢 Up 🟢",
      "last_poll": "2025-07-05 10:30:00"
    }
  ]
}
```

## 🚨 Monitoreo Automático

El sistema incluye un servicio de monitoreo que se ejecuta en segundo plano:

```bash
# Comando Django personalizado
python manage.py poll_hosts

# Comando con intervalo personalizado
python manage.py start_monitoring --interval 30

# Ejecutar una sola vez
python manage.py start_monitoring --once
```

## 🐛 Solución de Problemas

### Base de Datos
```bash
# Verificar conexión
python scripts/admin.py test-connection

# Reset completo (¡CUIDADO!)
python scripts/admin.py reset-database
```

### Servicios
```bash
# Estado de servicios
python scripts/admin.py monitoring-status

# Reiniciar monitoreo
python scripts/admin.py stop-monitoring
python scripts/admin.py start-monitoring
```

## 📈 Métricas y Estadísticas

- **Dashboard Principal**: Vista general con contadores
- **Historial Detallado**: Por host individual
- **Alertas**: Sistema de notificaciones por cambios de estado
- **Exportación**: Datos disponibles vía API

## 🔒 Seguridad

- Autenticación Django incorporada
- Sesiones seguras
- Configuración de producción lista
- Variables de entorno para credenciales

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- Basado en el proyecto original PYNG
- Migrado a Django con PostgreSQL
- Mejorado con monitoreo web HTTP/HTTPS
- Dashboard moderno con Bulma CSS
