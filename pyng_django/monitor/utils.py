import platform
import socket
import subprocess
import time

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