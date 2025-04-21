from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse  # Import JsonResponse for returning JSON responses
from django.contrib.auth import logout, authenticate, login  # Import necessary functions for user authentication
from django.contrib.auth.models import User  # Import User model for registration
from django.contrib.auth.tokens import default_token_generator  # Import token generator for password reset
from django.utils.http import urlsafe_base64_encode  # Import for encoding user ID
from django.utils.encoding import force_bytes  # Import for encoding user ID
from django.core.mail import send_mail  # Import for sending emails
from django.views.decorators.csrf import csrf_exempt  # Import csrf_exempt decorator
from django.contrib import messages  # Import messages framework
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, WeeklyDayOffForm  # Import the registration and weekly day off forms
from .models import LeaveRequest, AttendanceRecord, WeeklyDayOff  # Import the LeaveRequest, AttendanceRecord, and WeeklyDayOff models
import datetime  # Import the datetime module

@login_required
def office_head_dashboard(request):
    employees = User.objects.filter(is_staff=False, is_superuser=False)
    leave_requests = LeaveRequest.objects.all().order_by('-applied_at')
    attendance_records = AttendanceRecord.objects.select_related('user').order_by('-date')
    return render(request, 'attendance/office_head_dashboard.html', {
        'employees': employees,
        'leave_requests': leave_requests,
        'attendance_records': attendance_records,
    })

@login_required
@require_POST
def approve_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.status = 'Approved'
    leave_request.save()
    return redirect('attendance:office_head_dashboard')

@login_required
@require_POST
def reject_leave(request, leave_id):
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    leave_request.status = 'Rejected'
    leave_request.save()
    return redirect('attendance:office_head_dashboard')

@login_required
def export_attendance_records(request):
    attendance_data = {
        "message": "Attendance records exported successfully."
    }
    return JsonResponse(attendance_data)

@login_required
def dashboard(request):
    attendance_records = AttendanceRecord.objects.filter(user=request.user).order_by('-date')
    # Calculate work_hours for each attendance record
    for record in attendance_records:
        if record.check_in_time and record.check_out_time:
            check_in_dt = datetime.datetime.combine(record.date, record.check_in_time)
            check_out_dt = datetime.datetime.combine(record.date, record.check_out_time)
            duration = check_out_dt - check_in_dt
            # Convert duration to hours and minutes string
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            record.work_hours = f"{hours}h {minutes}m"
        else:
            record.work_hours = "N/A"
    try:
        weekly_day_off = WeeklyDayOff.objects.get(user=request.user)
    except WeeklyDayOff.DoesNotExist:
        weekly_day_off = None
    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-applied_at')
    return render(request, 'attendance/dashboard.html', {
        'attendance_records': attendance_records,
        'weekly_day_off': weekly_day_off,
        'leave_requests': leave_requests,
    })

@login_required
def mark_attendance(request):
    today = datetime.date.today()
    record, created = AttendanceRecord.objects.get_or_create(user=request.user, date=today)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'check_in':
            if not record.check_in_time:
                record.check_in_time = datetime.datetime.now().time()
                record.save()
            return redirect('attendance:dashboard')
        elif action == 'check_out':
            if record.check_in_time and not record.check_out_time:
                record.check_out_time = datetime.datetime.now().time()
                record.save()
            return redirect('attendance:dashboard')
    return render(request, 'attendance/mark_attendance.html', {'record': record})

def user_logout(request):
    logout(request)
    return redirect('attendance:login')

from .forms import LeaveRequestForm

@login_required
def leave_request_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            return redirect('attendance:leave_request_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'attendance/leave_request_form.html', {'form': form})

@login_required
def weekly_day_off(request):
    if request.method == 'POST':
        form = WeeklyDayOffForm(request.POST)
        if form.is_valid():
            day_off = form.cleaned_data['day_off']
            weekly_day_off_obj, created = WeeklyDayOff.objects.update_or_create(
                user=request.user,
                defaults={'day_off': day_off}
            )
            return redirect('attendance:dashboard')
    else:
        try:
            weekly_day_off_obj = WeeklyDayOff.objects.get(user=request.user)
            form = WeeklyDayOffForm(initial={'day_off': weekly_day_off_obj.day_off})
        except WeeklyDayOff.DoesNotExist:
            form = WeeklyDayOffForm()
    return render(request, 'attendance/weekly_day_off.html', {'form': form})

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('attendance:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'attendance/login.html')
    return render(request, 'attendance/login.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('attendance:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'attendance/register.html', {'form': form})

def office_head_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('attendance:office_head_dashboard')
        else:
            return render(request, 'attendance/office_head_login.html', {'error': 'Invalid username or password'})
    return render(request, 'attendance/office_head_login.html')

def office_head_register(request):
    return render(request, 'attendance/office_head_register.html')

@login_required
def leave_request_list(request):
    leave_requests = LeaveRequest.objects.filter(user=request.user)
    return render(request, 'attendance/leave_request_list.html', {'leave_requests': leave_requests})

def leave_request_cancel(request, leave_id):
    leave_request = LeaveRequest.objects.get(id=leave_id)
    leave_request.delete()
    return redirect('attendance:leave_request_list')

from .forms import PasswordResetForm

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                form.add_error('email', 'No user found with this email address.')
                return render(request, 'attendance/password_reset_form.html', {'form': form})
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: /reset/{uid}/{token}/',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return render(request, 'attendance/password_reset_done.html')
    else:
        form = PasswordResetForm()
    return render(request, 'attendance/password_reset_form.html', {'form': form})

