from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator
from decimal import *


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=250, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=4, decimal_places=2)
    topping_allowance = models.PositiveIntegerField(null=True, blank=True, default=None)
    xtra_cheese_allowance = models.BooleanField(default=False)

    def get_url(self):
        return reverse('detail', args=[self.slug])

    def __str__(self):
        return f'{self.category} {self.name}'


class Topping(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class SpecialPizza(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    is_special = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']
    
    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)
    topping_1 = models.ForeignKey(Topping, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    topping_2 = models.ForeignKey(Topping, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    topping_3 = models.ForeignKey(Topping, on_delete=models.CASCADE, null=True, blank=True, related_name='+')
    extra_cheese = models.BooleanField(default=False)

    class Meta:
        db_table = 'CartItem'

    def sub_total(self):
        return self.product.price * self.quantity

    def sub_total_extra_cheese(self):
        return (self.product.price + Decimal(0.5)) * self.quantity

    def __str__(self):
        return f'{self.product}, top1: {self.topping_1}, top2: {self.topping_2}, top3: {self.topping_3}, xtra-cheese: {self.extra_cheese}'
    
