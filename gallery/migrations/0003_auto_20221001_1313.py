# Generated by Django 3.1 on 2022-10-01 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_auto_20221001_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filemeta',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
    ]
