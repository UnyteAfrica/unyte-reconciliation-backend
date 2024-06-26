# Generated by Django 5.0.6 on 2024-06-26 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_customuser_gampid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='gampID',
            field=models.CharField(blank=True, help_text='GAMP ID for users associated with GAMP', null=True, unique=True),
        ),
    ]