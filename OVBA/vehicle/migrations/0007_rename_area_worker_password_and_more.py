# Generated by Django 5.0.3 on 2024-08-29 14:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0006_worker'),
    ]

    operations = [
        migrations.RenameField(
            model_name='worker',
            old_name='area',
            new_name='password',
        ),
        migrations.RenameField(
            model_name='worker',
            old_name='city',
            new_name='username',
        ),
    ]
