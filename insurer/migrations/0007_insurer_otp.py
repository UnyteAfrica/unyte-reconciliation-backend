# Generated by Django 5.0.6 on 2024-06-28 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurer', '0006_insurer_insurer_gampid'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurer',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
