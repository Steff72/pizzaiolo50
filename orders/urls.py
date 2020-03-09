from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<slug>', views.detail, name='detail'),
    path('cart/add/<int:product_id>', views.add_cart, name='add_cart'),
    path('cart/increase/<int:id>', views.increase, name='increase'),
    path('cart/decrease/<int:id>', views.decrease, name='decrease'),
    path('cart/remove/<int:id>', views.remove, name='remove'),
    path('cart', views.cart_detail, name='cart_detail'),
]
