# Generated by Django 5.0.6 on 2024-06-07 15:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agents', '0001_initial'),
        ('insurer', '0001_initial'),
        ('policies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='insurance_company',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='insurer.insurer'),
        ),
        migrations.AddField(
            model_name='agent',
            name='policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='policies.policies'),
        ),
    ]