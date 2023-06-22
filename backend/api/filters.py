from django.contrib.auth import get_user_model

from dj_rql.constants import FilterLookups
from dj_rql.filter_cls import RQLFilterClass
from dj_rql.qs import PrefetchRelated

from recipes.models import Recipe, Ingredient  # Tag

# from django_filters.rest_framework import FilterSet  # filters


# from rest_framework.exceptions import NotAuthenticated


User = get_user_model()


class RecipeFilters(RQLFilterClass):
    MODEL = Recipe
    SELECT = True
    DISTINCT = True
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


class IngredientFilters(RQLFilterClass):
    MODEL = Ingredient
    DISTINCT = True
    FILTERS = (
        {
            'filter': 'name',
            'search': True
        },
        {
            'filter': 'species',
            'search': True
        },
        {
            'filter': 'description',
            'search': True
        },
    )
