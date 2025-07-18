import datetime
import locale
from collections import defaultdict

from django.db.models import Q, F, Count
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Group, Room, SecondaryGroup, Day, GroupSaleStudent
from .serializers import GroupSerializer, GroupLessonSerializer, RoomsSerializer, SecondaryGroupSerializer, \
    DaySerializer, RoomFilterSerializer, GroupSaleStudentSerializer
from ..lesson.models import ExtraLesson, ExtraLessonGroup
from ..lesson.serializers import LessonScheduleSerializer, LessonScheduleWebSerializer
from ..studentgroup.models import SecondaryStudentGroup


class StudentGroupsView(ListCreateAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    search_fields = ('name', 'scheduled_day_type__name', "status", 'teacher__id',
                     'course__subject__id',)
    ordering_fields = ('name', 'scheduled_day_type', 'start_date',
                       'end_date', 'price_type', "status", 'teacher__id',
                       'course__subject__id',)
    filterset_fields = ('name', 'scheduled_day_type__name',
                        'price_type', "status", 'teacher__id',
                        'course__subject__id',)

    def get_queryset(self):
        queryset = Group.objects.all()
        teacher = self.request.GET.get('teacher', None)
        course = self.request.GET.get('course', None)
        subject = self.request.GET.get('subject', None)
        filial = self.request.GET.get('filial', None)
        day = self.request.GET.get('day', None)
        price_type = self.request.GET.get('price_type', None)
        level = self.request.GET.get('course__level__id', None)
        not_added = self.request.GET.get('not_added', None)
        student = self.request.GET.get('student', None)

        if student:
            queryset = queryset.filter(student_groups__student__id=student)

        if day == "1":
            days = []
            days.append(Day.objects.filter(name="Dushanba"))
            queryset = queryset.filter(scheduled_day_type__name__in=days)

        if day == "0":
            days = []
            days.append(Day.objects.filter(name="Seshanba"))
            queryset = queryset.filter(scheduled_day_type__name__in=days)

        if level:
            queryset = queryset.filter(level__id=level)

        if teacher:
            queryset = queryset.filter(teacher__id=teacher)
        if course:
            queryset = queryset.filter(course__id=course)
        if subject:
            queryset = queryset.filter(course__subject__id=subject)
        if filial:
            queryset = queryset.filter(filial__id=filial)

        if price_type:
            queryset = queryset.filter(price_type=price_type)
        if not_added and not_added.lower() == "true":
            queryset = queryset.exclude(status="INACTIVE")

        queryset = queryset.annotate(student_count=Count("student_groups"))
        return queryset.order_by("-student_count")


class GroupRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer


class GroupListAPIView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    pagination_class = None

    def get_serializer(self, *args, **kwargs):

        # super().get_serializer()

        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs,
                                include_only=["id", "name"])

    def get_queryset(self):
        filter = {}
        queryset = Group.objects.all()
        subject = self.request.GET.get('subject', None)
        status = self.request.GET.get('status', None)
        filial = self.request.GET.get('filial', None)
        course = self.request.GET.get('course', None)
        teacher = self.request.GET.get('teacher', None)
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)
        student = self.request.GET.get('student', None)
        not_added = self.request.GET.get('not_added', None)
        is_archived = self.request.GET.get('is_archived', None)

        if is_archived:
            filter["is_archived"] = is_archived.capitalize()
        if status:
            filter['status'] = status
        if student:
            filter["student_groups__student__id"] = student
        if filial:
            filter['filial__id'] = filial
        if course:
            filter['course__id'] = course
        if teacher:
            filter['teacher__id'] = teacher
        if start_date:
            filter['created_at__gte'] = start_date
        if end_date:
            filter['created_at__lte'] = end_date
        if subject:
            queryset = queryset.filter(course__subject__id=subject)
        if not_added and not_added.lower() == "true":
            queryset = queryset.exclude(status="INACTIVE")
        return queryset.filter(**filter)

    def get_paginated_response(self, data):
        return Response(data)


