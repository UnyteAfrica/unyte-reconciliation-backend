# Generated by Django 5.0.6 on 2024-07-09 15:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurer', '0011_insurer_policies'),
    ]

    operations = [
        migrations.AddField(
            model_name='insurer',
            name='unyte_unique_id',
            field=models.CharField(default=datetime.datetime(2024, 7, 9, 15, 41, 28, 933789, tzinfo=datetime.timezone.utc), max_length=70, unique=True),
            preserve_default=False,
        ),
    ]
