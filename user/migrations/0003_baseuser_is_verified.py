# Generated by Django 5.0.6 on 2024-06-07 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_baseuser_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
