from django.contrib import admin

from .models import Topping, SpecialPizza, Category, Product, Order, OrderItem


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


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    fieldsets = [
        ('Product', {'fields': ['product'], }),
        ('Quantity', {'fields': ['quantity'], }),
        ('Price', {'fields': ['price'], }),
    ]
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False
    max_num = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'emailAddress', 'created', 'status']
    list_display_links = ('id',)
    search_fields = ['id', 'emailAddress']
    readonly_fields = ['id', 'token', 'total', 'emailAddress', 'created', 'status']

    fieldsets = [
        ('ORDER INFORMATION', {'fields': ['id', 'token', 'emailAddress', 'total', 'created', 'status']}),
    ]

    inlines = [
        OrderItemAdmin,
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
