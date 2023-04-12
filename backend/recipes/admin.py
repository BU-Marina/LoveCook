from django.contrib import admin

from .models import (Category, Cuisine, FavoriteRecipe, Ingredient, Recipe,
                     RecipeImage, RecipeIngredient, Selection, SelectionRecipe,
                     Tag, Step, StepImage)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')
    list_filter = ('title', 'author', 'tags')
    # readonly_fields = ('favorited_by',)

    # def show_visitors(self, obj):
    #     return "\n".join([a.visitor_name for a in obj.visitor_set.all()])
    # def favorited_by(self, obj):
    #     return obj.favorited.count()


# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     list_filter = ('name',)

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeImage)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Category)
admin.site.register(Selection)
admin.site.register(SelectionRecipe)
admin.site.register(Cuisine)
admin.site.register(Tag)
admin.site.register(FavoriteRecipe)
admin.site.register(Step)
admin.site.register(StepImage)
# admin.site.register(ShoppingCart)
