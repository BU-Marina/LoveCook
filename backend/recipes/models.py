from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from djfractions.models import DecimalFractionField

from core.models import CreatedModel

MIN_COOKING_TIME = 5
MAX_COOKING_TIME = 600
MIN_INGREDIENTS_AMOUNT = 0.1
MIN_SERVINGS = 1
MAX_SERVINGS = 10
MIN_CUPGRAMS = 50
MAX_CUPGRAMS = 500
DEFAULT_CATEGORY_NAME = 'Другое'

User = get_user_model()


class Ingredient(models.Model):
    '''Ингредиент'''
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
    one_piece_weight = models.PositiveSmallIntegerField(
        verbose_name='Вес 1 шт (г)',
        help_text='Укажите вес 1 шт в граммах',
        null=True
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


class Flavoring(models.Model):
    '''Приправа'''
    ...


class Tag(models.Model):
    '''Тег'''
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
        help_text='Добавьте тег'
    )

    def __str__(self) -> str:
        return self.name


class Category(CreatedModel):
    '''Категория подборок'''
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
    return Category.objects.get_or_create(name=DEFAULT_CATEGORY_NAME)


class Selection(CreatedModel):
    '''Подборка'''
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
        help_text='Загрузите обложку для подборки'
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
    favorited_by = models.ManyToManyField(
        User,
        through='FavoriteSelection',
        related_name='favorite_selections'
    )
    recommended_by = models.ManyToManyField(
        User,
        through='RecommendSelection',
        related_name='recommend_selections'
    )

    def __str__(self) -> str:
        return self.title


class Cuisine(CreatedModel):
    '''Национальная кухня'''
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


class Equipment(models.Model):
    '''Оборудование'''
    name = models.CharField(
        max_length=250,
        verbose_name='Название',
        help_text='Введите название'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Добавьте описание',
        blank=True
    )
    image = models.ImageField(
        upload_to='equipment/images/',
        verbose_name='Картинка',
        help_text='Загрузите картинку'
    )

    def __str__(self) -> str:
        return self.name


class Recipe(CreatedModel):
    '''Рецепт'''
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
        help_text='Выберите кухню, к которой относится блюдо'
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
        help_text='Добавьте теги к рецепту'
    )
    selections = models.ManyToManyField(
        Selection,
        through='SelectionRecipe',
        verbose_name='Подборки',
        help_text='Добавьте рецепт в подборку',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        help_text='Укажите ингредиенты, используемые в рецепте'
    )
    equipment = models.ManyToManyField(
        Equipment,
        verbose_name='Оборудование',
        help_text='Укажите используемое оборудование'
    )
    favorited_by = models.ManyToManyField(
        User,
        through='FavoriteRecipe',
        related_name='favorite_recipes'
    )
    recommended_by = models.ManyToManyField(
        User,
        through='RecommendRecipe',
        related_name='recommend_recipes'
    )

    # class Meta:
    #     ordering = ['-created']

    def __str__(self) -> str:
        return self.title


class RecipeImage(models.Model):
    '''Картинка к рецепту'''
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

    def __str__(self) -> str:
        if self.is_cover:
            return f'Обложка рецепта {self.recipe}'
        return f'Картинка рецепта {self.recipe}'


class RecipeReview(CreatedModel):
    '''Отзыв'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    comment = models.CharField(
        max_length=500,
        verbose_name='Комментарий',
        help_text='Оставьте свой комментарий'
    )
    # rating = ...

    def __str__(self) -> str:
        return f'Комментарий пользователя {self.user} к рецепту {self.recipe}'


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
        ('г', 'грамм'),
        ('кг', 'килограмм'),
        ('л', 'литр'),
        ('мл', 'миллилитр'),
        ('ун', 'унция'),
        ('жид ун', 'жидкая унция'),
        ('шт', 'штука'),
        ('чашка', 'чашка'),
        ('ч л', 'чайная ложка'),
        ('с л', 'столовая ложка'),
        ('д л', 'десертная ложка'),
        ('пинта', 'пинта'),
        ('щепотка', 'щепотка'),
        ('по вкусу', 'по вкусу'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_info'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_info'
    )
    amount = DecimalFractionField(
        verbose_name='Количество',
        help_text='Укажите количество',
        max_digits=4,
        decimal_places=1,
        limit_denominator=10,
        coerce_thirds=False
    )
    measurement_unit = models.CharField(
        max_length=8,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения',
        choices=MEASUREMENT_UNITS
    )
    cupgrams = models.PositiveSmallIntegerField(
        verbose_name='Объем чашки (г)',
        help_text=('Укажите объем для меры измерения "чашка" '
                   'для перевода в другие меры измерения'),
        null=True,
        validators=[
            MinValueValidator(MIN_CUPGRAMS),
            MaxValueValidator(MAX_CUPGRAMS)
        ]
    )
    note = models.CharField(
        max_length=250,
        verbose_name='Примечание',
        help_text='Добавьте уточняющие детали к ингредиенту',
        blank=True
    )
    note_image = models.ImageField(
        upload_to='recipes/ingredients/images/',
        verbose_name='Картинка примечания',
        help_text='Добавьте картинку к примечанию'
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
                f'используется в рецепте {self.recipe} '
                f'в кол-ве {self.amount} {self.measurement_unit}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe_favorite')
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class FavoriteSelection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    selection = models.ForeignKey(
        Selection,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'selection'], name='unique_selection_favorite')
        ]

    def __str__(self) -> str:
        return f'Подборка {self.selection} в избранном у {self.user}'


class RecommendRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe_recommend')
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} рекомендован пользователем {self.user}'


class RecommendSelection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    selection = models.ForeignKey(
        Selection,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'selection'], name='unique_selection_recommend'
            )
        ]

    def __str__(self) -> str:
        return (
            f'Подборка {self.selection} рекомендована пользователем '
            f'{self.user}'
        )


class Step(models.Model):
    '''Шаг приготовления'''
    serial_num = models.PositiveSmallIntegerField(
        verbose_name='Порядковый номер',
        help_text='Укажите порядковый номер шага'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте короткое название шагу',
        blank=True
    )
    description = models.CharField(
        max_length=500,
        verbose_name='Описание',
        help_text='Опишите действия на этом шаге'
    )
    note = models.CharField(
        max_length=250,
        verbose_name='Примечание',
        help_text='Добавьте уточняющие детали к описанию шага',
        blank=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты, используемые на этом шаге'
    )

    def __str__(self) -> str:
        return (
            f'Шаг {self.serial_num} в рецепте {self.recipe}: '
            f'{self.description}'
        )


class StepImage(models.Model):
    '''Картинка к шагу'''
    step = models.ForeignKey(
        Step,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='recipes/steps/images/',
        verbose_name='Фото',
        help_text='Загрузите фото к шагу'
    )

    def __str__(self) -> str:
        return f'Фото шага {self.step}'


@receiver(pre_delete, sender=StepImage)
@receiver(pre_delete, sender=Selection)
@receiver(pre_delete, sender=Ingredient)
@receiver(pre_delete, sender=RecipeImage)
def image_delete(sender, instance, **kwargs):
    try:
        instance.image.delete(False)
    except AttributeError:
        instance.cover.delete(False)
    except Exception:
        pass


class ShoppingCart(models.Model):
    '''Список покупок'''
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


# class Article(CreatedModel):
#     ...

