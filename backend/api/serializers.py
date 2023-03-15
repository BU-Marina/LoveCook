from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Follow

RECIPES_LIMIT_DEFAULT = '6'

User = get_user_model()


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
#             'id', 'name', 'color', 'slug'
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ...
#     id = serializers.PrimaryKeyRelatedField(
#         read_only=False,
#         queryset=Ingredient.objects.all(),
#         source='ingredient.id'
#     )
#     # id = serializers.IntegerField(
#     #     read_only=False, source='ingredient.id'
#     # )
#     name = serializers.CharField(
#         read_only=True, source='ingredient.name'
#     )
#     measurement_unit = serializers.CharField(
#         read_only=True, source='ingredient.measurement_unit'
#     )

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'measurement_unit', 'amount')
#         read_only_fields = ('name', 'measurement_unit')


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


class RecipeSerializer(serializers.ModelSerializer):
    # ingredients = RecipeIngredientSerializer(
    #     many=True, read_only=False, source='recipe_ingredients'
    # )
    # tags = serializers.PrimaryKeyRelatedField(
    #     many=True, read_only=False,
    #     queryset=Tag.objects.values_list('id', flat=True)
    # )
    # image = Base64ImageField(required=True, read_only=False)

    class Meta:
        model = Recipe
        fields = (
            'title', 'description'
        )

    # def validate(self, data):
    #     if not data['recipe_ingredients']:
    #         raise serializers.ValidationError("Список ингредиентов пустой.")

    #     if not data['tags']:
    #         raise serializers.ValidationError("Список тегов пустой.")

    #     if len(data['tags']) != len(set(data['tags'])):
    #         raise serializers.ValidationError("Теги повторяются.")

    #     ingredints = [
    #         data['ingredient']['id'] for data in data['recipe_ingredients']
    #     ]
    #     if len(ingredints) != len(set(ingredints)):
    #         raise serializers.ValidationError("Ингредиенты повторяются.")

    #     return data

    # def set_ingredients(self, recipe, ingredients):
    #     objs = [RecipeIngredient(
    #         recipe=recipe,
    #         ingredient=data['ingredient']['id'],
    #         amount=int(data['amount'])
    #     ) for data in ingredients]

    #     return RecipeIngredient.objects.bulk_create(objs)

    # def create(self, validated_data):
    #     ingredients_data = validated_data.pop('recipe_ingredients')
    #     tags = validated_data.pop('tags')

    #     recipe = Recipe.objects.create(**validated_data)

    #     self.set_ingredients(recipe, ingredients_data)
    #     recipe.tags.set(tags)

    #     return recipe

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


class RecipeListSerializer(serializers.ModelSerializer):
    ...

#     class Meta:
#         model = Recipe
#         fields = (
#             'id', 'name', 'image', 'cooking_time'
#         )


class FavoriteSerializer(serializers.ModelSerializer):
    ...
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

#     class Meta:
#         model = Favorite
#         fields = ('user', 'recipe')
#         read_only_fields = ('user', 'recipe',)
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Favorite.objects.all(),
#                 fields=('user', 'recipe'),
#                 message='Вы уже добавили этот рецепт в избранное'
#             )
#         ]

#     def to_representation(self, instance):
#         return RecipeListSerializer(
#             instance.recipe,
#             context={'request': self.context.get('request')}
#         ).data


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
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

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
