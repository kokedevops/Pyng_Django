import platform
import socket
import subprocess
import time
import requests
import urllib.parse
from ipaddress import AddressValueError, ip_address as ip_address_validator

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

def poll_host_port(host_ip, port, timeout=5):
    '''Poll a specific port on a host via TCP socket'''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host_ip, port))
        sock.close()
        return '🟢 Up 🟢' if result == 0 else '🔴 Down 🔴'
    except Exception:
        return '🔴 Down 🔴'

def poll_host_smart(ip_address_full):
    '''
    Función inteligente que determina si hacer ping ICMP o verificación de puerto TCP
    - Si es solo IP: hace ping ICMP
    - Si es IP:Puerto: hace verificación TCP del puerto específico
    '''
    try:
        ip_only, port = validate_ip_port(ip_address_full)
        
        if port is not None:
            # Es IP:Puerto, verificar el puerto específico
            return poll_host_port(ip_only, port)
        else:
            # Es solo IP, hacer ping ICMP
            return poll_host_ip(ip_only)
            
    except ValueError:
        # Si hay error en la validación, asumir que está down
        return '🔴 Down 🔴'

def validate_ip_port(ip_str):
    """Valida una dirección IP con puerto opcional (formato: IP o IP:Puerto)"""
    # Verificar si es IPv6 (contiene :: o múltiples :)
    if '::' in ip_str or ip_str.count(':') > 1:
        # Para IPv6, solo validar la IP completa sin puerto por ahora
        try:
            ip_address_validator(ip_str)
            return ip_str, None
        except AddressValueError:
            raise ValueError(f"'{ip_str}' no es una dirección IPv6 válida")
    
    if ':' in ip_str:
        # Formato IP:Puerto para IPv4
        parts = ip_str.split(':')
        if len(parts) != 2:
            raise ValueError("Formato incorrecto. Use IP:Puerto")
        
        ip_part, port_part = parts
        
        # Validar IP
        try:
            ip_address_validator(ip_part)
        except AddressValueError:
            raise ValueError(f"'{ip_part}' no es una dirección IP válida")
        
        # Validar puerto
        try:
            port = int(port_part)
            if not (1 <= port <= 65535):
                raise ValueError(f"Puerto {port} fuera de rango (1-65535)")
        except ValueError:
            raise ValueError(f"'{port_part}' no es un puerto válido")
        
        return ip_part, port
    else:
        # Solo IP
        try:
            ip_address_validator(ip_str)
            return ip_str, None
        except AddressValueError:
            raise ValueError(f"'{ip_str}' no es una dirección IP válida")

def poll_web_url(url, timeout=10):
    '''Poll a web URL (HTTP/HTTPS) to check if it responds'''
    try:
        # Asegurar que la URL tenga protocolo
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        
        # Considerar exitoso si el código de estado es 2xx o 3xx
        if 200 <= response.status_code < 400:
            return '🟢 Up 🟢'
        else:
            return f'🔴 Down 🔴 (HTTP {response.status_code})'
            
    except requests.exceptions.Timeout:
        return '🔴 Down 🔴 (Timeout)'
    except requests.exceptions.ConnectionError:
        return '🔴 Down 🔴 (Connection Error)'
    except requests.exceptions.RequestException as e:
        return f'🔴 Down 🔴 (Error: {str(e)[:50]})'
    except Exception as e:
        return f'🔴 Down 🔴 (Error: {str(e)[:50]})'

def is_web_url(address):
    '''Determina si una dirección es una URL web'''
    # Verificar si contiene protocolo web
    if address.startswith(('http://', 'https://')):
        return True
    
    # Verificar si parece ser un dominio/URL sin protocolo
    if '.' in address and not address.replace('.', '').replace(':', '').isdigit():
        # No es una IP, probablemente es un dominio
        try:
            # Intentar validar como IP, si falla es probablemente un dominio
            ip_address_validator(address.split(':')[0])
            return False  # Es una IP válida
        except (AddressValueError, ValueError):
            return True  # No es IP válida, probablemente es dominio
    
    return False

def validate_web_or_ip(address):
    """Valida una dirección que puede ser IP, IP:Puerto, o URL web"""
    address = address.strip()
    
    if is_web_url(address):
        # Es una URL web, validar formato básico
        try:
            if not address.startswith(('http://', 'https://')):
                test_url = 'https://' + address
            else:
                test_url = address
            
            parsed = urllib.parse.urlparse(test_url)
            if parsed.netloc:
                return address, 'web'
            else:
                raise ValueError(f"'{address}' no es una URL válida")
        except Exception:
            raise ValueError(f"'{address}' no es una URL válida")
    else:
        # Es IP o IP:Puerto, usar validación existente
        ip_only, port = validate_ip_port(address)
        return address, 'ip'

def poll_host_universal(address):
    '''
    Función universal que puede monitorear:
    - IPs (ping ICMP)
    - IP:Puerto (verificación TCP)  
    - URLs web HTTP/HTTPS
    '''
    try:
        validated_address, address_type = validate_web_or_ip(address)
        
        if address_type == 'web':
            return poll_web_url(validated_address)
        else:
            return poll_host_smart(validated_address)
            
    except ValueError:
        return '🔴 Down 🔴 (Invalid Address)'