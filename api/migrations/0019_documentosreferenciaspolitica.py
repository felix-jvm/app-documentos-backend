# Generated by Django 5.1 on 2025-04-12 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_anexopolitica_boundproveedorespolitica_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentosReferenciasPolitica',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('IDDocumento', models.IntegerField(blank=True, db_column='IDDocumento', null=True)),
                ('Politica', models.IntegerField(blank=True, db_column='IDProcedimiento', null=True)),
            ],
            options={
                'db_table': 'DocumentosReferenciasPolitica',
                'managed': True,
            },
        ),
    ]
