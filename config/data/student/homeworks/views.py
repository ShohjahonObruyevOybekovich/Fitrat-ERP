from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from data.student.groups.models import Group
from data.student.homeworks.models import Homework, Homework_history
from data.student.homeworks.serializers import HomeworkSerializer, HomeworksHistorySerializer


# Create your views here.
class HomeworkListCreateView(ListCreateAPIView):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group = self.request.query_params.get('group')
        course = self.request.query_params.get('course')  # ✅ fix here
        theme = self.request.query_params.get('theme')
        choice = self.request.query_params.get('choice')

        # is_active = self.request.GET.get('is_active')
        queryset = Homework.objects.all()

        # if is_active:
            # queryset = queryset.filter(is_active=is_active.capitalize())
        if choice:
            queryset = queryset.filter(choice=choice)
        if group:
            queryset = queryset.filter(theme__course=Group.objects.get(id=group).course)

        if course:
            queryset = queryset.filter(theme__course__id=course)

        if theme:
            queryset = queryset.filter(theme__id=theme)
        return queryset.order_by("theme__created_at")

class HomeworkListNoPgCreateView(ListAPIView):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        group = self.request.query_params.get('group')
        course = self.request.query_params.get('course')  # ✅ fix here
        theme = self.request.query_params.get('theme')
        choice = self.request.query_params.get('choice')

        # is_active = self.request.GET.get('is_active')
        queryset = Homework.objects.all()

        # if is_active:
            # queryset = queryset.filter(is_active=is_active.capitalize())
        if choice:
            queryset = queryset.filter(choice=choice)
        if group:
            queryset = queryset.filter(theme__course=Group.objects.get(id=group).course)

        if course:
            queryset = queryset.filter(theme__course__id=course)

        if theme:
            queryset = queryset.filter(theme__id=theme)
        return queryset.order_by("theme__created_at")

    def get_paginated_response(self, data):
        return Response(data)

class HomeworkDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Homework.objects.all()
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]


class HomeworkHistoryListCreateView(ListCreateAPIView):
    queryset = Homework_history.objects.all()
    serializer_class = HomeworksHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    def get_queryset(self):
        homework = self.request.GET.get('homework', None)
        is_active = self.request.GET.get('is_active', None)
        status = self.request.GET.get('status', None)
        student = self.request.GET.get('student', None)

        queryset = Homework_history.objects.all()
        if homework:
            queryset = queryset.filter(homework__id=homework)
        if is_active:
            queryset = queryset.filter(is_active=is_active.capitalize())
        if status:
            queryset = queryset.filter(status=status)
        if student:
            queryset = queryset.filter(student__id=student) 
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class HomeworkHistoryView(RetrieveUpdateDestroyAPIView):
    queryset = Homework_history.objects.all()
    serializer_class = HomeworksHistorySerializer
    permission_classes = [IsAuthenticated]