class GroupLessonScheduleView(APIView):
    """
    API endpoint to get the lesson schedule for a given group ID.
    """

    def get(self, request, **kwargs):
        try:
            # Fetch the group by ID
            group = Group.objects.get(id=kwargs.get('pk'))
            # Serialize the group with the lesson schedule
            serializer = GroupLessonSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            # Return a 404 response if the group is not found
            return Response(
                {"error": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class TeachersGroupsView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        teacher_id = self.kwargs.get('pk')
        if teacher_id:
            teacher_groups = Group.objects.filter(teacher__id=teacher_id)
            return teacher_groups
        return Group.objects.none()


class RoomListAPIView(ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('room_number', 'room_filling')
    ordering_fields = ('room_number', 'room_filling')
    filterset_fields = ('room_number', 'room_filling')

    def get_queryset(self):
        filial = self.request.GET.get('filial', None)
        if filial:
            return Room.objects.filter(filial=filial)
        return Room.objects.all()  # Ensure it always returns a queryset

    def perform_create(self, serializer):
        """Automatically assign the requesting user's filial when creating a room."""
        serializer.save(filial=self.request.user.filial.first())


class RoomFilterView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomFilterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.GET.get('filial', None)
        queryset = Room.objects.filter(filial__id=filial)
        return queryset


class CheckRoomLessonScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filial = request.GET.get('filial')
        room_id = request.GET.get('room')
        date_str = request.GET.get('date')
        started_at_str = request.GET.get('started_at')
        ended_at_str = request.GET.get('ended_at')

        # Validate required fields
        if not all([room_id, date_str, started_at_str, ended_at_str]):
            return Response({'error': 'Missing required parameters'}, status=400)

        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            started_at = datetime.datetime.strptime(started_at_str, "%H:%M").time()
            ended_at = datetime.datetime.strptime(ended_at_str, "%H:%M").time()
        except ValueError:
            return Response({'error': 'Invalid date or time format'}, status=400)

        # Convert weekday to Uzbek
        weekday_name = date.strftime("%A")
        uzbek_weekdays = {
            "Monday": "Dushanba",
            "Tuesday": "Seshanba",
            "Wednesday": "Chorshanba",
            "Thursday": "Payshanba",
            "Friday": "Juma",
            "Saturday": "Shanba",
            "Sunday": "Yakshanba",
        }
        uzbek_day = uzbek_weekdays.get(weekday_name)
        if not uzbek_day:
            return Response({'error': f'Could not determine Uzbek weekday for "{weekday_name}"'}, status=400)

        try:
            day = Day.objects.get(name=uzbek_day)
        except Day.DoesNotExist:
            return Response({'error': f'Day "{uzbek_day}" not found in the database'}, status=400)

        # Calculate current week parity (0 for even, 1 for odd)
        current_week_parity = date.isocalendar()[1] % 2

        # Get all group lessons in that room, that day, overlapping in time and same week parity
        conflicting_groups = Group.objects.filter(
            room_number_id=room_id,
            start_date__lte=date,
            finish_date__gte=date,
            scheduled_day_type=day,
        ).annotate(
            start_week_parity=F('start_date__week') % 2
        ).filter(
            Q(started_at__lt=ended_at, ended_at__gt=started_at),
            start_week_parity=current_week_parity
        )

        # Extra lessons (groups)
        conflicting_extra_group_lessons = ExtraLessonGroup.objects.filter(
            room_id=room_id,
            date=date,
            started_at__lt=ended_at,
            ended_at__gt=started_at
        )

        # Extra lessons (students)
        conflicting_extra_lessons = ExtraLesson.objects.filter(
            room_id=room_id,
            date=date,
            started_at__lt=ended_at,
            ended_at__gt=started_at
        )

        # Format conflicts
        conflicts = {
            "group_lessons": GroupLessonSerializer(conflicting_groups, many=True).data,
            "extra_group_lessons": [
                {
                    "group": lesson.group.name,
                    "date": lesson.date,
                    "started_at": lesson.started_at,
                    "ended_at": lesson.ended_at
                } for lesson in conflicting_extra_group_lessons
            ],
            "extra_lessons": [
                {
                    "student": lesson.student.phone if lesson.student else None,
                    "teacher": lesson.teacher.username if lesson.teacher else None,
                    "date": lesson.date,
                    "started_at": lesson.started_at,
                    "ended_at": lesson.ended_at
                } for lesson in conflicting_extra_lessons
            ]
        }

        if any([
            conflicting_groups.exists(),
            conflicting_extra_group_lessons.exists(),
            conflicting_extra_lessons.exists()
        ]):
            return Response({'available': False, 'conflicts': conflicts})

        return Response({'available': True})


class RoomRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RoomsSerializer


class RoomNoPG(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('room_number', 'room_filling')
    ordering_fields = ('room_number', 'room_filling')
    filterset_fields = ('room_number', 'room_filling')
    pagination_class = None

    def get_queryset(self):
        filial = self.request.GET.get('filial', None)
        if filial:
            return Room.objects.filter(filial=filial)
        return Room.objects.filter(filial=self.request.user.filial.first())

    def get_paginated_response(self, data):
        return Response(data)


from django.utils.dateparse import parse_date


class SecondaryGroupsView(ListCreateAPIView):
    queryset = SecondaryGroup.objects.all()
    serializer_class = SecondaryGroupSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    search_fields = ('name', 'scheduled_day_type__name')
    ordering_fields = ('name', 'scheduled_day_type', 'start_date', 'end_date')
    filterset_fields = ('name', 'scheduled_day_type')

    def get_queryset(self):
        queryset = SecondaryGroup.objects.all()
        start_date = parse_date(self.request.GET.get('start_date')) if self.request.GET.get(
            'start_date') else None
        end_date = parse_date(self.request.GET.get('end_date')) if self.request.GET.get(
            'end_date') else None
        teacher = self.request.GET.get('teacher')
        course = self.request.GET.get('course')
        filial = self.request.GET.get('filial')

        if filial:
            queryset = queryset.filter(filial__id=filial)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        if teacher:
            queryset = queryset.filter(teacher__id=teacher)
        if course:
            queryset = queryset.filter(group__course__id=course)

        queryset = queryset.annotate(student_count=Count('secondarystudentgroup')).order_by('-student_count')
        return queryset


class SecondaryGroupRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SecondaryGroup.objects.all()
    serializer_class = SecondaryGroupSerializer
    permission_classes = [IsAuthenticated]


class SecondaryNoPG(ListAPIView):
    queryset = SecondaryGroup.objects.all()
    serializer_class = SecondaryGroupSerializer

    def get_queryset(self):
        queryset = SecondaryGroup.objects.all()

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        teacher = self.request.GET.get('teacher')
        course = self.request.GET.get('course')
        filial = self.request.GET.get('filial')

        # Apply filters correctly
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        if teacher:
            queryset = queryset.filter(teacher__id=teacher)
        if course:
            queryset = queryset.filter(group__course__id=course)

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class DaysAPIView(ListCreateAPIView):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated]


class DaysNoPG(ListAPIView):
    queryset = Day.objects.all()
    serializer_class = DaySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_paginated_response(self, data):
        return Response(data)


class GroupSchedule(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Group.objects.all()
        start_date = self.request.GET.get('from', None)
        end_date = self.request.GET.get('to', None)

        filial = self.request.user.filial
        room_id = self.request.GET.get('room')
        if room_id:
            return (queryset.filter(
                room_number=room_id,
                room_number__filial=filial,
            ).order_by('started_at'))

        if start_date and end_date:
            return (queryset.filter(
                room_number=room_id,
                room_number__filial=filial,
                created_at__gte=start_date,
                created_at__lte=end_date,
            ).order_by('started_at'))
        return queryset


class LessonScheduleListApi(ListAPIView):
    serializer_class = LessonScheduleSerializer
    queryset = Group.objects.filter(status="ACTIVE")
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Apply filters
        teacher = request.GET.get('teacher')
        name = request.GET.get('name')
        subject = request.GET.get('subject')
        room = request.GET.get('room')
        date_filter = request.GET.get('date', None)
        date_filter = datetime.datetime.strptime(date_filter, "%d-%m-%Y").date() if date_filter else None

        if name:
            queryset = queryset.filter(name=name)
        if subject:
            queryset = queryset.filter(course__subject__id=subject)
        if room:
            queryset = queryset.filter(room_number__id=room)
        if teacher:
            queryset = queryset.filter(teacher__id=teacher)

        # Now serialize the filtered queryset
        serializer = self.get_serializer(queryset, many=True)

        lessons_by_date = defaultdict(list)

        for item in serializer.data:
            days = item.get('days', [])
            for day in days:
                lesson_date = datetime.datetime.strptime(day['date'], "%d-%m-%Y").date()
                if date_filter and lesson_date != date_filter:
                    continue
                lessons_by_date[lesson_date].extend(day['lessons'])

        # Extra lessons (group-based)
        extra_lessons_group = ExtraLessonGroup.objects.filter(
            group__in=queryset,
            created_at__gte=datetime.date.today(),
        )

        for extra in extra_lessons_group:
            lesson_date = extra.date
            if date_filter and lesson_date != date_filter:
                continue
            lesson_data = {
                "subject": extra.group.course.subject.name if extra.group.course and extra.group.course.subject else None,
                "subject_label": extra.group.course.subject.label if extra.group.course and extra.group.course.subject else None,
                "teacher_name": f"{extra.group.teacher.first_name if extra.group.teacher.first_name else ''} {extra.group.teacher.last_name if extra.group.teacher else ''}",
                "room": extra.group.room_number.room_number if extra.group.room_number else None,
                "name": extra.group.name,
                "status": "Extra_lessons",
                "started_at": extra.started_at.strftime('%H:%M') if extra.started_at else None,
                "ended_at": extra.ended_at.strftime('%H:%M') if extra.ended_at else None,
            }

            lessons_by_date[lesson_date].append(lesson_data)

        # Extra lessons (individual)
        extra_lessons_individual = ExtraLesson.objects.filter(
            date__gte=datetime.date.today(),
        )

        for extra in extra_lessons_individual:
            lesson_date = extra.date
            if date_filter and lesson_date != date_filter:
                continue
            lesson_data = {
                "name": f"{extra.student.first_name} {extra.student.last_name}" if extra.student else None,
                "comment": extra.comment,
                "teacher_name": f"{extra.teacher.first_name} {extra.teacher.last_name}" if extra.teacher else None,
                "status": "Extra_lessons",
                "room": extra.room.room_number if extra.room else None,
                "started_at": extra.started_at.strftime('%H:%M') if extra.started_at else None,
                "ended_at": extra.ended_at.strftime('%H:%M') if extra.ended_at else None,
                "is_payable": extra.is_payable,
                "is_attendance": extra.is_attendance,
            }

            lessons_by_date[lesson_date].append(lesson_data)

        # Sort and return
        sorted_dates = sorted(lessons_by_date.keys())
        sorted_lessons = []
        for lesson_date in sorted_dates:
            lessons = lessons_by_date[lesson_date]
            lessons.sort(key=lambda x: x.get("started_at"))
            sorted_lessons.append({
                "date": lesson_date.strftime('%d-%m-%Y'),
                "lessons": lessons
            })

        return Response(sorted_lessons)


class LessonScheduleWebListApi(ListAPIView):
    serializer_class = LessonScheduleWebSerializer
    queryset = Group.objects.filter(status="ACTIVE")
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)

    ordering_fields = ['start_date', 'end_date', 'name']
    search_fields = ['name', 'teacher__id', 'course__subject__name', 'room_number']
    filterset_fields = ('name', 'teacher__id', 'course__subject__name', 'room_number')

    def get_queryset(self):
        group = self.request.GET.get('group', None)
        subject = self.request.GET.get('subject')
        teacher = self.request.GET.get('teacher')
        start_date_str = self.request.GET.get('started_at')

        queryset = self.queryset.all()

        if group:
            queryset = queryset.filter(id=group)
        if subject:
            queryset = queryset.filter(course__subject_id=subject)
        if teacher:
            queryset = queryset.filter(teacher_id=teacher)

        locale.setlocale(locale.LC_TIME, "uz_UZ.UTF-8")

        if start_date_str:
            # Convert string to datetime object
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            # Convert to Uzbek weekday name
            weekday_name = start_date.strftime("%A")  # Returns the full weekday name

            # Manually map to Uzbek names if locale doesn't support it
            uzbek_weekdays = {
                "Monday": "Dushanba",
                "Tuesday": "Seshanba",
                "Wednesday": "Chorshanba",
                "Thursday": "Payshanba",
                "Friday": "Juma",
                "Saturday": "Shanba",
                "Sunday": "Yakshanba",
            }
            weekday_name = uzbek_weekdays.get(weekday_name, weekday_name)
            ic(weekday_name.capitalize())
            days = Day.objects.get(name=weekday_name.capitalize())

            ic(weekday_name)
            if weekday_name:
                queryset = queryset.filter(scheduled_day_type=days)
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class GroupIsActiveNowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        WEEKDAYS_UZ = {
            "Monday": "dushanba",
            "Tuesday": "seshanba",
            "Wednesday": "chorshanba",
            "Thursday": "payshanba",
            "Friday": "juma",
            "Saturday": "shanba",
            "Sunday": "yakshanba"
        }
        group_id = self.kwargs.get('pk', None)
        ic(group_id)

        group = get_object_or_404(Group, id=group_id)


        now_time = datetime.datetime.now()


        print(now_time)

        current_weekday_en = now_time.strftime('%A')
        current_weekday_uz = WEEKDAYS_UZ[current_weekday_en]
        current_time = now_time.time()

        for day in group.scheduled_day_type.all():
            if day.name.lower() == current_weekday_uz:
                start = group.started_at
                end = group.ended_at

                ic(start, end, current_time)

                if start <= current_time <= end:
                    return Response({"is_scheduled_now": True})

        return Response({"is_scheduled_now": False})


class SecondaryGroupIsActiveNowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        WEEKDAYS_UZ = {
            "Monday": "dushanba",
            "Tuesday": "seshanba",
            "Wednesday": "chorshanba",
            "Thursday": "payshanba",
            "Friday": "juma",
            "Saturday": "shanba",
            "Sunday": "yakshanba"
        }

        group_id = self.kwargs.get('pk', None)
        ic(group_id)

        group = get_object_or_404(SecondaryGroup, id=group_id)

        now_time = datetime.datetime.now()
        current_weekday_en = now_time.strftime('%A')
        current_weekday_uz = WEEKDAYS_UZ[current_weekday_en]
        current_time = now_time.time()

        for day in group.scheduled_day_type.all():
            if day.name.lower() == current_weekday_uz:
                start = group.started_at
                end = group.ended_at

                ic(start, end, current_time)

                if start <= current_time <= end:
                    return Response({"is_scheduled_now": True})

        return Response({"is_scheduled_now": False})


class StudentGroupIsActiveNowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        WEEKDAYS_UZ = {
            "Monday": "dushanba",
            "Tuesday": "seshanba",
            "Wednesday": "chorshanba",
            "Thursday": "payshanba",
            "Friday": "juma",
            "Saturday": "shanba",
            "Sunday": "yakshanba"
        }

        student_id = self.kwargs.get('pk', None)
        ic(student_id)

        group = get_object_or_404(SecondaryStudentGroup, Q(student_id=student_id) | Q(lid_id=student_id))

        now_time = datetime.datetime.now()
        current_weekday_en = now_time.strftime('%A')
        current_weekday_uz = WEEKDAYS_UZ[current_weekday_en]
        current_time = now_time.time()

        for day in group.group.scheduled_day_type.all():
            if day.name.lower() == current_weekday_uz:

                start = group.group.started_at
                end = group.group.ended_at

                if start <= current_time <= end:
                    return Response({
                        "is_scheduled_now": True,
                        "group_id": group.id
                    })

        return Response({"is_scheduled_now": False, "group_id": None})


class StudentSaleGroupListCreateAPIView(ListCreateAPIView):
    queryset = GroupSaleStudent.objects.all()
    serializer_class = GroupSaleStudentSerializer

    def get_queryset(self):
        qs = GroupSaleStudent.objects.all()

        group = self.request.GET.get('group', None)
        student = self.request.GET.get('student', None)
        lid = self.request.GET.get('lid_id', None)
        if lid:
            qs = qs.filter(lid__id=lid)
        if group:
            qs = qs.filter(group__id=group)
        if student:
            qs = qs.filter(student__id=student)
        return qs

class StudentSaleGroupDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = GroupSaleStudent.objects.all()
    serializer_class = GroupSaleStudentSerializer
