# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Wearable',
            fields=[
                ('name', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('remarks', models.CharField(max_length=300)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wearable_Battery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('battery', models.IntegerField(default=0)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('wearable_name', models.ForeignKey(to='NowtifyWeb.Wearable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Wearable_Usage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('used', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('wearable_name', models.ForeignKey(to='NowtifyWeb.Wearable')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
