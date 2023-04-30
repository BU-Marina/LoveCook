from fractions import Fraction
from itertools import chain

from django.contrib.auth import get_user_model

from dj_rql.drf.serializers import RQLMixin
from drf_extra_fields.fields import Base64FileField, Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (MAX_COOKING_TIME, MIN_COOKING_TIME, Cuisine,
                            Equipment, FavoriteRecipe, FavoriteSelection,
                            Ingredient, Recipe, RecipeImage, RecipeIngredient,
                            RecipeReview, RecommendRecipe, Selection, Step,
                            Tag)
from users.models import Follow

RECIPES_LIMIT_DEFAULT = '6'
REVIEWS_LIMIT_DEFAULT = '10'
RECOMMENDED_BY_LIMIT_DEFAULT = '5'
# TAGS_LIMIT_DEFAULT = '3'
MAX_HOURS = MAX_COOKING_TIME // 60
MAX_TAGS_AMOUNT = 10
MAX_IMAGES_AMOUNT = 10
# MIN_STEPS_AMOUNT = 1
MAX_STEPS_AMOUNT = 20
MIN_TITLE_LENGTH = 2
MIN_DESCRIPTION_LENGTH = 8
MIN_NOTE_LENGTH = 8
MIN_PHRASE_LENGTH = 3

User = get_user_model()


def to_minutes(hours: int, minutes: int) -> int:
    return hours*60 + minutes


def from_minutes(minutes: int) -> dict[int, int]:
    hours = minutes // 60
    mins = minutes % 60
    return {
        'hours': hours,
        'minutes': mins
    }


class UserSerializer(serializers.ModelSerializer):
    ...
#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             'id', 'username', 'email', 'first_name', 'last_name',
#             'is_subscribed'
#         )

#     def get_is_subscribed(self, obj):
#         user = self.context['request'].user
#         return (
#             user.is_authenticated
#             and Follow.objects.filter(user=user, following=obj).exists()
#         )


class UserListSerializer(serializers.ModelSerializer):
    ...


class AuthorSerializer(RQLMixin, serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    image = Base64ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'name', 'surname', 'username', 'image',
            'is_subscribed', 'recipes_count'
        )
        read_only_fields = ('id', 'image')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, following=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SelectionListSerializer(RQLMixin, serializers.ModelSerializer):
    author = AuthorSerializer(many=False, read_only=True)
    cover = Base64ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    favorited_by_amount = serializers.SerializerMethodField()

    class Meta:
        model = Selection
        fields = (
            'id', 'title', 'author', 'cover', 'is_favorited',
            'recipes_count', 'favorited_by_amount'
        )
        read_only_fields = fields

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and FavoriteSelection.objects.filter(
                user=user, selection=obj
            ).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_favorited_by_amount(self, obj):
        return FavoriteSelection.objects.filter(selection=obj).count()


class CookingTimeSerializer(RQLMixin, serializers.Serializer):
    hours = serializers.IntegerField(
        default=0,
        min_value=0,
        max_value=MAX_HOURS
    )
    minutes = serializers.IntegerField(
        default=0,
        min_value=0,
        max_value=59
    )

    def validate(self, attrs):
        super().validate(attrs)
        return to_minutes(**attrs)

    def to_representation(self, value):
        return from_minutes(value)


class ImageSerializer(RQLMixin, serializers.ModelSerializer):
    image = Base64ImageField(read_only=False)

    class Meta:
        model = RecipeImage
        fields = (
            'image', 'is_cover'
        )
        extra_kwargs = {'is_cover': {'required': False, 'default': 0}}


class SlugCreatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            value, _ = queryset.get_or_create(**{self.slug_field: data})
            return value
        except (TypeError, ValueError):
            self.fail('invalid')


