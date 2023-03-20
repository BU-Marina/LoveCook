from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from core.models import CreatedModel

MIN_COOKING_TIME = 5
MAX_COOKING_TIME = 600
MIN_INGREDIENTS_AMOUNT = 0.1
MIN_SERVINGS = 1
MAX_SERVINGS = 10

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
        upload_to='ingredients/images',
        verbose_name='Фото',
        help_text='Загрузите картинку ингредиента'
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
        unique=True,
        verbose_name='Название',
        help_text='Дайте название категории подборок'
    )
    description = models.TextField(verbose_name='Описание', blank=True)

    def __str__(self) -> str:
        return self.name


def get_default_category() -> Category:
    return Category.objects.get_or_create(name='Другое')


class Selection(CreatedModel):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название подборке'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите подборку',
        blank=True
    )
    cover = models.ImageField(
        upload_to='selections/',
        verbose_name='Картинка',
        help_text='Загрузите обложку для подборки',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='selections',
        verbose_name='Автор'
    )
    category = models.ForeignKey(
        Category,
        related_name='selections',
        on_delete=models.SET(get_default_category)
    )

    def __str__(self) -> str:
        return self.title


class Cuisine(CreatedModel):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
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
        help_text='Опишите блюдо',
        blank=True
    )
    servings = models.PositiveSmallIntegerField(
        verbose_name='Кол-во порций',
        help_text='Укажите кол-во порций',
        default=MIN_SERVINGS,
        validators=[
            MinValueValidator(MIN_SERVINGS),
            MaxValueValidator(MAX_SERVINGS)
        ]
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text=(
            'Укажите время, необходимое для приготовления блюда (мин)'
        ),
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
        default='Приятного аппетита!',
        blank=True
    )
    video = models.FileField(
        upload_to='recipes/videos',
        verbose_name='Видео приготовления',
        help_text='Загрузите видео приготовления блюда по этому рецепту',
        blank=True,
        null=True
    )
    cuisine = models.ForeignKey(
        Cuisine,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='recipes',
        verbose_name='Национальная кухня',
        help_text='Выберите кухню, к которой относится блюдо',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        help_text='Добавьте теги к рецепту',
    )
    selections = models.ManyToManyField(
        Selection,
        through='SelectionRecipe',
        verbose_name='Подборки',
        help_text='Добавьте рецепт в подборку',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты, используемые в рецепте',
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
        upload_to='recipes/images/',
        verbose_name='Фото',
        help_text='Загрузите картинку готового блюда'
    )
    is_cover = models.BooleanField()
    # alt text

    def __str__(self) -> str:
        if self.is_cover:
            return f'Обложка рецепта {self.recipe}'
        return f'Картинка рецепта {self.recipe}'


@receiver(pre_delete, sender=Ingredient)
@receiver(pre_delete, sender=RecipeImage)
def recipeimage_delete(sender, instance, **kwargs):
    try:
        instance.image.delete(False)
    except Exception:
        pass


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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} в избранном у {self.user}'


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
