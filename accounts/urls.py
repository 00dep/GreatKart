from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledAuthenticationForm

urlpatterns = [
    path('register/', views.register, name='accounts_register'),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=StyledAuthenticationForm,
        ),
        name='accounts_login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='home'),
        name='accounts_logout',
    ),

    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url=reverse_lazy('accounts_password_reset_done'),
        ),
        name='accounts_password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='accounts_password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts_password_reset_complete'),
        ),
        name='accounts_password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='accounts_password_reset_complete',
    ),
]