# Generated by Django 5.0.6 on 2024-10-07 10:00

import django.db.models.deletion
import django_resized.forms
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('insurer', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('otp', models.CharField(blank=True, max_length=6, null=True, unique=True)),
                ('otp_created_at', models.TimeField(blank=True, null=True)),
                ('home_address', models.CharField(help_text='Agent home address', max_length=255, unique=True)),
                ('bvn', models.CharField(help_text='Agent BVN', max_length=11, unique=True)),
                ('bank_account', models.CharField(help_text='Agent Bank account', max_length=10, unique=True)),
                ('unyte_unique_agent_id', models.CharField(max_length=70, unique=True)),
                ('agent_gampID', models.CharField(blank=True, help_text='GAMP ID for users associated with GAMP', null=True)),
                ('affiliated_company', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='insurer.insurer')),
            ],
            options={
                'abstract': False,
            },
            bases=('user.customuser',),
        ),
        migrations.CreateModel(
            name='AgentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', django_resized.forms.ResizedImageField(crop=None, default='profile_pic/default.png', force_format=None, keep_meta=True, quality=-1, scale=None, size=[400, 400], upload_to='profile_pic')),
                ('agent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='agents.agent')),
            ],
        ),
    ]
