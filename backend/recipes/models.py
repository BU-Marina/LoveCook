from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

MIN_COOKING_TIME = 1
MIN_INGREDIENTS_AMOUNT = 0.1

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Ингредиент',
        help_text='Введите название'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения',
    )

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
        help_text='Введите название тега'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
        help_text='Придумайте слаг тега'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        help_text='Введите введите hex-код цвета'
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название рецепту'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Опишите своё блюдо'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Обложка',
        help_text='Загрузите картинку готового блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text=('Укажите время необходимое для приготовления (в минутах)'),
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество',
        validators=[MinValueValidator(MIN_INGREDIENTS_AMOUNT)]
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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart')
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
