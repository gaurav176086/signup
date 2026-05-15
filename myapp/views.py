from django.shortcuts import render
import random
from .models import *
from .serializers import *
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status   
from django.utils.timezone import now
from django.core.mail import send_mail
# Create your views here.

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp_code=otp_code, purpose="signup")
            send_mail(
                'Your OTP Code',
                f'Your OTP code for signup is: {otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return Response({"message": "User created. Please verify your email with the OTP sent."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        
        if not email or not otp_code:
            return Response({"error": "Email and OTP code are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            otp_entry = OTP.objects.filter(user=user, otp_code=otp_code, purpose="signup", otp_verified=False).first()
            
            if otp_entry and (now() - otp_entry.created_at).total_seconds() < 60:  # OTP valid for 5 minutes
                user.is_active = True
                user.is_verified = True
                user.save()
                otp_entry.otp_verified = True
                otp_entry.save()
                return Response({"message": "Email verified successfully. You can now log in."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP code."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if user.is_verified:
                    return Response({"message": "Login successful."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Email not verified. Please verify your email before logging in."}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        

class ResendOTPView(APIView):

    def post(self, request):

        email = request.data.get("email")

        if not email:
            return Response({
                "error": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response({
                "error": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(
            user=user,
            purpose="signup",
            otp_code=otp_code
        )

        send_mail(
            subject="Resend OTP",
            message=f"Your OTP is {otp_code}",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False
        )

        return Response({
            "message": "OTP resent successfully"
        }, status=status.HTTP_200_OK)



class ForgotPasswordView(APIView):
    
    def post(self, request):

        email = request.data.get("email")

        if not email:
            return Response({
                "error": "Email is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response({
                "error": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(
            user=user,
            purpose="reset_password",
            otp_code=otp_code
        )

        send_mail(
            subject="Reset Password OTP",
            message=f"Your reset OTP is {otp_code}",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False
        )

        return Response({
            "message": "Reset OTP sent successfully"
        }, status=status.HTTP_200_OK)



class VerifyResetOTPView(APIView):
    
    def post(self, request):

        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({
                "error": "Email and OTP are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            otp_obj = OTP.objects.filter(
                user=user,
                purpose="reset_password",
                otp_code=otp,
                otp_verified=False
            ).latest("created_at")

        except User.DoesNotExist:
            return Response({
                "error": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        except OTP.DoesNotExist:
            return Response({
                "error": "Invalid OTP"
            }, status=status.HTTP_400_BAD_REQUEST)

        # OTP expiry = 5 minutes
        if (now() - otp_obj.created_at).seconds > 300:
            return Response({
                "error": "OTP expired"
            }, status=status.HTTP_400_BAD_REQUEST)

        otp_obj.otp_verified = True
        otp_obj.save()

        return Response({
            "message": "OTP verified successfully"
        }, status=status.HTTP_200_OK)



class ResetPasswordView(APIView):
    
    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({
                "error": "Email and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response({
                "error": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

        verified_otp = OTP.objects.filter(
            user=user,
            purpose="reset_password",
            otp_verified=True
        ).exists()

        if not verified_otp:
            return Response({
                "error": "Verify OTP first"
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        # Optional: delete old OTPs
        OTP.objects.filter(
            user=user,
            purpose="reset_password"
        ).delete()

        return Response({
            "message": "Password reset successful"
        }, status=status.HTTP_200_OK)