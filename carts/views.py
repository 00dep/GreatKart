from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem

def _cart_id(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []
    quantity = 1

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        for key in request.POST:
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=request.user)
        cart_item_exists = False
        for item in cart_items:
            if list(item.variations.all()) == product_variation:
                item.quantity += quantity
                item.save()
                cart_item_exists = True
                break
        if not cart_item_exists:
            cart_item = CartItem.objects.create(
                product=product,
                user=request.user,
                quantity=quantity,
            )
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()
    else:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        cart_item_exists = False
        for item in cart_items:
            if list(item.variations.all()) == product_variation:
                item.quantity += quantity
                item.save()
                cart_item_exists = True
                break
        if not cart_item_exists:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=quantity,
            )
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()

    return redirect('carts:cart')


def remove_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return redirect('carts:cart')


def update_cart(request, cart_item_id, action):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('carts:cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart_id = request.session.session_key
            if not cart_id:
                request.session.create()
                cart_id = request.session.session_key
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

    except Cart.DoesNotExist:
        pass

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
    }
    return render(request, 'store/cart.html', context)