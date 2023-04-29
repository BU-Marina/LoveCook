import random

from django.contrib.auth import get_user_model

# from django_filters.rest_framework import DjangoFilterBackend
from dj_rql.drf import RQLFilterBackend
# from dj_rql.drf.compat import DjangoFiltersRQLFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated  # AllowAny
from rest_framework.response import Response

from recipes.models import FavoriteRecipe, Recipe, Selection

from .filters import RecipeFilters
from .pagination import CursorSetPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, RecipeListSerializer,
                          RecipeSerializer, SelectionListSerializer,
                          SelectionSerializer, RecipeIngredientReprSerializer)

# from django.http import HttpResponse


# from users.models import Follow


User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    permission_classes = [
        # IsAuthorOrReadOnly,
        IsAuthenticated,
    ]
    pagination_class = CursorSetPagination
    filter_backends = (RQLFilterBackend, filters.OrderingFilter)
    rql_filter_class = RecipeFilters
    ordering_fields = ['created']
    ordering = ('-created',)
    # filter_backends = [
    #     filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend
    # ]
    # filterset_class = RecipeFilter

    # def get_permissions(self):
    #     if self.action == 'download_shopping_cart':
    #         return (IsAuthenticated(),)
    #     return super().get_permissions()

    def get_serializer_class(self):
        # if self.action == 'shopping_cart':
        #     return ShoppingCartSerializer
        if self.action == 'list':
            return RecipeListSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        return RecipeSerializer

    # def get_queryset(self):
    #     if self.action == 'shopping_cart':
    #         return ShoppingCart.objects.all()
    #     if self.action == 'download_shopping_cart':
    #         return RecipeIngredient.objects.filter(
    #             recipe__shoppingcart__user=self.request.user
    #         )
    #     return Recipe.objects.all()

    def user_recipe_relation(self, request, pk, **kwargs):
        model = kwargs.get('model')
        not_exist_message = kwargs.get('not_exist_message')

        if request.method == 'POST':
            serializer = self.get_serializer(data={
                'recipe': pk
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=pk)

            try:
                relation = model.objects.get(
                    user=user,
                    recipe=recipe
                )
            except model.DoesNotExist:
                raise ValidationError(not_exist_message)

            self.perform_destroy(relation)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # @action(methods=['post', 'delete'], detail=True)
    # def shopping_cart(self, request, *args, **kwargs):
    #     return self.user_recipe_relation(
    #         request, kwargs, model=ShoppingCart,
    #         not_exist_message=(
    #             'Этот рецепт уже не находится в вашем'
    #             'списке покупок.'
    #         )
    #     )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, *args, **kwargs):
        return self.user_recipe_relation(
            request, kwargs.get('pk'), model=FavoriteRecipe,
            not_exist_message='Этот рецепт уже не находится у вас в избранном.'
        )

    @action(methods=['get'], detail=False)
    def random(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        recipe = random.choice(queryset)
        serializer = RecipeListSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def ingredients(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
        ingredients = recipe.ingredients_info.all()
        serializer = RecipeIngredientReprSerializer(
            ingredients, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(methods=['get'], detail=False)
    # def download_shopping_cart(self, request, *args, **kwargs):
    #     recipes_ingredients = self.get_queryset()
    #     recipes = recipes_ingredients.values(
    #         'recipe__name',
    #         'recipe__author__username'
    #     ).distinct()
    #     ingredients = recipes_ingredients.values(
    #         'ingredient__name',
    #         'ingredient__measurement_unit'
    #     ).annotate(amount=Sum('amount'))

    #     shoppingcart = 'Список ингредиентов к покупке:\n'
    #     shoppingcart += '\n'.join([
    #         f'• {ingredient["ingredient__name"]}'
    #         f' ({ingredient["ingredient__measurement_unit"]})'
    #         f' - {ingredient["amount"]}'
    #         for ingredient in ingredients
    #     ])
    #     shoppingcart += '\n\nСписок составлен для следующих рецептов:\n'
    #     shoppingcart += '\n'.join([
    #         f'• {recipe["recipe__name"]}'
    #         f' - {recipe["recipe__author__username"]}'
    #         for recipe in recipes
    #     ])
    #     shoppingcart += '\n\n---'
    #     shoppingcart += '\nFoodgram | Продуктовый Помощник'

    #     filename = '{}_shopping_cart.txt'.format(self.request.user)
    #     response = HttpResponse(
    #         shoppingcart, content_type='text.txt; charset=utf-8'
    #     )
    #     response['Content-Disposition'] = (
    #         'attachment; filename={}'.format(filename)
    #     )
    #     return response


class SelectionViewSet(viewsets.ModelViewSet):
    queryset = Selection.objects.all()
    serializer_class = SelectionSerializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    permission_classes = [
        IsAuthorOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action == 'list':
            return SelectionListSerializer
        return SelectionSerializer

    @action(methods=['get'], detail=True, url_path='random-recipe')
    def random_recipe(self, request, *args, **kwargs):
        selection = get_object_or_404(Selection, pk=kwargs.get('pk'))
        queryset = self.filter_queryset(selection.recipes.all())
        recipe = random.choice(queryset)
        serializer = RecipeListSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    ...
#     queryset = Tag.objects.all()
#     serializer_class = TagSerializer
#     permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    ...
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
#     permission_classes = [
#         AllowAny,
#     ]
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = IngredientFilter


class CustomUserViewSet(UserViewSet):
    ...
#     permission_classes = [
#         AllowAny,
#     ]
#     pagination_class = LimitPagination

#     def get_permissions(self):
#         if self.action in [
#             'me', 'set_password', 'logout', 'subscriptions', 'subscribe'
#         ]:
#             return (IsAuthenticated(),)
#         return super().get_permissions()

#     def get_serializer_class(self):
#         if self.action == 'subscribe':
#             return SubscribeSerializer
#         if self.action == 'subscriptions':
#             return SubscriptionsSerializer
#         return super().get_serializer_class()

#     def get_queryset(self):
#         if self.action == 'subscribe':
#             return Follow.objects.all()
#         if self.action == 'subscriptions':
#             return User.objects.filter(following__user=self.request.user)
#         return User.objects.all()

#     @action(methods=['get'], detail=False)
#     def subscriptions(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         page = self.paginate_queryset(queryset)
#         serializer_context = {'request': request}
#         serializer = self.get_serializer(
#             page, context=serializer_context, many=True
#         )
#         return self.get_paginated_response(serializer.data)

#     @action(methods=['post', 'delete'], detail=True)
#     def subscribe(self, request, *args, **kwargs):
#         user = self.request.user
#         author_id = kwargs.get('id')
#         author = get_object_or_404(User, pk=author_id)

#         if request.method == 'POST':
#             serializer = self.get_serializer(data={
#                 'user': user.id,
#                 'following': author.id
#             })
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         if request.method == 'DELETE':
#             try:
#                 subscription = Follow.objects.get(
#                     user=user,
#                     following=author
#                 )
#             except Follow.DoesNotExist:
#                 raise ValidationError('Вы уже не подписаны на этого автора.')

#             self.perform_destroy(subscription)
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
