# Generated by Django 5.0.6 on 2024-06-26 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0004_agent_gampid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='gampID',
        ),
    ]
