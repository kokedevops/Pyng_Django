from django.http import JsonResponse
from .models import Hosts, PollHistory, HostAlerts


def get_all_hosts(request):
    """Get all hosts"""
    hosts = list(Hosts.objects.values('id', 'hostname', 'ip_address', 'last_poll', 'status'))
    return JsonResponse({'data': hosts})


def get_host_counts(request):
    """Get host total, available, unavailable host counts"""
    total = Hosts.objects.count()
    num_up = Hosts.objects.filter(status='🟢 Up 🟢').count()
    num_down = Hosts.objects.filter(status='🔴 Down 🔴').count()
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