# Generated by Django 5.0.6 on 2024-06-28 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurer', '0007_insurer_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurer',
            name='otp_created_at',
            field=models.TimeField(blank=True, null=True),
        ),
    ]