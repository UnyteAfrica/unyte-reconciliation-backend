# Generated by Django 5.0.6 on 2024-06-26 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_customuser_gampid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='gampID',
        ),
    ]