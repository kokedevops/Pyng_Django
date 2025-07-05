from django.http import JsonResponse
from .models import Hosts, PollHistory, HostAlerts


def get_all_hosts(request):
    """Get all hosts with type information"""
    hosts = []
    for host in Hosts.objects.all():
        host_type = "🌐 Web" if host.is_web_url() else "🖥️ IP"
        hosts.append({
            'id': host.id,
            'hostname': host.hostname,
            'ip_address': host.ip_address,
            'host_type': host_type,
            'last_poll': host.last_poll,
            'status': host.status
        })
    return JsonResponse({'data': hosts})


def get_host_counts(request):
    """Get host total, available, unavailable host counts"""
    total = Hosts.objects.count()
    # Count hosts that are up (status starts with green circle)
    num_up = Hosts.objects.filter(status__startswith='🟢').count()
    # Count hosts that are down (status starts with red circle)
    num_down = Hosts.objects.filter(status__startswith='🔴').count()
    data = {'total_hosts': total, 'available_hosts': num_up, 'unavailable_hosts': num_down}
    return JsonResponse(data)


def get_all_host_alerts(request):
    """Get all host alerts"""
    alerts = list(HostAlerts.objects.all().values('hostname', 'ip_address', 'poll_time', 'host_status'))
    return JsonResponse({'data': alerts})


def get_poll_history(request, host_id):
    """Get poll history for a single host"""
    history = list(PollHistory.objects.filter(host_id=host_id).values('poll_time', 'poll_status'))
    return JsonResponse({'data': history})