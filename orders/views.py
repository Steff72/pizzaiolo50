from django.shortcuts import render, get_object_or_404, redirect
from . models import SpecialPizza, Category, Product, Topping, Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from decimal import *


def index(request):
    special = SpecialPizza.objects.filter(is_special=True).first()
    regulars = Product.objects.filter(category=1)
    sicilians = Product.objects.filter(category=2)
    subs = Product.objects.filter(category=3)
    pastas = Product.objects.filter(category=4)
    salads = Product.objects.filter(category=5)
    dinners = Product.objects.filter(category=6)


    context = {
        'special': special,
        'regulars': regulars,
        'sicilians': sicilians,
        'subs': subs,
        'pastas': pastas,
        'salads': salads,
        'dinners': dinners
    }

    return render(request, 'orders/index.html', context)


def detail(request, slug):

    nr_topp = None

    product = get_object_or_404(Product, slug=slug)
    if product.topping_allowance:
        nr_topp = range(int(product.topping_allowance))

    toppings = Topping.objects.all()

    context = {
        'product': product,
        'toppings': toppings,
        'nr_topp': nr_topp
    }
        
    return render(request, 'orders/detail.html', context)


def _cart_id(request):
        cart = request.session.session_key
        if not cart:
                cart = request.session.create()
        return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    cart_item = CartItem.objects.create(
        product=product, quantity=1, cart=cart
    )
    if request.method == "POST":
        cart_item.extra_cheese = request.POST.get('extra_cheese')

        if product.topping_allowance:
            topping_1 = Topping.objects.get(id=request.POST.get('top0'))
            cart_item.topping_1 = topping_1

            if product.topping_allowance >= 2:
                topping_2 = Topping.objects.get(id=request.POST.get('top1'))
                cart_item.topping_2 = topping_2

                if product.topping_allowance >= 3:
                    topping_3 = Topping.objects.get(id=request.POST.get('top2'))
                    cart_item.topping_3 = topping_3
    cart_item.save()

    return redirect('cart_detail')


def increase(request, id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.quantity +=1
    cart_item.save()

    return redirect('cart_detail')


def decrease(request, id):
    cart_item = CartItem.objects.get(id=id)
    if cart_item.quantity >= 2:
        cart_item.quantity -= 1
        cart_item.save()
    
    return redirect('cart_detail')


def remove(request, id):
    cart_item = CartItem.objects.get(id=id)
    cart_item.delete()
    
    return redirect('cart_detail')


def cart_detail(request, counter=0, cart_items=None):
    total = 0

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            if cart_item.extra_cheese:
                total += (cart_item.quantity * Decimal(0.5))
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except ObjectDoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'counter': counter
    }

    return render(request, 'orders/cart.html', context)


def cart(request):
    return render(request, 'orders/cart.html')