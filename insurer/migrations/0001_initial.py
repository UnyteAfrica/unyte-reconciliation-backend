# Generated by Django 5.0.6 on 2024-10-16 13:03

import django.db.models.deletion
import django_resized.forms
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Insurer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(help_text='Business name of insurer', max_length=50, unique=True)),
                ('admin_name', models.CharField(help_text='Contact name of admin of insurer account', max_length=20)),
                ('business_registration_number', models.CharField(help_text='Business registration number of Tax ID of insurer', max_length=50, unique=True)),
                ('insurer_gamp_id', models.CharField(blank=True, default='', help_text='GAMP ID for users associated with GAMP')),
                ('unyte_unique_insurer_id', models.CharField(max_length=70, unique=True)),
                ('otp', models.CharField(blank=True, max_length=6, null=True, unique=True)),
                ('otp_created_at', models.TimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'INSURER',
                'verbose_name_plural': 'INSURERS',
            },
        ),
        migrations.CreateModel(
            name='InsurerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', django_resized.forms.ResizedImageField(crop=None, default='profile_pic/default.png', force_format=None, keep_meta=True, quality=-1, scale=None, size=[400, 400], upload_to='profile_pic')),
                ('insurer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='insurer.insurer')),
            ],
            options={
                'verbose_name': 'INSURER PROFILE',
                'verbose_name_plural': 'INSURER PROFILES',
            },
        ),
    ]
