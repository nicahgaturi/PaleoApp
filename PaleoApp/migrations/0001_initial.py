# Generated by Django 5.2.4 on 2025-07-09 16:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shelf_number', models.CharField(blank=True, default='N/A', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AccessionNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(unique=True)),
                ('date_time_accessioned', models.DateTimeField(auto_now_add=True)),
                ('type_status', models.CharField(blank=True, choices=[('Type', 'Type'), ('Holotype', 'Holotype'), ('Isotype', 'Isotype'), ('Lectotype', 'Lectotype'), ('Syntype', 'Syntype'), ('Isosyntype', 'Isosyntype'), ('Paratype', 'Paratype'), ('Neotype', 'Neotype'), ('Topotype', 'Topotype')], help_text='Please select the type status', max_length=50, null=True)),
                ('comment', models.TextField(blank=True, help_text='Any additional comments', null=True)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PaleoApp.collection')),
                ('locality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PaleoApp.locality')),
                ('storage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='PaleoApp.storage')),
            ],
        ),
    ]
