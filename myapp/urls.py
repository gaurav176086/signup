from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('resend-otp/', ResendOTPView.as_view(), name='password-reset'),
    path('forgot-password/',ForgotPasswordView.as_view(),name='forgot_password'),
    path("verify-reset-otp/", VerifyResetOTPView.as_view(),name='verify_reset_otp'),
    path("reset-password/", ResetPasswordView.as_view(), name='reset_password'),
]
