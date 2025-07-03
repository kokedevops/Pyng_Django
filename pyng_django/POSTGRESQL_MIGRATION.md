# Migración a PostgreSQL - PYNG

Este documento explica cómo migrar la aplicación PYNG de SQLite a PostgreSQL.

## Requisitos previos

1. **PostgreSQL instalado**: Descargar desde https://www.postgresql.org/download/
2. **Base de datos creada**: Crear una base de datos llamada `pyng_db` (o el nombre que prefieras)

## Pasos para la migración

### 1. Instalar PostgreSQL

Si no tienes PostgreSQL instalado:

**Windows:**
- Descargar desde: https://www.postgresql.org/download/windows/
- Durante la instalación, recordar la contraseña del usuario `postgres`

**Crear la base de datos:**
```sql
-- Conectar como usuario postgres
CREATE DATABASE pyng_db;
CREATE USER pyng_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE pyng_db TO pyng_user;
```

### 2. Configurar variables de entorno

Ejecutar el script de configuración:
```bash
python setup_postgresql.py
```

Este script:
- Creará un archivo `.env` con la configuración de la base de datos
- Verificará la conexión a PostgreSQL
- Ejecutará las migraciones iniciales

### 3. Migrar datos existentes (opcional)

Si tienes datos en SQLite que quieres conservar:
```bash
python migrate_data.py
```

Este script:
- Exportará los datos de SQLite
- Los importará a PostgreSQL
- Conservará usuarios, hosts, configuraciones, etc.

### 4. Ejecutar la aplicación

```bash
python manage.py runserver
```

## Configuración del archivo .env

El archivo `.env` debe contener:

```env
# Configuración de la base de datos PostgreSQL
DB_NAME=pyng_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Configuración de desarrollo
DEBUG=True
```

## Verificar la migración

1. **Conexión a la base de datos:**
   ```bash
   python manage.py dbshell
   ```

2. **Ver tablas creadas:**
   ```sql
   \dt
   ```

3. **Verificar datos:**
   ```sql
   SELECT COUNT(*) FROM monitor_hosts;
   ```

## Solución de problemas

### Error de conexión
- Verificar que PostgreSQL esté ejecutándose
- Comprobar credenciales en `.env`
- Verificar que la base de datos existe

### Error de permisos
```sql
GRANT ALL PRIVILEGES ON DATABASE pyng_db TO tu_usuario;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tu_usuario;
```

### Resetear migraciones (si es necesario)
```bash
python manage.py migrate monitor zero
python manage.py makemigrations
python manage.py migrate
```

## Ventajas de PostgreSQL

- **Mejor rendimiento** para consultas complejas
- **Soporte para concurrencia** múltiple
- **Tipos de datos avanzados**
- **Mejor escalabilidad**
- **Funciones y triggers**
- **Replicación y backup**

## Backup y restauración

### Crear backup
```bash
pg_dump -U postgres pyng_db > backup.sql
```

### Restaurar backup
```bash
psql -U postgres pyng_db < backup.sql
```
