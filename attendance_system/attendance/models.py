from django.db import models
from django.contrib.auth.models import User

class AttendanceRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    def hours_worked(self):
        if self.check_in_time and self.check_out_time:
            from datetime import datetime, date, time, timedelta
            datetime_in = datetime.combine(date.min, self.check_in_time)
            datetime_out = datetime.combine(date.min, self.check_out_time)
            if datetime_out < datetime_in:
                datetime_out += timedelta(days=1)  # handle overnight shifts
            duration = datetime_out - datetime_in
            hours = duration.total_seconds() / 3600
            return round(hours, 2)
        return None

class WeeklyDayOff(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    day_off = models.CharField(max_length=3, choices=DAYS_OF_WEEK)

    def __str__(self):
        return f"{self.user.username} - {self.get_day_off_display()}"

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Sick Leave', 'Sick Leave'),
        ('Vacation', 'Vacation'),
        ('Personal Leave', 'Personal Leave'),
        ('Maternity Leave', 'Maternity Leave'),
        ('Paternity Leave', 'Paternity Leave'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    @property
    def duration(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} to {self.end_date}) - {self.status}"
