# Generated by Django 5.0.6 on 2024-07-09 18:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurer', '0013_rename_unyte_unique_id_insurer_unyte_unique_insurer_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsurerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_image', models.ImageField(default='default.png', upload_to='profile_pic')),
                ('insurer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='insurer.insurer')),
            ],
        ),
    ]