class IngredientSerializer(RQLMixin, serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Ingredient
        fields = (
            'id', 'name', 'species', 'image', 'description'
        )
        read_only_fields = ('id',)


class IngredientImageSerializer(RQLMixin, serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ('name', 'image')


class StepReprSerializer(RQLMixin, serializers.ModelSerializer):
    ingredients = IngredientImageSerializer(many=True, read_only=True)

    class Meta:
        model = Step
        fields = (
            'serial_num', 'title', 'description', 'note', 'ingredients'
        )
        read_only_fields = fields


class StepSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'too_short': '{name} должен содержать минимум {min} символа(-ов).',
        'only_letters': '{name} не должен содержать цифры и символы.',
    }

    class Meta:
        model = Step
        fields = (
            'serial_num', 'title', 'description', 'note', 'ingredients'
        )

    def to_representation(self, instance):
        return StepReprSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def validate_title(self, value):
        if value and len(value) < MIN_TITLE_LENGTH:
            self.fail(
                'too_short',
                name='title',
                min=MIN_TITLE_LENGTH
            )
        if not all(symb.isalpha() or symb.isspace() for symb in value):
            self.fail(
                'only_letters',
                name='title'
            )
        return value

    def validate_description(self, value):
        if len(value) < MIN_DESCRIPTION_LENGTH:
            self.fail(
                'too_short',
                name='description',
                min=MIN_DESCRIPTION_LENGTH
            )
        return value

    def validate_note(self, value):
        if value and len(value) < MIN_NOTE_LENGTH:
            self.fail(
                'too_short',
                name='note',
                min=MIN_NOTE_LENGTH
            )

        return value


class MeasurementSerializer(serializers.Serializer):
    amount = serializers.CharField(max_length=4)
    unit = serializers.CharField(max_length=2)
    unit_full = serializers.CharField(max_length=8)


class RecipeIngredientReprSerializer(RQLMixin, serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=False, read_only=True)
    amount = serializers.SerializerMethodField()
    other_measures = serializers.SerializerMethodField()
    measurement_unit_full = serializers.SerializerMethodField()

    UNIT_TO_GRAMS = {
        'кг': 1000,
        'л': 1000,
        'мл': 1,
        'ун': 28.35,
        'жид ун': 28.41,
        'ч л': 5,
        'д л': 10,
        'c л': 15,
        'пинта': 403.2,
    }

    FULL_UNITS = {
        'кг': 'килограмм',
        'л': 'литр',
        'мл': 'миллилитр',
        'ун': 'унция',
        'жид ун': 'жидкая унция',
        'ч л': 'чайная ложка',
        'д л': 'десертная ложка',
        'c л': 'столовая ложка',
        'пинта': 'пинта',
    }

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount', 'measurement_unit',
                  'measurement_unit_full', 'other_measures')
        read_only_fields = fields

    def get_measurement_unit_full(self, obj):
        return obj.get_measurement_unit_display()

    def fractions_repr(self, fraction):
        return str(fraction)

    def get_amount(self, obj):
        request = self.context.get('request')
        count_servings = request.query_params.get('servings')

        try:
            count_servings = int(count_servings)
        except ValueError:
            raise ParseError(
                'Передано некорректное значение параметра servings. '
                'Должно быть целое число.'
            )
        except TypeError:
            pass

        if count_servings:
            self.new_amount = obj.amount * Fraction(
                count_servings/obj.recipe.servings
            )
            return self.fractions_repr(self.new_amount)

        return self.fractions_repr(obj.amount)

    def get_grams(self, amount, unit):
        if unit == 'г':
            return amount

        grams_in_one = self.UNIT_TO_GRAMS.get(unit)
        if not grams_in_one:
            return None

        return amount*grams_in_one

    def get_other_measures(self, obj):
        obj_amount = self.new_amount if self.new_amount else obj.amount
        obj_unit = obj.measurement_unit
        grams = self.get_grams(obj_amount, obj_unit)
        other_measures = []

        if grams:
            other_measures.append({
                'amount': grams, 'unit': 'г', 'unit_full': 'грамм'
            })
            for unit, grams_in_one in self.UNIT_TO_GRAMS.items():
                if unit == obj_unit:
                    continue

                amount = (Fraction(1/grams_in_one)*grams).limit_denominator()
                if amount.denominator <= 10:
                    other_measures.append({
                        'amount': amount,
                        'unit': unit,
                        'unit_full': self.FULL_UNITS.get(unit)
                    })

        return MeasurementSerializer(
            other_measures,
            many=True,
            context={'request': self.context.get('request')}
        ).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'measurement_unit', 'amount')

    def to_representation(self, instance):
        return RecipeIngredientReprSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class EquipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipment
        fields = ('name', 'image', 'description')


