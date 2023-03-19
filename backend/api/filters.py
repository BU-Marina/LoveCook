from django.contrib.auth import get_user_model

from django_filters.rest_framework import FilterSet  # filters

# from rest_framework.exceptions import NotAuthenticated

# from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(FilterSet):
    ...
    # is_favorited = filters.BooleanFilter(method='filter_favorited')
    # is_in_shopping_cart = filters.BooleanFilter(
    #     method='filter_shopping_cart'
    # )
    # tags = filters.ModelMultipleChoiceFilter(
    #     field_name='tags__slug',
    #     to_field_name="slug",
    #     queryset=Tag.objects.all()
    # )
    # author = filters.ModelChoiceFilter(queryset=User.objects.all())

    # class Meta:
    #     model = Recipe
    #     fields = ['author', 'tags']

    # def filter_favorited(self, queryset, field_name, value):
    #     user = self.request.user
    #     if user.is_anonymous:
    #         raise NotAuthenticated(
    #             'Войдите или зарегистрируйтесь, '
    #             'чтобы просматривать избранное.'
    #         )
    #     if value:
    #         return queryset.filter(favorited__user=user)
    #     return queryset

    # def filter_shopping_cart(self, queryset, field_name, value):
    #     user = self.request.user
    #     if user.is_anonymous:
    #         raise NotAuthenticated(
    #             'Войдите или зарегистрируйтесь, чтобы просматривать '
    #             'свой список покупок.'
    #         )
    #     if value:
    #         return queryset.filter(shoppingcart__user=user)
    #     return queryset


class IngredientFilter(FilterSet):
    ...
    # name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    # class Meta:
    #     model = Ingredient
    #     fields = ('name',)
