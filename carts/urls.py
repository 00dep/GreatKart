from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('update/<int:cart_item_id>/<str:action>/', views.update_cart, name='update_cart'),
]