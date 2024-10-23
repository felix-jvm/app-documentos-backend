# Generated by Django 5.1 on 2024-09-13 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Anexos',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Num', models.IntegerField(blank=True, db_column='Num', null=True)),
                ('Nombre', models.CharField(blank=True, db_column='Nombre', max_length=50, null=True)),
                ('Codigo', models.CharField(blank=True, db_column='Codigo', max_length=50, null=True)),
                ('IDProcedimiento', models.IntegerField(blank=True, db_column='IDProcedimiento', null=True)),
            ],
            options={
                'db_table': 'Anexos',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DescripcionesProcedimiento',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.CharField(db_column='Codigo', max_length=50)),
                ('IDProcedimiento', models.IntegerField(db_column='IDProcedimiento')),
                ('Descripcion', models.TextField(db_column='Descripcion')),
            ],
            options={
                'db_table': 'DescripcionesProcedimiento',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Documentos',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.CharField(db_column='Codigo', max_length=50)),
                ('Descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=100, null=True)),
            ],
            options={
                'db_table': 'Documentos',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DocumentosReferencias',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('IDDocumento', models.IntegerField(blank=True, db_column='IDDocumento', null=True)),
                ('IDProcedimiento', models.IntegerField(blank=True, db_column='IDProcedimiento', null=True)),
            ],
            options={
                'db_table': 'DocumentosReferencias',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HistorialCambios',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Fecha', models.DateField(auto_now_add=True)),
                ('Version', models.DecimalField(blank=True, db_column='Version', decimal_places=2, max_digits=2, null=True)),
                ('Descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=500, null=True)),
                ('IDProcedimiento', models.IntegerField(blank=True, db_column='IDProcedimiento', null=True)),
            ],
            options={
                'db_table': 'HistorialCambios',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Procedimiento',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.CharField(db_column='Codigo', max_length=50)),
                ('Objetivo', models.TextField(db_column='Objetivo')),
                ('Alcance', models.TextField(db_column='Alcance')),
                ('Diagrama_Flujo', models.ImageField(blank=True, db_column='Diagrama_Flujo', null=True, upload_to='DIAGRAMA_FLUJO')),
            ],
            options={
                'db_table': 'Procedimiento',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Puestos',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Descripcion', models.CharField(db_column='Descripcion', max_length=50)),
                ('UnidadNegocio', models.IntegerField(blank=True, db_column='UnidadNegocio', null=True)),
                ('Actividad', models.IntegerField(blank=True, db_column='Actividad', null=True)),
            ],
            options={
                'db_table': 'Puestos',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Responsabilidades',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('IDProcedimiento', models.IntegerField(db_column='IDProcedimiento')),
                ('IDPuesto', models.IntegerField(db_column='IDPuesto')),
                ('Descripcion', models.CharField(db_column='Descripcion', max_length=500)),
            ],
            options={
                'db_table': 'Responsabilidades',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RevAprobacion',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('IDProcedimiento', models.IntegerField()),
                ('ElaboradoPor', models.CharField(blank=True, db_column='ElaboradoPor', max_length=50, null=True)),
                ('FirmaElaborado', models.CharField(blank=True, db_column='FirmaElaborado', max_length=50, null=True)),
                ('PuestoElaborado', models.CharField(blank=True, db_column='PuestoElaborado', max_length=50, null=True)),
                ('RevisadoPor', models.CharField(blank=True, db_column='RevisadoPor', max_length=50, null=True)),
                ('FirmaRevisado', models.CharField(blank=True, db_column='FirmaRevisado', max_length=50, null=True)),
                ('PuestoRevisado', models.CharField(blank=True, db_column='PuestoRevisado', max_length=50, null=True)),
                ('AprobadoPor', models.CharField(blank=True, db_column='AprobadoPor', max_length=50, null=True)),
                ('FirmaAprobado', models.CharField(blank=True, db_column='FirmaAprobado', max_length=50, null=True)),
                ('PuestoAprobado', models.CharField(blank=True, db_column='PuestoAprobado', max_length=50, null=True)),
            ],
            options={
                'db_table': 'RevAprobacion',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SubDescripciones',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Codigo', models.CharField(db_column='Codigo', max_length=50)),
                ('IDDescripcion', models.IntegerField(blank=True, db_column='IDDescripcion', null=True)),
                ('SubDescripcion', models.TextField(db_column='SubDescripcion')),
            ],
            options={
                'db_table': 'SubDescripciones',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Termino',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('Descripcion', models.CharField(db_column='Descripcion', max_length=50)),
                ('DescripcionGeneral', models.CharField(blank=True, db_column='DescripcionGeneral', max_length=500, null=True)),
            ],
            options={
                'db_table': 'Termino',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TerminologiasDef',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('IDProcedimiento', models.IntegerField(db_column='IDProcedimiento')),
                ('IDTermino', models.IntegerField(db_column='IDTermino')),
                ('Descripcion', models.CharField(db_column='Descripcion', max_length=500)),
            ],
            options={
                'db_table': 'TerminologiasDef',
                'managed': True,
            },
        ),
    ]