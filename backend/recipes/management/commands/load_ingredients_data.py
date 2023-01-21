import json
import os

from django.core.management import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = 'Loads data from json'
    file_name = 'ingredients.json'
    data_path = os.path.join(BASE_DIR, 'data')

    def handle(self, *args, **options):

        if Ingredient.objects.exists():
            print('ingredients data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print('Loading ingredients data')

        path = os.path.join(self.data_path, self.file_name)
        with open(path, 'r', encoding="utf-8") as data:
            loaded_data = json.load(data)
            Ingredient.objects.bulk_create(
                objs=[
                    Ingredient(**ingredient_data)
                    for ingredient_data in loaded_data
                ]
            )
            print(f'Ингредиенты из файла {self.file_name} загружены.')
