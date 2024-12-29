# Generated by Django 5.1 on 2024-12-29 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_documentos_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermisoNivel',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Nivel', models.IntegerField(db_column='Nivel')),
                ('Descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=100, null=True)),
            ],
            options={
                'db_table': 'PermisoNivel',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Nombre', models.CharField(db_column='Nombre', max_length=50)),
                ('Contrasena', models.BinaryField(db_column='Contrasena')),
                ('Activo', models.BooleanField(db_column='Activo', default=True)),
                ('PermisoNivel', models.IntegerField(db_column='PermisoNivel')),
            ],
            options={
                'db_table': 'Usuario',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UsuarioCodigo',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.CharField(db_column='Codigo', max_length=100)),
            ],
            options={
                'db_table': 'UsuarioCodigo',
                'managed': True,
            },
        ),
        migrations.AlterField(
            model_name='procedimiento',
            name='Diagrama_Flujo',
            field=models.BinaryField(blank=True, db_column='Diagrama_Flujo', null=True),
        ),
    ]