# Generated by Django 5.0.6 on 2024-08-15 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policies', '0009_policies_insurer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agentpolicy',
            old_name='quantity',
            new_name='quantity_bought',
        ),
        migrations.AddField(
            model_name='agentpolicy',
            name='quantity_sold',
            field=models.IntegerField(default=1),
        ),
    ]