# Generated by Django 3.0.4 on 2020-03-07 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_refund'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_refund_requested',
            field=models.BooleanField(default=False),
        ),
    ]
