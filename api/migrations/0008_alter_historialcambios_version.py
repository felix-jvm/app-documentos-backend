# Generated by Django 5.1 on 2024-10-16 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_procedimiento_diagrama_flujo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historialcambios',
            name='Version',
            field=models.CharField(blank=True, db_column='Version', max_length=500, null=True),
        ),
    ]
