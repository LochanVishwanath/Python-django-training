# Generated by Django 2.2.4 on 2021-08-27 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dropship', '0002_auto_20210827_1456'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='status',
            field=models.CharField(choices=[('OPEN', 'OPEN'), ('INPROGRESS', 'INPROGRESS'), ('INREVIEW', 'INREVIEW'), ('QATESTING', 'QATESTING'), ('DONE', 'DONE')], default='OPEN', max_length=15),
        ),
    ]