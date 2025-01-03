# Generated by Django 4.2.16 on 2024-12-17 21:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "investment_fund",
            "0012_alter_transactions_options_alter_transactions_amount_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="transactions",
            name="fund",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transactions",
                to="investment_fund.investmentfund",
            ),
        ),
    ]
