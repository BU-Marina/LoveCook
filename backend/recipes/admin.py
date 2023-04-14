from django.contrib import admin

from .models import (Category, Cuisine, Equipment, FavoriteRecipe,
                     FavoriteSelection, Ingredient, Recipe, RecipeImage,
                     RecipeIngredient, RecommendRecipe, RecommendSelection,
                     Selection, SelectionRecipe, Step, StepImage, Tag)


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
admin.site.register(FavoriteSelection)
admin.site.register(Step)
admin.site.register(StepImage)
admin.site.register(Equipment)
admin.site.register(RecommendRecipe)
admin.site.register(RecommendSelection)
# admin.site.register(ShoppingCart)