class EquipmentListSerializer(RQLMixin, serializers.ModelSerializer):

    class Meta:
        model = Equipment
        fields = ('id', 'name', 'image')
        read_only_fields = fields


class RecipeReviewSerializer(RQLMixin, serializers.ModelSerializer):
    user = AuthorSerializer(many=False, read_only=True)

    class Meta:
        model = RecipeReview
        fields = ('user', 'comment')


class RecipeReprSerializer(RQLMixin, serializers.ModelSerializer):
    author = AuthorSerializer(many=False, read_only=True)
    selections = SelectionListSerializer(
        many=True, read_only=True
    )
    images = ImageSerializer(many=True, read_only=False)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='ingredients_info'
    )
    ingredients_amount = serializers.SerializerMethodField()
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name'
    )
    steps = StepSerializer(many=True, read_only=True)
    steps_amount = serializers.SerializerMethodField()
    equipment = EquipmentListSerializer(many=True, read_only=True)
    cuisine = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='name'
    )
    cooking_time = CookingTimeSerializer()
    video = Base64FileField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorited_by_amount = serializers.SerializerMethodField()
    recipes_from_author = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    is_recommended = serializers.SerializerMethodField()
    recommended_by = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'description', 'servings', 'cooking_time',
            'cuisine', 'ending_phrase', 'images', 'video', 'tags',
            'selections', 'ingredients', 'ingredients_amount', 'steps',
            'steps_amount', 'author', 'is_favorited', 'favorited_by_amount',
            'equipment', 'created', 'recipes_from_author', 'is_recommended',
            'recommended_by', 'reviews'
        )
        read_only_fields = fields

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_recommended(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and RecommendRecipe.objects.filter(user=user, recipe=obj).exists()
        )

    def get_ingredients_amount(self, obj):
        return obj.ingredients.count()

    def get_steps_amount(self, obj):
        return obj.steps.count()

    def get_favorited_by_amount(self, obj):
        return obj.favorited_by.count()

    def get_recipes_from_author(self, obj):
        return RecipeListSerializer(
            Recipe.objects.filter(author=obj.author).exclude(pk=obj.pk),
            many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_recommended_by(self, obj):
        request = self.context.get('request')
        recommended_by_limit = request.query_params.get(
            'recommended_by_limit', RECOMMENDED_BY_LIMIT_DEFAULT
        )

        return AuthorSerializer(
            obj.recommended_by.all()[:int(recommended_by_limit)],
            many=True,
            context={'request': self.context.get('request')}
        ).data

    def get_reviews(self, obj):
        request = self.context.get('request')
        reviews_limit = request.query_params.get(
            'reviews_limit', REVIEWS_LIMIT_DEFAULT
        )

        reviews = obj.reviews.all()[:int(reviews_limit)]

        return RecipeReviewSerializer(
            reviews, many=True, context={'request': request}
        ).data

    # def get_is_in_shopping_cart(self, obj):
    #     user = self.context['request'].user
    #     return (
    #         user.is_authenticated
    #         and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
    #     )


class RecipeListSerializer(RecipeReprSerializer):
    # tags = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'description', 'servings', 'cooking_time',
            'cuisine', 'images', 'tags', 'ingredients_amount', 'ingredients',
            'steps_amount', 'author', 'is_favorited', 'favorited_by_amount'
        )

    # def get_tags(self, obj):
    #     request = self.context.get('request')
    #     tags_limit = request.query_params.get(
    #         'tags_limit', TAGS_LIMIT_DEFAULT
    #     )

    #     tags = obj.tags.all()[:int(tags_limit)]

    #     return TagSerializer(
    #         tags, many=True, context={'request': request}
    #     ).data


