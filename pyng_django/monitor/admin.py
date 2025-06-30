from django.contrib import admin
from .models import Profile, Hosts, PollHistory, HostAlerts, Polling, SmtpServer, WebThemes

# Register your models here.
admin.site.register(Profile)
admin.site.register(Hosts)
admin.site.register(PollHistory)
admin.site.register(HostAlerts)
admin.site.register(Polling)
admin.site.register(SmtpServer)
admin.site.register(WebThemes)

