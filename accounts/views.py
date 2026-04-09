from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm


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
