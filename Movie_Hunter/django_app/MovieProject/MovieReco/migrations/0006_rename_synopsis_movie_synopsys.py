# Generated by Django 3.2.6 on 2021-08-18 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MovieReco', '0005_rename_distance_moviesynopsisdistance_distance_score'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='synopsis',
            new_name='synopsys',
        ),
    ]
