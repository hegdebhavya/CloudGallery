# Generated by Django 3.1 on 2022-10-01 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filemeta',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
