from django.contrib.auth import get_user_model

from dj_rql.constants import FilterLookups
from dj_rql.filter_cls import RQLFilterClass
from dj_rql.qs import PrefetchRelated

from recipes.models import Recipe  # Ingredient, Tag

# from django_filters.rest_framework import FilterSet  # filters


# from rest_framework.exceptions import NotAuthenticated


User = get_user_model()


class RecipeFilters(RQLFilterClass):
    MODEL = Recipe
    SELECT = True
    FILTERS = (
        {
            'filter': 'title',
            'search': True
        },
        {
            'filter': 'description',
            'search': True
        },
        {
            'filter': 'author',
            'sources': (
                            'author__username', 'author__name',
                            'author__surname'
                        ),
            'search': True
        },
        {
            'filter': 'cooking_time',
            'lookups': {
                            FilterLookups.GT,
                            FilterLookups.LT,
                            FilterLookups.EQ,
                        }
        },
        {
            'filter': 'servings',
            'lookups': {
                            FilterLookups.GT,
                            FilterLookups.LT,
                            FilterLookups.EQ,
                        }
        },
        {
            'namespace': 'cuisine',
            'qs': PrefetchRelated('cuisine'),
            'filters': (
                {
                    'filter': 'id',
                    'lookup': FilterLookups.IN
                },
                {
                    'filter': 'name',
                    'search': True
                },
            )
        },
        {
            'filter': 'cuisine',
            'source': 'cuisine__id',
            'lookup': FilterLookups.IN
        },
        {
            'namespace': 'ingredients',
            'qs': PrefetchRelated('ingredients'),
            'filters': (
                {
                    'filter': 'id',
                    'lookups': {
                                    FilterLookups.IN,
                                    FilterLookups.OUT,
                                }
                },
                {
                    'filter': 'name',
                    'search': True
                },
            )
        },
        {
            'namespace': 'equipment',
            'qs': PrefetchRelated('equipment'),
            'filters': (
                {
                    'filter': 'id',
                    'lookups': {
                                    FilterLookups.IN,
                                    FilterLookups.OUT,
                                }
                },
                {
                    'filter': 'name',
                    'search': True
                },
            )
        },
        {
            'namespace': 'tags',
            'qs': PrefetchRelated('tags'),
            'filters': (
                {
                    'filter': 'id',
                    'lookup': FilterLookups.IN
                },
                {
                    'filter': 'name',
                    'search': True
                },
            )
        },
        {
            'namespace': 'selections',
            'qs': PrefetchRelated('selections'),
            'filters': (
                {
                    'filter': 'title',
                    'search': True
                },
                {
                    'filter': 'description',
                    'search': True
                },
            )
        },
    )


# class RecipeFilter(FilterSet):
#     ...
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


# class IngredientFilter(FilterSet):
#     ...
    # name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    # class Meta:
    #     model = Ingredient
    #     fields = ('name',)
