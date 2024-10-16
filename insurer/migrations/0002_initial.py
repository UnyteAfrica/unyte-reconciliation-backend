# Generated by Django 5.0.6 on 2024-10-09 10:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("insurer", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="insurer",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="insurerprofile",
            name="insurer",
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="insurer.insurer"),
        ),
    ]