class RecipeSerializer(RQLMixin, serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=False, required=True, source='ingredients_info'
    )
    steps = StepSerializer(many=True, read_only=False, required=True)
    selections = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, required=False,
        queryset=Selection.objects.all()
    )
    tags = SlugCreatedField(
        many=True, read_only=False, required=False,
        slug_field='name', queryset=Tag.objects.all()
    )
    cuisine = serializers.SlugRelatedField(
        many=False, read_only=False, required=False,
        slug_field='name', queryset=Cuisine.objects.all()
    )
    cooking_time = CookingTimeSerializer()
    video = Base64FileField(read_only=False, required=False)
    images = ImageSerializer(many=True, read_only=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    equipment = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, required=False,
        queryset=Equipment.objects.all()
    )

    default_error_messages = {
        'covers_out_of_range': (
            'Неправильное кол-во обложек. '
            'У рецепта должна быть одна обложка.'
        ),
        'out_of_range': (
            '{item} вне диапазона. Должно быть между {min} и {max}.'
        ),
        'no_data': (
            'Ничего не передано в {name}.'
        ),
        'too_many': 'Слишком много {name} (макс {max}).',
        'too_short': '{name} должен содержать минимум {min} символа(-ов).',
        'only_letters': '{name} не должен содержать цифры и символы.',
        'no_digits': '{name} не должен содержать цифры.',
        'not_allowed': 'Запрос {method} не должен содержать {field}.',
        'no_repeat': '{name} не должны повторяться.',
        'no_match': (
            '{common_field} в {field} должны состоять из '
            '{common_field} в recipe.'
        ),
        'required': '{field} обязательное поле.',
    }

    class Meta:
        model = Recipe
        fields = (
            'title', 'description', 'servings', 'cooking_time',
            'cuisine', 'ending_phrase', 'images', 'video', 'tags',
            'selections', 'ingredients', 'steps', 'equipment', 'author'
        )

    def set_recipe_relation(self, recipe, objs_data, model) -> None:
        objs = [model(
            recipe=recipe,
            **data
        ) for data in objs_data]

        model.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_info')
        images = validated_data.pop('images')
        steps = validated_data.pop('steps')
        tags = validated_data.pop('tags', [])
        selections = validated_data.pop('selections', [])

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.selections.set(selections)

        self.set_recipe_relation(recipe, ingredients, RecipeIngredient)
        self.set_recipe_relation(recipe, images, RecipeImage)

        for data in steps:
            ingredients = data.pop('ingredients', [])
            data['recipe'] = recipe
            step = Step.objects.create(**data)
            step.ingredients.set(ingredients)

        return recipe

    def validate_title(self, value):
        if len(value) < MIN_TITLE_LENGTH:
            self.fail(
                'too_short',
                name='title',
                min=MIN_TITLE_LENGTH
            )
        if not all(symb.isalpha() or symb.isspace() for symb in value):
            self.fail(
                'only_letters',
                name='title'
            )
        return value

    def validate_description(self, value):
        if value and len(value) < MIN_DESCRIPTION_LENGTH:
            self.fail(
                'too_short',
                name='description',
                min=MIN_DESCRIPTION_LENGTH
            )
        return value

    def validate_ending_phrase(self, value):
        if value and len(value) < MIN_PHRASE_LENGTH:
            self.fail(
                'too_short',
                name='ending_phrase',
                min=MIN_PHRASE_LENGTH
            )
        if any(symb.isdigit() for symb in value):
            self.fail(
                'no_digits',
                name='ending_phrase'
            )
        return value

    def validate_cooking_time(self, value):
        if not (MIN_COOKING_TIME <= value <= MAX_COOKING_TIME):
            self.fail(
                'out_of_range',
                item='cooking_time',
                min=str(MIN_COOKING_TIME) + ' мин',
                max=str(MAX_HOURS) + ' ч'
            )

        return value

    def validate_images(self, data):
        if not data:
            self.fail('no_data', name='images')

        if len(data) > MAX_IMAGES_AMOUNT:
            self.fail('too_many', name='images', max=MAX_IMAGES_AMOUNT)

        covers_sum = sum([image.get('is_cover') for image in data])

        if covers_sum != 1:
            self.fail('covers_out_of_range')

        return data

    def validate_tags(self, data):
        if len(data) > 10:
            self.fail('too_many', name='tags', max=MAX_TAGS_AMOUNT)

        return data

    def validate_ingredients(self, data):
        if not data:
            self.fail('no_data', name='ingredients')

        ingredints_ids = [
            ing_info['ingredient'] for ing_info in data]

        if len(ingredints_ids) != len(set(ingredints_ids)):
            self.fail('no_repeat', name='ingredients')

        return data

    def validate_selections(self, data):
        request = self.context.get('request')
        if data and request.method == 'PATCH':
            self.fail('not_allowed', method='PATCH', field='selections')

        return data

    # def validate_reviews(self, data):
    #     request = self.context.get('request')
    #     if data and request.method == 'PATCH':
    #         self.fail('not_allowed', method='PATCH', field='reviews')

    #     return data

    def validate_steps(self, data):
        if not data:
            self.fail('no_data', name='steps')

        if len(data) > MAX_STEPS_AMOUNT:
            self.fail('too_many', name='steps', max=MAX_STEPS_AMOUNT)

        if not all(step.get('description') for step in data):
            self.fail('required', field='description')

        return data

    def steps_ingds_check(self, ingredients: set, recipe_ingredients: set):
        steps_ingredients = set(chain.from_iterable(ingredients))
        return steps_ingredients <= recipe_ingredients

    def update(self, instance, validated_data):
        if 'ingredients_info' in validated_data:
            RecipeIngredient.objects.filter(
                recipe=instance
            ).delete()
            ingredients = validated_data.pop('ingredients_info')
            self.set_recipe_relation(instance, ingredients, RecipeIngredient)

        if 'steps' in validated_data:
            steps = validated_data.pop('steps')
            steps_ingredints = [step['ingredients'] for step in steps]
            recipe_ingredients = instance.ingredients.all()

            if not self.steps_ingds_check(
                steps_ingredints, set(recipe_ingredients)
            ):
                self.fail(
                    'no_match',
                    common_field='ingredients',
                    field='steps'
                )

            Step.objects.filter(recipe=instance).delete()
            for data in steps:
                ingredients = data.pop('ingredients', [])
                data['recipe'] = instance
                step = Step.objects.create(**data)
                step.ingredients.set(ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReprSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), required=False
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в избранное.'
            )
        ]

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class SelectionSerializer(serializers.ModelSerializer):
    recipes = RecipeListSerializer(
        many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    favorited_by_amount = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Selection
        fields = (
            'id', 'title', 'is_favorited', 'favorited_by_amount',
            'recipes_count', 'recipes'
        )
        read_only_fields = ('id',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and FavoriteSelection.objects.filter(
                user=user, selection=obj
            ).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_favorited_by_amount(self, obj):
        return FavoriteSelection.objects.filter(selection=obj).count()


class SubscriptionsSerializer(UserSerializer):
    ...
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = (
#             'email', 'id', 'username', 'first_name', 'last_name',
#             'is_subscribed', 'recipes', 'recipes_count'
#         )

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         recipes_limit = request.query_params.get(
#             'recipes_limit', RECIPES_LIMIT_DEFAULT
#         )

#         recipes = Recipe.objects.filter(author=obj)[:int(recipes_limit)]

#         serializer = RecipeListSerializer(
#             recipes, many=True, context={'request': request}
#         )
#         return serializer.data

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    ...
#     queryset = User.objects.all()
#     user = serializers.PrimaryKeyRelatedField(queryset=queryset)
#     following = serializers.PrimaryKeyRelatedField(queryset=queryset)

#     class Meta:
#         model = Follow
#         fields = ('user', 'following')
#         read_only_fields = ('user', 'following')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Follow.objects.all(),
#                 fields=('user', 'following'),
#                 message='Вы уже подписаны на этого автора'
#             )
#         ]

#     def validate_following(self, value):
#         if self.context['request'].user == value:
#             raise serializers.ValidationError(
#                 "Нельзя подписаться на самого себя"
#             )
#         return value

#     def to_representation(self, instance):
#         return SubscriptionsSerializer(
#             instance.following,
#             context={'request': self.context.get('request')}
#         ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    ...
    # user = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all()
    # )
    # recipe = serializers.PrimaryKeyRelatedField(
    #     queryset=Recipe.objects.all()
    # )

#     class Meta:
#         model = ShoppingCart
#         fields = ('user', 'recipe')
#         read_only_fields = ('user', 'recipe')
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=ShoppingCart.objects.all(),
#                 fields=('user', 'recipe'),
#                 message='Вы уже добавили этот рецепт в список покупок'
#             )
#         ]

#     def to_representation(self, instance):
#         return RecipeListSerializer(
#             instance.recipe,
#             context={'request': self.context.get('request')}
#         ).data
