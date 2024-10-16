# Generated by Django 5.0.6 on 2024-10-09 10:24

import django_resized.forms
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Insurer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business_name', models.CharField(help_text='Business name of insurer', max_length=50, unique=True)),
                ('admin_name', models.CharField(help_text='Contact name of admin of insurer account', max_length=20)),
                (
                    'business_registration_number',
                    models.CharField(
                        help_text='Business registration number of Tax ID of insurer', max_length=50, unique=True
                    ),
                ),
                (
                    'insurer_gamp_id',
                    models.CharField(blank=True, help_text='GAMP ID for users associated with GAMP', null=True),
                ),
                ('unyte_unique_insurer_id', models.CharField(max_length=70, unique=True)),
                ('otp', models.CharField(blank=True, max_length=6, null=True, unique=True)),
                ('otp_created_at', models.TimeField(blank=True, null=True)),
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
                (
                    'profile_image',
                    django_resized.forms.ResizedImageField(
                        crop=None,
                        default='profile_pic/default.png',
                        force_format=None,
                        keep_meta=True,
                        quality=-1,
                        scale=None,
                        size=[400, 400],
                        upload_to='profile_pic',
                    ),
                ),
            ],
            options={
                'verbose_name': 'INSURER PROFILE',
                'verbose_name_plural': 'INSURER PROFILES',
            },
        ),
    ]
