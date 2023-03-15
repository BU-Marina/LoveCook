from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from core.models import CreatedModel

MIN_COOKING_TIME = 5
MAX_COOKING_TIME = 600
MIN_INGREDIENTS_AMOUNT = 0.1
MIN_SERVINGS = 1

User = get_user_model()


class Ingredient(models.Model):
    # CONDIMENT = 'C'
    # SOLID = 'S'
    # LIQUID = 'L'
    # CATEGORY = [
    #     (CONDIMENT, 'Приправы'),
    #     (SOLID, 'Твердые'),
    #     (LIQUID, 'Жидкости'),
    # ]

    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        help_text='Введите название'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите ингредиент'
    )
    species = models.CharField(
        max_length=200,
        verbose_name='Подвид',
        help_text='Укажите подвид, если нужно',
        blank=True
    )
    image = models.ImageField(
        upload_to='ingredients/',
        verbose_name='Фото',
        help_text='Загрузите картинку ингредиента',
    )
    # category = models.CharField(
    #     max_length=1,
    #     choices=CATEGORY
    # )

    # def get_measurement_units(self):
    #     ...

    def __str__(self) -> str:
        if self.species:
            return f'{self.name} ({self.species})'
        return f'{self.name}'


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
        help_text='Добавьте тег'
    )

    def __str__(self) -> str:
        return self.name


class Category(CreatedModel):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название категории подборок'
    )


def getDefaultCategory():
    return Category.objects.get_or_create(name='Другое') #*


class Selection(CreatedModel):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название подборке'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите подборку'
    )
    cover = models.ImageField(
        upload_to='selections/',
        verbose_name='Картинка',
        help_text='Загрузите обложку для подборки',
    )
    category = models.ForeignKey(
        Category,
        related_name='selections',
        on_delete=models.SET(getDefaultCategory)
    )

    def __str__(self) -> str:
        return self.title


class Cuisine(CreatedModel):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    description = models.TextField(verbose_name='Описание')
    # image

    def __str__(self) -> str:
        return self.name


class Recipe(CreatedModel):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название рецепту'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите блюдо'
    )
    servings = models.PositiveSmallIntegerField(
        verbose_name='Кол-во порций',
        help_text='Укажите кол-во порций',
        default=MIN_SERVINGS,
        validators=[MinValueValidator(MIN_SERVINGS)]
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text=('Укажите время, необходимое для приготовления блюда'),
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        ]
    )
    ending_phrase = models.TextField(
        verbose_name='Завершающая фраза',
        help_text=(
            'Завершите рецепт пожеланием приятного аппетита '
            'или вашей авторской фразой'
        ),
        default='Приятного аппетита!'
    )
    video = models.FileField(
        upload_to='recipes/',
        verbose_name='Видео приготовления',
        help_text='Загрузите видео приготовления блюда по этому рецепту'
    )
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(Tag)
    selections = models.ManyToManyField(
        Selection,
        through='SelectionRecipe'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )

    # class Meta:
    #     ordering = ['-created']

    def __str__(self) -> str:
        return self.title


class RecipeImage(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Фото',
        help_text='Загрузите картинку готового блюда',
    )
    is_cover = models.BooleanField()

    def __str__(self) -> str:
        if self.is_cover:
            return f'Обложка {self.id} рецета {self.recipe}'
        return f'Картинка {self.id} рецета {self.recipe}'


class SelectionRecipe(CreatedModel):
    selection = models.ForeignKey(
        Selection,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['selection', 'recipe'],
                name='unique_selection_recipe'
            )
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} принадлежит подборке {self.selection}'


class RecipeIngredient(models.Model):
    MEASUREMENT_UNITS = [
        ('гр', 'гр'),
        ('кг', 'кг'),
        ('л', 'литр'),
        ('мл', 'мл'),
        ('ун', 'унция'),
        ('шт', 'шт'),
        ('щ', 'щепотка'),
        ('ч', 'чашка'),
        ('ч л', 'чайная ложка'),
        ('с л', 'столовая ложка'),
        ('д л', 'десертная ложка'),
        ('п', 'пинта'),
        ('пв', 'по вкусу'),
    ]
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество'
    )
    measurement_unit = models.CharField(
        max_length=3,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения',
        choices=MEASUREMENT_UNITS
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self) -> str:
        return (f'Ингредиент {self.ingredient} '
                f'используется в рецепте {self.recipe}')


class Favorite(models.Model):
    ...
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='favorited_by'
    # )
    # recipe = models.ForeignKey(
    #     Recipe,
    #     on_delete=models.CASCADE,
    #     related_name='favorited'
    # )

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['user', 'recipe'], name='unique_favorite')
    #     ]

    # def __str__(self) -> str:
    #     return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    ...
    # user = models.ForeignKey(
    #     User,
    #     on_delete=models.CASCADE,
    #     related_name='shoppingcart'
    # )
    # recipe = models.ForeignKey(
    #     Recipe,
    #     on_delete=models.CASCADE,
    #     related_name='shoppingcart'
    # )

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['user', 'recipe'], name='unique_shoppingcart')
    #     ]

    # def __str__(self) -> str:
    #     return f'Рецепт {self.recipe} в списке покупок у {self.user}'
