from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm, LoginForm
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from django.contrib.auth import login
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import Reminder, ReminderHistory
from .serializers import ReminderSerializer
from django.utils.timezone import now


# User Registration
def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect("dashboard")  # Redirect to a dashboard or home page
    else:
        form = SignUpForm()
    return render(request, "register.html", {"form": form})

# User Login
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")  # Redirect to a dashboard or home page
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

# User Logout
def logout_view(request):
    logout(request)
    return redirect("login")  # Redirect to login page

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "user": UserSerializer(user).data,
                "token": AuthToken.objects.create(user)[1]
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                "user": UserSerializer(user).data,
                "token": AuthToken.objects.create(user)[1]
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from knox.views import LogoutView as KnoxLogoutView

class LogoutAPI(KnoxLogoutView):
    permission_classes = (permissions.IsAuthenticated,)


class AddReminderAPI(APIView):
    permission_classes = [IsAuthenticated]  # User must be logged in

    def post(self, request, *args, **kwargs):
        data = request.data.copy()  # Copy request data
        data['user'] = request.user.id  # Attach logged-in user ID
        serializer = ReminderSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)  # Save reminder with the user
            return Response({"message": "Reminder added successfully!", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


#  API to Retrieve User's Reminders
class GetUserRemindersAPI(generics.ListAPIView):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]  # Ensure user is logged in

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user) 


# class EditDeleteReminderAPI(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = ReminderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Reminder.objects.filter(user=self.request.user)

#     def get_object(self):
#         return get_object_or_404(Reminder, id=self.kwargs["pk"], user=self.request.user)


class EditDeleteReminderAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        """Handles editing a reminder and saving history."""
        reminder = self.get_object()

        old_data = {
            "medicine_type": reminder.medicine_type,
            "medicine_name": reminder.medicine_name,
            "dosage": reminder.dosage,
            "start_date": reminder.start_date.strftime("%Y-%m-%d %H:%M"),
            "end_date": reminder.end_date.strftime("%Y-%m-%d %H:%M") if reminder.end_date else None,
            "reminder_interval": reminder.reminder_interval
        }

        serializer = self.get_serializer(reminder, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Save history for edit action
            ReminderHistory.objects.create(
                user=request.user,
                reminder_id=reminder.id,
                action="edit",
                old_data=old_data,
                new_data=request.data,
                timestamp=now()
            )

            return Response({"message": "Reminder updated successfully!", "data": serializer.data}, status=200)
        
        return Response(serializer.errors, status=400)

    def delete(self, request, *args, **kwargs):
        """Handles deleting a reminder and saving history."""
        reminder = self.get_object()

        old_data = {
            "medicine_type": reminder.medicine_type,
            "medicine_name": reminder.medicine_name,
            "dosage": reminder.dosage,
            "start_date": reminder.start_date.strftime("%Y-%m-%d %H:%M"),
            "end_date": reminder.end_date.strftime("%Y-%m-%d %H:%M") if reminder.end_date else None,
            "reminder_interval": reminder.reminder_interval
        }

        # Save history for delete action
        ReminderHistory.objects.create(
            user=request.user,
            reminder_id=reminder.id,
            action="delete",
            old_data=old_data,
            timestamp=now()
        )

        reminder.delete()

        return Response({"message": "Reminder deleted successfully!"}, status=200)




class ReminderHistoryAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        history = ReminderHistory.objects.filter(user=request.user).order_by("-timestamp")
        history_data = [
            {
                "action": log.action,
                "reminder_id": log.reminder_id,
                "old_data": log.old_data,
                "new_data": log.new_data if log.action == "edit" else None,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for log in history
        ]
        return Response(history_data, status=status.HTTP_200_OK)
