import os
from celery.schedules import crontab
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")

app = Celery("root")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Frequent tasks (Runs every minute)
    "send-daily-messages": {
        "task": "data.tasks.tasks.check_daily_tasks",
        "schedule": crontab(minute="*/1"),
    },
    "check-daily-leads": {
        "task": "data.lid.new_lid.tasks.check_daily_leads",
        "schedule": crontab(minute="*/1"),
    },
    "update-frozen-days": {
        "task": "data.student.student.task.update_frozen_days",
        "schedule": crontab(hour=0,minute=0),
    },
    "event-task": {
        "task": "data.event.tasks.check_today_tasks",
        "schedule": crontab(hour=9,minute=0),
    },

    # Daily tasks
    "check_attendance_daily": {
        "task": "data.finances.timetracker.tasks.check_daily_user_attendance",
        "schedule": crontab(hour=0, minute=0),
    },
    "check_today_task":{
        "task":"data.tasks.tasks.check_today_task",
        "schedule": crontab(hour=0, minute=0),
    },
    "send_daily_excel_report": {
        "task": "data.dashboard.tasks.send_daily_excel_report",
        "schedule": crontab(hour=9, minute=0),
    },
    "activate_group": {
        "task": "data.student.groups.tasks.activate_group",
        "schedule": crontab(hour=0, minute=0),
    },
    "check_exam_status": {
        "task": "data.student.quiz.tasks.handle_task_creation",
        "schedule": crontab(minute=0),
    },

    # Monthly tasks (Runs on the 1st or 28th of the month)
    "check-monthly-extra-lessons": {
        "task": "data.student.mastering.tasks.check_monthly_extra_lessons",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
    "check_accountant_kpi": {
        "task": "data.student.mastering.tasks.check_accountant_kpi",
        "schedule": crontab(day_of_month=28, hour=0, minute=0),
    },
    "check_monthly_asos5": {
        "task": "data.finance.compensation.tasks.check_monthly_student_catching_monitoring",
        "schedule": crontab(day_of_month=28, hour=0, minute=0),
    },

    # KPI Checks (Runs on the 1st of the month)
    "check_attendance_manager_kpi": {
        "task": "data.student.mastering.tasks.check_attendance_manager_kpi",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
    "check_filial_manager_kpi": {
        "task": "data.student.mastering.tasks.check_filial_manager_kpi",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
    "check_filial_director_kpi": {
        "task": "data.student.mastering.tasks.check_filial_director_kpi",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
    "check_monitoring_manager_kpi": {
        "task": "data.student.mastering.tasks.check_monitoring_manager_kpi",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),
    },
}


app.conf.timezone = "Asia/Tashkent"
