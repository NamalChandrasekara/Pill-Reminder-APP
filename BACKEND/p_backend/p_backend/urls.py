from django.urls import path
from myapp.views import EditDeleteReminderAPI, RegisterAPI, LoginAPI, LogoutAPI, AddReminderAPI, GetUserRemindersAPI, ReminderHistoryAPI

urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/logout/', LogoutAPI.as_view(), name='logout'),
    path("api/reminders/add/", AddReminderAPI.as_view(), name="add_reminder"),
    path("api/reminders/", GetUserRemindersAPI.as_view(), name="get_reminders"),
    path("api/reminders/<int:pk>/", EditDeleteReminderAPI.as_view(), name="edit_delete_reminder"),
    path("api/reminders/history/", ReminderHistoryAPI.as_view(), name="reminder_history"),

]
