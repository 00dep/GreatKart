from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('search/', views.store, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('<slug:category_slug>/', views.products_by_category, name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]