# Generated by Django 3.0.4 on 2020-03-05 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to=''),
        ),
    ]
