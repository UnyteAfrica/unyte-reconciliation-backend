# Generated by Django 5.0.6 on 2024-08-24 10:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamp_env', '0004_remove_gamparbitraryproduct_product_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gamparbitraryproduct',
            name='policy',
        ),
        migrations.AddField(
            model_name='gamparbitrarypolicy',
            name='product_type',
            field=models.ForeignKey(default=1, help_text='The product attached to a policy', on_delete=django.db.models.deletion.CASCADE, to='gamp_env.gamparbitraryproduct'),
            preserve_default=False,
        ),
    ]
