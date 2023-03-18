import json
import base64
import os

from django.core.management import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient
# from users.models import Follow

User = get_user_model()

ALREDY_LOADED_ERROR_MESSAGE = """Если вам нужно загрузить новые данные вместо 
уже загруженных, удалите db.sqlite3, чтобы снести бд.
Затем выполните миграции для создания пустой бд,
готовой к загрузке данных.
"""

def image64_decode(imagebase64):
    format, imgstr = imagebase64.split(';base64,')
    ext = format.split('/')[-1]  
    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return data


class Command(BaseCommand):
    help = 'Загружает тестовые данные из json файла'
    data_path = os.path.join(BASE_DIR, 'data')
    file_names = {
        Ingredient: 'ingredients.json',
        User: 'users.json'
    }
    fields_to_convert = {
        Ingredient: {"image": image64_decode},
        User: {"password": make_password}
    }

    def data_already_loaded(self, entity):
        if entity.objects.exists():
            print(f'{entity.__name__}: Объекты уже загружены...завершение.') # может поменять на логи?
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return True
        return False

    def field_conversion(self, entity, data, field_name, func):
        objs = []
        try:
            for item in data:
                field = item.pop(field_name)
                item[field_name] = func(field)
                objs.append(entity(**item))
        except Exception:
            objs=[entity(**item) for item in data]
            print(
                f'{entity.__name__}: Во время преобразования поля {field_name} '
                f'произошла ошибка: {Exception} \n Данные не преобразованы.'
            )
        return objs

    def load_data(self, entity, file_name):
        path = os.path.join(self.data_path, file_name)

        if not os.path.exists(path):
            print(
                f'{entity.__name__}: Файл {path} не найден. '
                'Данные не загружены.\n'
            )
            return

        with open(path, 'r', encoding="utf-8") as data:
            loaded_data = json.load(data)

            objs=loaded_data
            for field_name, func in self.fields_to_convert[entity].items():
                objs = self.field_conversion(entity, objs, field_name, func)

            entity.objects.bulk_create(objs)

            print(f'{entity.__name__}: Данные из файла {file_name} загружены.\n')

    def handle(self, *args, **options):
        for entity, file_name in self.file_names.items():
            if self.data_already_loaded(entity):
                continue

            print(f'{entity.__name__}: Загрузка данных...')
            self.load_data(entity, file_name)
