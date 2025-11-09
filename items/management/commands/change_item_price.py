# items/management/commands/change_item_price.py
from django.core.management.base import BaseCommand
from items.models import Item

class Command(BaseCommand):
    help = 'Change the price of an item and record in history'

    def add_arguments(self, parser):
        parser.add_argument('item_id', type=int, help='ID of the item')
        parser.add_argument('new_price', type=int, help='New price for the item')

    def handle(self, *args, **options):
        try:
            item = Item.objects.get(id=options['item_id'])
            old_price = item.cost
            item.cost = options['new_price']
            item.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully changed price of "{item.name}" from {old_price} to {item.cost}')
            )
        except Item.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Item with ID {options["item_id"]} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
