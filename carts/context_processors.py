from .models import Cart, CartItem

def counter(request):
    cart_count = 0
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
        cart_count = sum(item.quantity for item in cart_items)
    except Cart.DoesNotExist:
        cart_count = 0
    except Exception:
        cart_count = 0
    return {'cart_count': cart_count}