from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<slug>', views.detail, name='detail'),
    path('cart/add/<int:product_id>', views.add_cart, name='add_cart'),
    path('cart/increase/<int:id>', views.increase, name='increase'),
    path('cart/decrease/<int:id>', views.decrease, name='decrease'),
    path('cart/remove/<int:id>', views.remove, name='remove'),
    path('thankyou/<int:order_id>', views.thankyou, name='thankyou'),
    path('cart', views.cart_detail, name='cart_detail'),
    path('order_history', views.orderHistory, name='order_history'),
    path('order_view/<int:order_id>', views.viewOrder, name='order_view'),
    path('order_list', views.orderList, name='order_list'),
    path('complete_order/<int:order_id>', views.completeOrder, name='complete_order'),
]
