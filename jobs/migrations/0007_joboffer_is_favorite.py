# Generated by Django 5.2 on 2025-04-21 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_alter_joboffer_publication_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='is_favorite',
            field=models.BooleanField(default=False, verbose_name='Oferta favorita'),
        ),
    ]
