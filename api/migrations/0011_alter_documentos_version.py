# Generated by Django 5.1 on 2024-10-17 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_departamento_tipodocumento_documentos_iddepartamento_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentos',
            name='Version',
            field=models.CharField(blank=True, db_column='Version', max_length=500, null=True),
        ),
    ]
