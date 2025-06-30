from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import api_views

app_name = 'monitor'

urlpatterns = [
    # Vistas principales
    path('', views.index, name='index'),
    path('setup/', views.setup_view, name='setup'),
    path('account/', views.account, name='account'),
    path('setTheme/', views.set_theme, name='set_theme'),
    path('configurePolling/', views.configure_polling, name='configure_polling'),

    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('updatePassword/', views.update_password, name='update_password'),
    path('updateEmail/', views.update_email, name='update_email'),

    # Hosts
    path('addHosts/', views.add_hosts, name='add_hosts'),
    path('updateHosts/', views.update_hosts, name='update_hosts'),
    path('deleteHost/', views.delete_host, name='delete_host'),

    # SMTP
    path('configureSMTP/', views.configure_smtp, name='configure_smtp'),
    path('smtpTest/', views.smtp_test, name='smtp_test'),

    # API
    path('api/hosts', api_views.get_all_hosts, name='api_get_all_hosts'),
    path('api/host_counts', api_views.get_host_counts, name='api_get_host_counts'),
    path('api/host_alerts', api_views.get_all_host_alerts, name='api_get_all_host_alerts'),
    path('pollHistory/<int:host_id>/', api_views.get_poll_history, name='api_get_poll_history'),
]

