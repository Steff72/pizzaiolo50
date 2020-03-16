from django.shortcuts import render, get_object_or_404, redirect
from . models import SpecialPizza, Category, Product, Topping, Cart, CartItem, Order, OrderItem
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


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
    if request.session.get('cart'):
        cart = request.session['cart']
    else:
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

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_total = int(total * 100)
    description = 'Pizzaiolo50 - New Order'
    data_key = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            customer = stripe.Customer.create(
                email=email,
                source=token
            )
            charge = stripe.Charge.create(
                amount=stripe_total,
                currency='usd',
                description=description,
                customer=customer.id
            )
            # Creating the order
            try:
                order_details = Order.objects.create(
                    token=token,
                    total=total,
                    emailAddress=email,
                )
                order_details.save()

                for cart_item in cart_items:
                    # adjust price for sub with xtra cheese
                    if cart_item.extra_cheese:
                            price=(cart_item.product.price + Decimal(0.5))
                    else:
                        price=cart_item.product.price

                    # adjust product name for toppings and xtra cheese
                    product = f'{cart_item.product}'
                    if cart_item.topping_1:
                        product = f'{product}, {cart_item.topping_1}'
                        if cart_item.topping_2:
                            product = f'{product}, {cart_item.topping_2}'
                            if cart_item.topping_3:
                                product = f'{product}, {cart_item.topping_3}'
                    if cart_item.extra_cheese:
                        product = f'{product}, extra-cheese'

                    # create OrderItem
                    or_item = OrderItem.objects.create(
                        product=product,
                        quantity=cart_item.quantity,
                        price=price,
                        order=order_details
                    )
                    or_item.save()
                    cart_item.delete()

                # send email
                send_mail(
                    'Pizzaiolo50 Order',
                    'Thank you for ordering at Pizzaiolo50! \nOrder Id is ' 
                    + str(order_details.id) + '.\n It will be ready in 10 - 15 minutes.\n Enjoy your meal!',
                    'pizzaiolo50w@gmail.com',
                    [email, 'pizzaiolo50w@gmail.com'],
                    fail_silently=False,
                )
                
                return redirect('thankyou', order_details.id)
            except ObjectDoesNotExist:
                pass

        except stripe.error.CardError as e:
            return False, e

    context = {
        'cart_items': cart_items,
        'total': total,
        'counter': counter,
        'data_key': data_key,
        'stripe_total': stripe_total,
        'description': description
        }

    return render(request, 'orders/cart.html', context)


def thankyou(request, order_id):
    if order_id:
        customer_order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/thankyou.html', {'customer_order': customer_order})


@login_required(redirect_field_name='next', login_url='login')
def orderHistory(request):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order_details = Order.objects.filter(emailAddress=email)
    return render(request, 'orders/order_history.html', {'order_details': order_details})


@login_required(redirect_field_name='next', login_url='login')
def viewOrder(request, order_id):
    if request.user.is_authenticated:
        email = str(request.user.email)
        order = Order.objects.get(id=order_id, emailAddress=email)
        order_items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/order_view.html', {'order': order, 'order_items': order_items})


@login_required(redirect_field_name='next', login_url='login')
def orderList(request):
    if request.user.is_staff:
        orders = []
        open_orders = Order.objects.filter(status='Paid').order_by('created')
        for o in open_orders:
            orders.append(OrderItem.objects.filter(order=o)) 
        return render(request, 'orders/order_list.html', {'order_items': orders, 'open_orders': open_orders})
    else:
        return redirect('index')


@login_required(redirect_field_name='next', login_url='login')
def completeOrder(request, order_id):
    if request.user.is_staff:
        order = Order.objects.get(id=order_id)
        order.status = 'Ready'
        order.save()
        messages.success(request, 'Order completed')
        return redirect('order_list')
    else:
        return redirect('index')