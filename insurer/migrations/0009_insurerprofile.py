# Generated by Django 5.0.6 on 2024-07-03 01:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurer', '0008_insurer_otp_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsurerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(default='default.png', upload_to='<django.db.models.fields.related.OneToOneField>/profile_pic')),
                ('insurer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='insurer.insurer')),
            ],
        ),
    ]