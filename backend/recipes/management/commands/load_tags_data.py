import json
import os

from django.core.management import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Tag

ALREDY_LOADED_ERROR_MESSAGE = """
Если вам нужно загрузить новые данные вместо уже загруженных,
удалите db.sqlite3, чтобы снести бд.
Затем выполните миграции для создания пустой бд,
готовой к загрузке данных"""


class Command(BaseCommand):
    help = 'Загружает данные из json файла'
    file_name = 'tags.json'
    data_path = os.path.join(BASE_DIR, 'data')

    def handle(self, *args, **options):

        if Tag.objects.exists():
            print('Теги уже загружены...завершение.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        print('Загрузка тегов...')

        path = os.path.join(self.data_path, self.file_name)
        with open(path, 'r', encoding="utf-8") as data:
            loaded_data = json.load(data)
            Tag.objects.bulk_create(
                objs=[
                    Tag(**tag_data)
                    for tag_data in loaded_data
                ]
            )
            print(f'Теги из файла {self.file_name} загружены.')
