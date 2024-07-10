# Generated by Django 5.0.6 on 2024-07-10 16:58

import django_resized.forms
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('insurer', '0015_alter_insurerprofile_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='insurerprofile',
            name='profile_image',
            field=django_resized.forms.ResizedImageField(crop=None, default='profile_pic/default.png', force_format=None, keep_meta=True, quality=-1, scale=None, size=[400, 400], upload_to='profile_pic'),
        ),
    ]
