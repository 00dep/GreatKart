import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GreatKart.settings')
import django
django.setup()
from django.test import Client
from store.models import Product
from carts.models import Cart, CartItem

p = Product.objects.first()
print('product', p.id, p.category.slug, p.slug)

c = Client()
# view product page first, then add to cart in same session
r1 = c.get(f'/store/{p.category.slug}/{p.slug}/', SERVER_NAME='127.0.0.1')
print('first view status', r1.status_code)
print('session after view', dict(c.session))

r2 = c.get(f'/cart/add-cart/{p.id}/', SERVER_NAME='127.0.0.1', follow=True)
print('add_cart status', r2.status_code)
print('path after add', r2.request['PATH_INFO'] if hasattr(r2, 'request') else 'no request')
print('session after add', dict(c.session))

r3 = c.get(f'/store/{p.category.slug}/{p.slug}/', SERVER_NAME='127.0.0.1')
print('second view status', r3.status_code)
print('session after second view', dict(c.session))

s = r3.content.decode('utf-8')
idx = s.find('class="badge badge-pill badge-danger notify"')
print('idx', idx)
if idx != -1:
    print(s[idx-80:idx+120])
else:
    print('badge element not found in HTML')

print('Carts', list(Cart.objects.values('id','cart_id')))
print('Items', list(CartItem.objects.values('id','product_id','quantity','cart_id','is_active')))
