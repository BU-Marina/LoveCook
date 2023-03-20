from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64FileField, Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (MAX_COOKING_TIME, MIN_COOKING_TIME, Cuisine,
                            Favorite, Recipe, RecipeImage, RecipeIngredient,
                            Selection, Tag)

# from users.models import Follow

RECIPES_LIMIT_DEFAULT = '6'
MAX_HOURS = MAX_COOKING_TIME // 60
MAX_TAGS_AMOUNT = 10

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


def try_pop_item(data, item_key, many=True):
    try:
        return data.pop(item_key)
    except KeyError:
        if many:
            return []


class IngredientSerializer(serializers.ModelSerializer):
    ...

#     class Meta:
#         model = Ingredient
#         fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    ...

#     class Meta:
#         model = Tag
#         fields = (
#             'name'
#         )


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


class RecipeRepresentationSerializer(serializers.ModelSerializer):
    ...
#     ingredients = RecipeIngredientSerializer(
#         many=True, read_only=True, source='recipe_ingredients'
#     )
#     tags = TagSerializer(many=True, read_only=True)
#     author = UserSerializer(many=False, read_only=True)
#     is_favorited = serializers.SerializerMethodField()
#     is_in_shopping_cart = serializers.SerializerMethodField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'ingredients', 'tags', 'author', 'image', 'name', 'text',
#             'cooking_time', 'is_in_shopping_cart', 'is_favorited'
#         )
#         read_only_fields = fields

#     def get_is_favorited(self, obj):
#         user = self.context['request'].user
#         return (
#             user.is_authenticated
#             and Favorite.objects.filter(user=user, recipe=obj).exists()
#         )

#     def get_is_in_shopping_cart(self, obj):
#         user = self.context['request'].user
#         return (
#             user.is_authenticated
#             and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
#         )


class CookingTimeSerializer(serializers.Serializer):
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

    default_error_messages = {
        'incorrect_type': (
            'Передан некорректный тип данных в {item}. '
            'Ожидалось целое число, но была получена строка {input_type}.'
        ),
        'out_of_range': (
            '{item} вне диапазона. Должно быть между {min} и {max}.'
        )
    }

    def to_internal_value(self, data):
        hours, minutes = data.get('hours'), data.get('minutes')
        if not isinstance(hours, int):
            self.fail(
                'incorrect_type',
                item='hours',
                input_type=type(hours).__name__
            )

        if not isinstance(minutes, int):
            self.fail(
                'incorrect_type',
                item='minutes',
                input_type=type(minutes).__name__
            )

        if not (0 <= hours <= MAX_HOURS):
            self.fail(
                'out_of_range',
                item='Minutes',
                min=0,
                max=MAX_HOURS
            )

        if not (0 <= minutes <= 59):
            self.fail('out_of_range', item='Minutes', min=0, max=59)

        value = to_minutes(hours, minutes)

        if not (MIN_COOKING_TIME <= value <= MAX_COOKING_TIME):
            self.fail(
                'out_of_range',
                item='Cooking_time',
                min=str(MIN_COOKING_TIME) + ' мин',
                max=str(MAX_HOURS) + ' ч'
            )

        return value

    def to_representation(self, value):
        return from_minutes(value)


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=False)

    class Meta:
        model = RecipeImage
        fields = (
            'image', 'is_cover'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'measurement_unit', 'amount')


class SlugCreatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            value, _ = queryset.get_or_create(**{self.slug_field: data})
            return value
        except (TypeError, ValueError):
            self.fail('invalid')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=False, required=True, source='recipe_ingredients'
    )
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

    default_error_messages = {
        'covers_out_of_range': (
            'Неправильное кол-во обложек. '
            'У рецепта должна быть одна обложка.'
        ),
        'no_data': (
            'Не было передано ни одного {name}, '
            'должно быть мин 1.'
        ),
        'too_many': 'Слишком много {name} (макс {max}).',
    }

    class Meta:
        model = Recipe
        fields = (
            'title', 'description', 'servings', 'cooking_time',
            'cuisine', 'ending_phrase', 'images', 'video', 'tags',
            'selections', 'ingredients', 'author'
        )

    def set_recipe_relation(self, recipe, objs_data, model) -> None:
        objs = [model(
            recipe=recipe,
            **data
        ) for data in objs_data]

        model.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        images = validated_data.pop('images')
        tags = try_pop_item(validated_data, 'tags')
        selections = try_pop_item(validated_data, 'selections')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.selections.set(selections)

        self.set_recipe_relation(recipe, ingredients, RecipeIngredient)
        self.set_recipe_relation(recipe, images, RecipeImage)

        return recipe

    def validate_images(self, data):
        if not data:
            self.fail('no_data', name='изображения')

        covers_sum = sum([image.get('is_cover') for image in data])

        if covers_sum != 1:
            self.fail('covers_out_of_range')

        return data

    def validate_tags(self, data):
        if len(data) > 10:
            self.fail('too_many', name='тегов', max=MAX_TAGS_AMOUNT)

        return data

    def validate_ingredients(self, data):
        if not data:
            self.fail('no_data', name='ингредиента')

        return data

    # def update(self, instance, validated_data):
    #     if 'recipe_ingredients' in validated_data:
    #         RecipeIngredient.objects.filter(
    #             recipe=instance
    #         ).delete()
    #         ingredients_data = validated_data.pop('recipe_ingredients')
    #         self.set_ingredients(instance, ingredients_data)

    #     if 'tags' in validated_data:
    #         tags = validated_data.pop('tags')
    #         instance.tags.set(tags)

    #     return super().update(instance, validated_data)

    # def to_representation(self, instance):
    #     return RecipeRepresentationSerializer(
    #         instance,
    #         context={'request': self.context.get('request')}
    #     ).data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), required=False
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в избранное.'
            )
        ]

#     def to_representation(self, instance):
#         return RecipeListSerializer(
#             instance.recipe,
#             context={'request': self.context.get('request')}
#         ).data


class RecipeListSerializer(serializers.ModelSerializer):
    ...

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'name', 'image', 'cooking_time'
#         )


class UserListSerializer(UserCreateSerializer):
    ...

#     class Meta:
#         model = User
#         fields = (
#             'id', 'username', 'password', 'email', 'first_name', 'last_name'
#         )
#         read_only_fields = ('id',)


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
