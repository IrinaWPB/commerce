# Generated by Django 3.1.7 on 2021-04-05 15:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20210403_2325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watchlist',
            name='product',
        ),
        migrations.AddField(
            model_name='watchlist',
            name='product',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='auctions.listing'),
            preserve_default=False,
        ),
    ]