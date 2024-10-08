# Generated by Django 5.0.3 on 2024-08-31 12:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0007_rename_area_worker_password_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to='certificates/')),
                ('shop', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='vehicle.shopdetails')),
            ],
        ),
    ]
