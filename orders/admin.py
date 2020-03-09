from django.contrib import admin

from .models import Topping, SpecialPizza, Category, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'price')
    list_display_links = ('id', 'name')
    list_editable = ('price',)
    prepopulated_fields = {'slug': ('category', 'name',)}
    list_per_page = 20


class SpecialPizzaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_special')
    list_display_links = ('id', 'name')
    list_editable = ('is_special',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Topping)
admin.site.register(SpecialPizza, SpecialPizzaAdmin)
