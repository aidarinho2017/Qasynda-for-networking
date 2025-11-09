# Generated manually for ItemPriceHistory

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_item_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemPriceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField()),
                ('changed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_history', to='items.item')),
            ],
            options={
                'ordering': ['-changed_at'],
            },
        ),
    ]
