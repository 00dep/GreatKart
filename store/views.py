from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, JsonResponse
from store.models import Product
from category.models import Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Variation, Order, OrderProduct, Payment
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.core.exceptions import ObjectDoesNotExist
import datetime
import json
from django.conf import settings
import stripe
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def store(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    keyword = request.GET.get('keyword')
    if keyword:
        products = products.filter(name__icontains=keyword)

    product_count = products.count()

    paginator = Paginator(products, 2)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'categories': categories,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def products_by_category(request, category_slug):
    return store(request, category_slug=category_slug)


def signin(request):
    return redirect('accounts_login')


def register(request):
    return redirect('accounts_register')


def cart(request):
    return render(request, 'store/cart.html')


def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        colors = Variation.objects.filter(product=product, variation_category='color', is_active=True)
        sizes = Variation.objects.filter(product=product, variation_category='size', is_active=True)
    except Product.DoesNotExist:
        raise Http404("Product not found")

    context = {
        'product': product,
        'colors': colors,
        'sizes': sizes,
    }
    return render(request, 'store/product_detail.html', context)


@login_required(login_url='accounts_login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)


@login_required(login_url='accounts_login')
def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    if not cart_items.exists():
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        except Cart.DoesNotExist:
            cart_items = CartItem.objects.none()

    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store:store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        data = Order()
        data.user = current_user
        data.first_name = request.POST.get('first_name')
        data.last_name = request.POST.get('last_name')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.address_line_1 = request.POST.get('address_line_1')
        data.address_line_2 = request.POST.get('address_line_2')
        data.country = request.POST.get('country')
        data.state = request.POST.get('state')
        data.city = request.POST.get('city')
        data.order_note = request.POST.get('order_note')
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
            'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        }
        return render(request, 'store/payments.html', context)
    else:
        return redirect('store:checkout')


def payments(request):
    order = Order.objects.get(user=request.user, is_ordered=False)
    payment = Payment(
        user=request.user,
        payment_id=request.POST.get('payment_id'),
        payment_method=request.POST.get('payment_method'),
        amount_paid=order.order_total,
        status=request.POST.get('status'),
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

    product = Product.objects.get(id=item.product_id)
    product.stock -= item.quantity
    product.save()

    CartItem.objects.filter(user=request.user).delete()

    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


@login_required(login_url='accounts_login')
def create_checkout_session(request):
    if request.method == 'POST':
        order = Order.objects.get(user=request.user, is_ordered=False)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card', 'upi'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': f'Order #{order.order_number}',
                        },
                        'unit_amount': int(order.order_total * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri('/store/order_complete/'),
            cancel_url=request.build_absolute_uri('/store/checkout/'),
            metadata={
                'order_id': order.id,
            },
        )

        return JsonResponse({'id': checkout_session.id})
    return JsonResponse({'error': 'Invalid request'})


@login_required(login_url='accounts_login')
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'store/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
