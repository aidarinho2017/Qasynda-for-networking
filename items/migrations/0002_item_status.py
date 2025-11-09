# Generated manually for adding status to Item

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='status',
            field=models.CharField(choices=[('in_sell', 'In Sell'), ('soon', 'Soon')], default='in_sell', max_length=20, null=True),
        ),
    ]
