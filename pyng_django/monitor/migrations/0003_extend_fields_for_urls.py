# Generated manually for URL support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0002_hosts_port_alter_hosts_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hosts',
            name='ip_address',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='hosts',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='hosts',
            name='previous_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
