from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from store.models import Product
from carts.models import CartItem


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully. Please sign in.')
            return redirect('accounts_login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required(login_url='accounts_login')
def profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='accounts_login')
def my_orders(request):
    from store.models import Order
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)
