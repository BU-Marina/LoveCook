import json
import base64
import os

from django.core.management import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from foodgram.settings import BASE_DIR
from recipes.models import (
    Ingredient,
    Tag,
    Category,
    Selection,
    Cuisine,
    Recipe,
    SelectionRecipe,
    RecipeImage,
    RecipeIngredient,
    Favorite
)
# from users.models import Follow

User = get_user_model()

ALREDY_LOADED_ERROR_MESSAGE = """Если вам нужно загрузить новые данные вместо 
уже загруженных, удалите db.sqlite3, чтобы снести бд.
Затем выполните миграции для создания пустой бд,
готовой к загрузке данных.
"""

def image64_decode(imagebase64, *args):
    if not imagebase64:
        return imagebase64
    format, imgstr = imagebase64.split(';base64,')
    ext = format.split('/')[-1]  
    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return data

def get_instance(pk, entity):
    return entity[0].objects.get(pk=pk)


class Command(BaseCommand):
    help = 'Загружает тестовые данные из json файла'
    data_path = os.path.join(BASE_DIR, 'data')
    file_names = {
        Ingredient: 'ingredients.json',
        User: 'users.json',
        Tag: 'tags.json',
        Category: 'categories.json',
        Selection: 'selections.json',
        Cuisine: 'cuisines.json',
        Recipe: 'recipes.json',
        SelectionRecipe: 'selectionsrecipes.json',
        RecipeImage: 'recipesimages.json',
        RecipeIngredient: 'recipesingreds.json',
        Favorite: 'favorites.json',
    }
    to_convert = {
        Ingredient: {"image": (image64_decode,)},
        User: {"password": (make_password,)},
        Selection: {
            "cover": (image64_decode,),
            "author": (get_instance, User),
            "category": (get_instance, Category)
        },
        Recipe: {"author": (get_instance, User)},
        SelectionRecipe: {
            "selection": (get_instance, Selection),
            "recipe": (get_instance, Recipe)
        },
        RecipeImage: {
            "recipe": (get_instance, Recipe),
            "image": (image64_decode,)
        },
        RecipeIngredient: {
            "recipe": (get_instance, Recipe),
            "ingredient": (get_instance, Ingredient)
        },
        Favorite: {
            "recipe": (get_instance, Recipe),
            "user": (get_instance, User)
        }
    }
    to_set = {
        Recipe: "tags",
    }

    def data_already_loaded(self, entity):
        if entity.objects.exists():
            print(f'{entity.__name__}: Объекты уже загружены...завершение.') # может поменять на логи?
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return True
        return False

    def field_conversion(self, entity, data, field_name, func_info):
        func, *args = func_info
        objs = []

        try:
            for obj_data in data:
                value = obj_data.pop(field_name)
                obj_data[field_name] = func(value, args)
                objs.append(obj_data)
        except Exception as e:
            print(
                f'{entity.__name__}: Во время преобразования поля {field_name} '
                f'произошла ошибка: {e} \n Данные не преобразованы.'
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

            if entity in self.to_convert:
                for field_name, func_info in self.to_convert[entity].items():
                    objs = self.field_conversion(
                        entity, objs, field_name, func_info
                    )

            if not objs:
                print('Данные не загружены.\n')
                return
            
            if entity in self.to_set:
                field_name = self.to_set[entity]
                for obj in objs:
                    values = obj.pop(field_name) # try except
                    instance = entity.objects.create(**obj)
                    getattr(instance, field_name).set(values)

            else:
                entity.objects.bulk_create([entity(**obj) for obj in objs])

            print(f'{entity.__name__}: Данные из файла {file_name} загружены.\n')

    def handle(self, *args, **options):
        for entity, file_name in self.file_names.items():
            if self.data_already_loaded(entity):
                continue

            print(f'{entity.__name__}: Загрузка данных...')
            self.load_data(entity, file_name)
