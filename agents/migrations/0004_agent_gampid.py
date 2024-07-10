# Generated by Django 5.0.6 on 2024-06-26 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0003_alter_agent_affiliated_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='gampID',
            field=models.CharField(blank=True, help_text='GAMP ID for users associated with GAMP', null=True),
        ),
    ]
