from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'author', 'pub_date')
#     list_filter = ('name', 'author', 'tags')
#     readonly_fields = ('favorited_by',)

#     def favorited_by(self, obj):
#         return obj.favorited.count()


# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'measurement_unit')
#     list_filter = ('name',)

admin.site.register(Recipe)

# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Ingredient, IngredientAdmin)
# admin.site.register(RecipeIngredient)
# admin.site.register(Tag)
# admin.site.register(Favorite)
# admin.site.register(ShoppingCart)
