from django.contrib.auth.backends import BaseBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import CustomUser


class PhoneAuthBackend(BaseBackend):
    def authenticate(self, request, phone=None, password=None):
        print(f"Attempting authentication for phone: {phone}")
        try:
            user = CustomUser.objects.get(phone=phone)

            if user.check_password(password):
                print("Authentication successful")
                return user
            elif user.is_archived:
                return Response({"Xodim arxivlanganligi sababli tizimga kirishi taqiqlanadi!"})

            else:
                print("Invalid password")
        except CustomUser.DoesNotExist:
            print("User does not exist")
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


# class StudentAuthBackend(BaseBackend):
#     def authenticate(self, request, phone=None, password=None):
#         ic(password)  # Parolni tekshiramiz
#         print(f"Attempting authentication for phone: {phone}")
#
#         try:
#             student = Student.objects.get(phone=phone)
#             user = getattr(student, 'user', None)
#             if not user:
#                 print("Student user mavjud emas!")
#                 return None
#
#             if student.is_archived:
#                 raise AuthenticationFailed("O'quvchi arxivlanganligi tufayli, tizimga kirolmaydi!")
#
#             ic(user.password)  # User passwordni tekshiramiz
#             ic(password,user.password)
#
#             if check_password(password, user.password):
#                 print("Authentication successful")
#                 return user
#             else:
#                 print("Invalid password")
#                 return None
#         except ObjectDoesNotExist:
#             print("User does not exist")
#             return None
#
#     def get_user(self, user_id):
#         try:
#             return Student.objects.get(pk=user_id).user  # Return user, not Student
#         except ObjectDoesNotExist:
#             return None


class FilialRestrictedQuerySetMixin:
    """
    Mixin to filter querysets by the user's filial and enforce data restrictions.
    """

    def get_queryset(self):
        # Get the base queryset from the view
        queryset = super().get_queryset()
        role = self.request.query_params.get('role', None)
        if role:
            return CustomUser.objects.filter(role=role)

        # Get the user's filial
        user = self.request.user
        user_filial = getattr(user, "filial", None)

        if user.role == "DIRECTOR":
            return queryset

        if not user_filial:
            return queryset.none()

        queryset = queryset.filter(filial__in=user_filial.all())

        return queryset

    def perform_create(self, serializer):
        """
        Automatically assign the user's filial during object creation.
        """
        user = self.request.user
        user_filial = getattr(user, "filial", None)

        if not user_filial:
            raise PermissionDenied("You do not have a valid filial assigned.")

        if user.role == "CALL_OPERATOR":
            return serializer.save()

        serializer.save(filial=user_filial)
