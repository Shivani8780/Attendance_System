from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'attendance'

urlpatterns = [
    path('office-head-dashboard/', views.office_head_dashboard, name='office_head_dashboard'),
    path('approve-leave/<int:leave_id>/', views.approve_leave, name='approve_leave'),
    path('reject-leave/<int:leave_id>/', views.reject_leave, name='reject_leave'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('logout/', views.user_logout, name='logout'),
    path('leave-request/create/', views.leave_request_create, name='leave_request_create'),
    path('weekly-day-off/', views.weekly_day_off, name='weekly_day_off'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('office-head-login/', views.office_head_login, name='office_head_login'),
    path('office-head-register/', views.office_head_register, name='office_head_register'),
    path('leave-request/list/', views.leave_request_list, name='leave_request_list'),
    path('leave-request/cancel/<int:leave_id>/', views.leave_request_cancel, name='leave_request_cancel'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('export-attendance-records/', views.export_attendance_records, name='export_attendance_records'),
    path('export-office-head-data/', views.export_office_head_data, name='export_office_head_data'),
    path('', lambda request: redirect('attendance:login'), name='root_redirect'),
]
