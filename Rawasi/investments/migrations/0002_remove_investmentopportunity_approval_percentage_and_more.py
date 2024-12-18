# Generated by Django 5.1.4 on 2024-12-16 17:19

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investmentopportunity',
            name='approval_percentage',
        ),
        migrations.RemoveField(
            model_name='investmentopportunity',
            name='investment_duration',
        ),
        migrations.RemoveField(
            model_name='investmentopportunity',
            name='required_approval_percentage',
        ),
        migrations.AddField(
            model_name='voting',
            name='required_approval_percentage',
            field=models.FloatField(default=70.0),
        ),
        migrations.AddField(
            model_name='voting',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='voting',
            name='voting_end_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='voting',
            name='voting_start_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='voting',
            name='vote',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Rejected', max_length=10),
        ),
        migrations.CreateModel(
            name='BuySellTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('Buy', 'Buy'), ('Sell', 'Sell')], max_length=4)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=50)),
                ('required_approval_percentage', models.FloatField(default=70.0)),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buy_sell_transactions', to='investments.investmentopportunity')),
            ],
        ),
    ]