# Generated by Django 5.1 on 2025-05-02 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_instructivo_instructivoanexo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='clasificaciontipomaterialpolitica',
            name='TipoPolitica',
            field=models.BinaryField(blank=True, db_column='TipoPolitica', null=True),
        ),
    ]
