from django.urls import include, path

from .views import (MasteringList, MasteringNoPG, MasteringDetail, MasteringQuizFilter, MasteringStudentFilter,
                    StuffMasteringList, MasteringTeachersList, TeacherMasteringList)

urlpatterns = [
    path('', MasteringList.as_view(), name='mastering_list'),
    path('<uuid:pk>', MasteringDetail.as_view(), name='mastering_detail'),
    path("no-pg/", MasteringNoPG.as_view(), name='mastering_nopg'),

    path("quiz/<uuid:pk>/", MasteringQuizFilter.as_view(), name='mastering_quiz'),

    path("student/", MasteringStudentFilter.as_view(), name='mastering_student'),

    path("employee/", StuffMasteringList.as_view(), name='mastering_list'),
    path("employee/<uuid:pk>/", MasteringTeachersList.as_view(), name='mastering_list'),
    path("stuff/<uuid:pk>/", TeacherMasteringList.as_view(), name='mastering_detail'),
]