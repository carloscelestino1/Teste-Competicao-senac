# Generated by Django 5.2.3 on 2025-07-20 15:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_eventadress_event_id_eventadress_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='Seat_id',
        ),
        migrations.DeleteModel(
            name='Seat',
        ),
    ]
