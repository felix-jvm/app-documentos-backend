# Generated by Django 5.1 on 2024-10-16 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_historialcambios_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='procedimiento',
            name='deleted',
            field=models.BooleanField(blank=True, db_column='deleted', default=False, null=True),
        ),
    ]