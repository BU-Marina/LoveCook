from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64FileField, Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (MAX_COOKING_TIME, MIN_COOKING_TIME, Cuisine,
                            FavoriteRecipe, Recipe, RecipeImage, RecipeIngredient,
                            Selection, Tag, Step)

# from users.models import Follow

RECIPES_LIMIT_DEFAULT = '6'
MAX_HOURS = MAX_COOKING_TIME // 60
MAX_TAGS_AMOUNT = 10
MAX_IMAGES_AMOUNT = 10

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
#         many=True, read_only=True, source='ingredients_info'
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
#             and FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()
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

    def validate(self, attrs):
        super().validate(attrs)
        return to_minutes(**attrs)

    def to_representation(self, value):
        return from_minutes(value)


class ImageSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=False)

    class Meta:
        model = RecipeImage
        fields = (
            'image', 'is_cover'
        )
        extra_kwargs = {'is_cover': {'required': False, 'default': 0}}


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


class StepSerializer(serializers.ModelSerializer):

    class Meta:
        model = Step
        fields = (
            'serial_num', 'description', 'note', 'ingredients'
        )


class RecipeSerializer(serializers.ModelSerializer):
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

    default_error_messages = {
        'covers_out_of_range': (
            'Неправильное кол-во обложек. '
            'У рецепта должна быть одна обложка.'
        ),
        'out_of_range': (
            '{item} вне диапазона. Должно быть между {min} и {max}.'
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
            'selections', 'ingredients', 'steps', 'author'
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

    def validate_cooking_time(self, value):
        if not (MIN_COOKING_TIME <= value <= MAX_COOKING_TIME):
            self.fail(
                'out_of_range',
                item='Cooking_time',
                min=str(MIN_COOKING_TIME) + ' мин',
                max=str(MAX_HOURS) + ' ч'
            )

        return value

    def validate_images(self, data):
        if not data:
            self.fail('no_data', name='изображения')

        if len(data) > MAX_IMAGES_AMOUNT:
            self.fail('too_many', name='картинок', max=MAX_IMAGES_AMOUNT)

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
    #         ingredients_data = validated_data.pop('ingredients_info')
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
