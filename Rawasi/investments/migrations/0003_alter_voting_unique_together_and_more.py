# Generated by Django 5.1.4 on 2024-12-16 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investments', '0002_remove_investmentopportunity_approval_percentage_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='voting',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='buyselltransaction',
            name='required_approval_percentage',
        ),
        migrations.AddField(
            model_name='voting',
            name='vote_type',
            field=models.CharField(choices=[('Buy', 'Buy'), ('Sell', 'Sell')], default='Buy', max_length=4),
        ),
        migrations.AlterField(
            model_name='voting',
            name='vote',
            field=models.CharField(choices=[('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Pending', 'Pending')], default='Pending', max_length=10),
        ),
    ]
