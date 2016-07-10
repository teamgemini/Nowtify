# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NowtifyWeb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wearable_Usage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('used', models.BooleanField(default=False)),
                ('updated', models.DateTimeField()),
                ('wearable_name', models.ForeignKey(to='NowtifyWeb.Wearable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='usage',
            name='wearable_name',
        ),
        migrations.DeleteModel(
            name='Usage',
        ),
    ]
