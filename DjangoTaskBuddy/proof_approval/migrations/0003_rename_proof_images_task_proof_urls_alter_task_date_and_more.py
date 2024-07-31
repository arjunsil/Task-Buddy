# Generated by Django 5.0.7 on 2024-07-31 03:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proof_approval', '0002_proofimage'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='proof_images',
            new_name='proof_urls',
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateField(default=datetime.datetime(2024, 7, 31, 3, 25, 45, 141557, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='task',
            name='time',
            field=models.TimeField(default=datetime.datetime(2024, 7, 31, 3, 25, 45, 141775, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='ProofImage',
        ),
    ]