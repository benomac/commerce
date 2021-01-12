# Generated by Django 3.1.4 on 2021-01-10 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='currant_price',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='auctions.bid'),
            preserve_default=False,
        ),
    ]