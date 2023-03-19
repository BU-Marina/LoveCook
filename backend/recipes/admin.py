from django.contrib import admin

from .models import (Category, Cuisine, Favorite, Ingredient, Recipe,
                     RecipeImage, RecipeIngredient, Selection, SelectionRecipe,
                     Tag)

# class RecipeAdmin(admin.ModelAdmin):
#     list_display = ('title', 'images')
#     list_filter = ('title', 'author', 'tags')
#     readonly_fields = ('favorited_by',)

#     def favorited_by(self, obj):
#         return obj.favorited.count()


# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     list_filter = ('name',)

admin.site.register(Recipe)
admin.site.register(RecipeImage)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Category)
admin.site.register(Selection)
admin.site.register(SelectionRecipe)
admin.site.register(Cuisine)

# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
# admin.site.register(ShoppingCart)
