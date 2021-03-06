# Generated by Django 3.0.3 on 2020-03-03 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend', '0005_auto_20200227_2315'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
                ('apartment_address', models.CharField(max_length=100)),
                ('country', models.CharField(choices=[('BD', 'Bangladesh')], max_length=2)),
                ('state', models.CharField(choices=[('Chittagong', (('cbra', 'Brahmanbaria'), ('ccom', 'Comilla'), ('clak', 'Lokshmipur'), ('cnoa', 'Noakhali'), ('cfen', 'Feni'), ('ckha', 'Khagrachhari'), ('cran', 'Rangamati'), ('cban', 'Bandarban'), ('cchi', 'Chittagong'), ('ccox', "Cox's Bazar"))), ('Barisal', (('bbra', 'Barisal'), ('bbar', 'Barguna'), ('bhol', 'Bhola'), ('bjal', 'Jhalokati'), ('bpat', 'Patuakhali'), ('bpir', 'Pirojpur'))), ('Dhaka', (('ddha', 'Dhaka'), ('dgha', 'Ghazipur'), ('dkis', 'Kishoreganj'), ('dman', 'Manikganj'), ('dmun', 'Munshiganj'), ('dnar', 'Narayanganj'), ('dnrs', 'Narasingdi'), ('dtan', 'Tangail'), ('dfar', 'Faridpur'), ('dgop', 'Gopalganj'), ('dmad', 'Madaripur'), ('draj', 'Rajbari'), ('dsha', 'Shariatpur')))], max_length=4)),
                ('zip_code', models.CharField(blank=True, max_length=15)),
                ('same_billing_shipping_address', models.BooleanField(default=True)),
                ('save_info', models.BooleanField(default=True)),
                ('payment_method', models.CharField(choices=[('str', 'Stripe'), ('bks', 'bKash'), ('con', 'Cash On Delivery')], max_length=3)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='billing_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='backend.BillingInfo'),
        ),
    ]
