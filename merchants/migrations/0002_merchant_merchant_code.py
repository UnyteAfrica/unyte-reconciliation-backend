# Generated by Django 5.0.6 on 2024-12-19 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='merchant_code',
            field=models.CharField(default='MER-123', help_text='Agent merchant code for merchant representation on superpool', max_length=10),
        ),
    ]
