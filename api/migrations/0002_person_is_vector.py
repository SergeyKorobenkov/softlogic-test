# Generated by Django 3.1.2 on 2020-10-22 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='is_vector',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
