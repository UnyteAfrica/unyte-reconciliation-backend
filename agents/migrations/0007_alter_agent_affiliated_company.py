# Generated by Django 5.0.6 on 2024-06-26 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0006_agent_agent_gampid'),
        ('insurer', '0006_insurer_insurer_gampid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='affiliated_company',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, to='insurer.insurer'),
        ),
    ]
