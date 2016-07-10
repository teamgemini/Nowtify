# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('used', models.BooleanField(default=False)),
                ('updated', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wearable',
            fields=[
                ('name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('remarks', models.CharField(max_length=300)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='usage',
            name='wearable_name',
            field=models.ForeignKey(to='NowtifyWeb.Wearable'),
            preserve_default=True,
        ),
    ]
