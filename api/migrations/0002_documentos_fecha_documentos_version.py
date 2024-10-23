# Generated by Django 5.1 on 2024-10-10 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentos',
            name='Fecha',
            field=models.DateField(auto_now_add=True, db_column='Fecha', null=True),
        ),
        migrations.AddField(
            model_name='documentos',
            name='Version',
            field=models.DecimalField(blank=True, db_column='Version', decimal_places=4, default=False, max_digits=6, null=True),
        ),
    ]