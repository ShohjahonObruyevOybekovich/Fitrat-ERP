from django.core.exceptions import FieldError
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, \
    ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lid
from .serializers import LidSerializer
from ...student.lesson.models import FirstLLesson
from ...student.student.models import Student


class LidListCreateView(ListCreateAPIView):
    serializer_class = LidSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ["first_name", "last_name", "phone_number", ]
    filterset_fields = [
        "student_type",
        "education_lang",
        "filial",
        "marketing_channel",
        "lid_stage_type",
        "lid_stages",
        "ordered_stages",
        "is_dubl",
        "is_archived",
    ]
    def get_serializer(self, *args, **kwargs):

        # super().get_serializer()

        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs,
        include_only=["id","first_name","last_name","middle_name","photo","phone_number",
                      "filial","lid_stages","lid_stage_type","ordered_stages","call_operator","sales_manager","is_archived"
                      ,"ordered_date","created_at"])

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Lid.objects.none()

        queryset = Lid.objects.all()
        filial = self.request.query_params.get("filial")

        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True)
            )
        else:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True)
            )

        # ✅ Additional Filters
        is_archived = self.request.query_params.get("is_archived")
        search_term = self.request.query_params.get("search", "")
        course_id = self.request.query_params.get("course")
        call_operator_id = self.request.query_params.get("call_operator")
        service_manager = self.request.query_params.get("service_manager")
        sales_manager = self.request.query_params.get("sales_manager")
        teacher = self.request.query_params.get("teacher")
        channel = self.request.query_params.get("channel")
        subject = self.request.query_params.get("subject")
        is_student = self.request.query_params.get("is_student")

        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if channel:
            queryset = queryset.filter(marketing_channel__id=channel)

        if service_manager:
            queryset = queryset.filter(service_manager_id=service_manager)

        if sales_manager:
            queryset = queryset.filter(sales_manager_id=sales_manager)

        if teacher:
            queryset = queryset.filter(lids_group__group__teacher_id=teacher)

        if subject:
            queryset = queryset.filter(subject_id=subject)

        if is_student == "false":
            queryset = queryset.filter(is_student=False)

        if call_operator_id:
            queryset = queryset.filter(call_operator_id=call_operator_id)

        if course_id:
            queryset = queryset.filter(lids_group__group__course_id=course_id)

        if search_term:
            try:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(phone_number__icontains=search_term)
                )
            except FieldError as e:
                print(f"FieldError: {e}")

        # ✅ Date Filtering
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        ic(start_date,end_date)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)

        return queryset


class LidRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class LidListNoPG(ListAPIView):
    queryset = Lid.objects.all()
    serializer_class = LidSerializer
    pagination_class = None

    def get_queryset(self):
        filial = self.request.query_params.get("filial")
        is_archived = self.request.query_params.get("is_archived")
        is_student = self.request.query_params.get("is_student")
        queryset = Lid.objects.all()
        if is_archived:
            queryset = queryset.filter(is_archived=is_archived.capitalize())

        if filial:
            queryset = queryset.filter(filial__id=filial)

        if is_student:
            queryset = queryset.filter(is_student=is_student.capitalize())
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class FirstLessonCreate(CreateAPIView):
    serializer_class = LidSerializer
    queryset = Lid.objects.all()
    permission_classes = [IsAuthenticated]


class ExportLidToExcelAPIView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter("is_student", openapi.IN_QUERY,
                              description="Filter by whether the lead is a student (true/false)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter("filial_id", openapi.IN_QUERY, description="Filter by filial ID",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter("lid_stage_type", openapi.IN_QUERY, description="Filter by lid stage type",
                              type=openapi.TYPE_STRING),
        ],
        responses={200: "Excel file generated"}
    )
    def get(self, request):
        # Get filters from query parameters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        lid_stage_type = request.query_params.get("lid_stage_type")
        filial = self.request.query_params.get("filial")
        is_archived = self.request.query_params.get("is_archived")
        course_id = self.request.query_params.get("course")
        call_operator_id = self.request.query_params.get("call_operator")
        service_manager = self.request.query_params.get("service_manager")
        sales_manager = self.request.query_params.get("sales_manager")
        teacher = self.request.query_params.get("teacher")
        channel = self.request.query_params.get("marketing_channel")
        subject = self.request.query_params.get("subject")
        is_student = self.request.query_params.get("is_student")

        filter = {}
        if filial:
            filter["filial__id"] = filial
        if is_archived:
            filter["is_archived"] = is_archived.capitalize()
        if course_id:
            filter["lids_group__course__id"] = course_id
        if call_operator_id:
            filter["call_operator__id"] = call_operator_id
        if service_manager:
            filter["service_manager__id"] = service_manager
        if sales_manager:
            filter["sales_manager__id"] = sales_manager
        if teacher:
            filter["lids_group__teacher__id"] = teacher
        if channel:
            filter["marketing_channel__id"] = channel
        if subject:
            filter["subject__id"] = subject
        if is_student:
            filter["is_student"] = is_student.capitalize()

        queryset = Lid.objects.filter(**filter)

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        if lid_stage_type:
            queryset = queryset.filter(lid_stage_type=lid_stage_type)

        # Create Excel workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Lids Data"

        # Define headers
        headers = [
            "Ism", "Familiya", "Telefon raqami",
            "Tug'ulgan sanasi", "O'quv tili", "O'quv sinfi",
            "Fan", "Ball", "Filial", "Marketing kanali", "Lead varonkasi",
            "Lead etapi", "Buyurtma etapi", "Arxivlangan",
            "Call Operator", "Sotuv menejeri", "O'quvchi bo'lgan", "Service manager", "Yaratilgan vaqti"
        ]
        sheet.append(headers)

        ORDERED_STAGE_LABELS = {
            "KUTULMOQDA": "Jarayonda",
            "BIRINCHI_DARSGA_KELMAGAN": "Sinov darsiga kelmagan",
            "BIRINCHI_DARS_BELGILANGAN": "Sinov darsi belgilangan",
            "YANGI_BUYURTMA": "Yangi buyurtma",
        }
        Lid_STAGE_LABELS = {
            "YANGI_LEAD": "Yangi lead",
            "KUTULMOQDA": "Jarayonda",
        }
        for lid in queryset:
            sheet.append([
                lid.first_name,
                lid.last_name,
                lid.phone_number,
                lid.date_of_birth.strftime('%d-%m-%Y') if lid.date_of_birth else "",
                "Uzbek tili" if lid.education_lang == "UZB" else "Ingliz tili" if lid.education_lang == "ENG" else "Rus tili" if lid.education_lang == "RU" else "",
                "Maktab" if lid.edu_class == "SCHOOL" else "Universitet" if lid.edu_class == "UNIVERSITY" else "Abutirent" if lid.edu_class else "",
                lid.subject.name if lid.subject else "",
                lid.ball,
                lid.filial.name if lid.filial else "",
                lid.marketing_channel.name if lid.marketing_channel else "",
                "Buyurtma yaratilgan" if lid.lid_stage_type == "ORDERED_LID" else "Yangi lead",
                Lid_STAGE_LABELS.get(lid.lid_stages, ""),
                ORDERED_STAGE_LABELS.get(lid.ordered_stages, ""),
                "Ha" if lid.is_archived else "Yo'q",
                lid.call_operator.full_name if lid.call_operator else "",
                lid.sales_manager.full_name if lid.sales_manager else "",
                "Ha" if lid.is_student else "Yo'q",
                lid.service_manager.full_name if lid.service_manager else "",
                lid.created_at.strftime('%d-%m-%Y %H:%M:%S') if lid.created_at else "",
            ])

        # Style headers
        for col_num, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.font = Font(bold=True, size=12)
            cell.alignment = Alignment(horizontal="center", vertical="center")
            sheet.column_dimensions[cell.column_letter].width = 20

        # Create the HTTP response with the Excel file
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Lids_Data.xlsx"'
        workbook.save(response)

        return response


class LidStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Lid.objects.all()

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = Lid.objects.all()

        filial = self.request.query_params.get("filial")
        is_archived = self.request.query_params.get("is_archived")
        # course_id = self.request.query_params.get("course")
        call_operator_id = self.request.query_params.get("call_operator")
        service_manager = self.request.query_params.get("service_manager")
        sales_manager = self.request.query_params.get("sales_manager")
        # teacher = self.request.query_params.get("teacher")
        # channel = self.request.query_params.get("channel")
        # subject = self.request.query_params.get("subject")
        is_student = self.request.query_params.get("is_student")

        filter = {}

        if filial:
            filter["filial__id"] = filial
        if is_archived:
            filter["is_archived"] = True
        # if course_id:
        #     filter["lids_group__course__id"] = course_id
        if call_operator_id:
            filter["call_operator__id"] = call_operator_id
        if service_manager:
            filter["service_manager__id"] = service_manager
        if sales_manager:
            filter["sales_manager__id"] = sales_manager
        # if teacher:
        #     filter["lids_group__teacher__id"] = teacher
        # if channel:
        #     filter["subject__id"] = subject
        if is_student:
            filter["is_student"] = is_student.capitalize()

        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True)
            )

        else:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True)
            )

        leads_count = queryset.filter(lid_stage_type="NEW_LID", is_archived=False, **filter).count()
        new_leads = queryset.filter(lid_stage_type="NEW_LID", lid_stages="YANGI_LEAD", is_archived=False,
                                    **filter).count()
        in_progress = queryset.filter(lid_stage_type="NEW_LID", is_archived=False, lid_stages="KUTULMOQDA",
                                      **filter).count()
        order_created = queryset.filter(is_archived=False, lid_stage_type="ORDERED_LID", **filter).exclude(
            call_operator__isnull=True).count()
        archived_new_leads = queryset.filter(is_archived=True, lid_stage_type="NEW_LID", **filter).count()

        ordered_new = queryset.filter(lid_stage_type="ORDERED_LID", is_archived=False,
                                      ordered_stages="YANGI_BUYURTMA", **filter).count()

        ordered_new_fix = queryset.filter(ordered_date__isnull=False, **filter).count()
        ordered_leads_count = queryset.filter(lid_stage_type="ORDERED_LID", is_archived=False, **filter).count()
        ordered_waiting_leads = queryset.filter(lid_stage_type="ORDERED_LID", is_archived=False,
                                                ordered_stages="KUTULMOQDA", **filter).count()
        ordered_archived = queryset.filter(is_archived=True, is_student=False, lid_stage_type="ORDERED_LID",
                                           **filter).count()
        first_lesson = queryset.filter(lid_stage_type="ORDERED_LID", is_archived=False,
                                       ordered_stages="BIRINCHI_DARS_BELGILANGAN",is_student=False, **filter).count()
        first_lesson_not = queryset.filter(lid_stage_type="ORDERED_LID", is_archived=False,
                                           ordered_stages="BIRINCHI_DARSGA_KELMAGAN", **filter).count()
        all_archived = queryset.filter(is_archived=True, is_student=False, **filter).count()
        archived_lid = queryset.filter(lid_stage_type="NEW_LID", is_student=False, is_archived=True, **filter).count()

        first_lesson_all = FirstLLesson.objects.filter(lid__lid_stage_type="ORDERED_LID", **filter).count()

        new_student = Student.objects.filter(is_archived=True,student_stage_type="NEW_STUDENT",**filter).count()
        active_student = Student.objects.filter(is_archived=True,student_stage_type="ACTIVE_STUDENT",**filter).count()

        print(f"all_archived: {all_archived}", queryset.filter(is_archived=True, is_student=False, **filter))
        print(f"active_student: {active_student}", Student.objects.filter(is_archived=True,student_stage_type="ACTIVE_STUDENT",**filter))
        print(f"new_student: {new_student}", Student.objects.filter(is_archived=True,student_stage_type="NEW_STUDENT",**filter))

        no_debt = Student.objects.filter(is_archived=True,balance__gte=100000, **filter).count()

        lead_no_debt = Lid.objects.filter(is_archived=True,is_student=False,balance__gte=100000,**filter).count()

        debt = Student.objects.filter(is_archived=True,balance__lt=100000, **filter).count()

        lead_debt = Lid.objects.filter(is_archived=True,is_student=False,balance__lt=100000, **filter).count()

        no_debt_sum = Student.objects.filter(is_archived=True,balance__gte=100000, **filter).aggregate(total=Sum("balance"))["total"] or 0
        lead_no_debt_sum = Lid.objects.filter(is_archived=True,is_student=False,balance__gte=100000, **filter).aggregate(total=Sum("balance"))["total"] or 0
        debt_sum = Student.objects.filter(is_archived=True,balance__lt=100000, **filter).aggregate(total=Sum("balance"))["total"] or 0
        lead_debt_sum = Lid.objects.filter(is_archived=True,is_student=False,balance__lt=100000, **filter).aggregate(total=Sum("balance"))["total"] or 0


        response_data = {
            "new_lid_statistics": {
                "leads_count": leads_count,
                "new_leads": new_leads,
                "in_progress": in_progress,
                "order_created": order_created,
                "archived_new_leads": archived_new_leads,
            },
            "ordered_statistics": {
                "ordered_leads_count": ordered_leads_count,
                "ordered_new": ordered_new,
                "ordered_new_fix" :ordered_new_fix,
                "ordered_waiting_leads": ordered_waiting_leads,
                "ordered_first_lesson_not_come": first_lesson_not,
                "ordered_first_lesson": first_lesson,
                "ordered_archived": ordered_archived,
                "first_lesson_all":first_lesson_all
            },
            "lid_archived": {
                "all": all_archived,
                "lid": archived_lid,
                "order": ordered_archived,
            },
            "student_archived": {
                "all":all_archived + new_student + active_student,
                "new_students": new_student,
                "active_students": active_student,
                "no-debt": no_debt + lead_no_debt,
                "debt": debt + lead_debt,
                "no_debt_sum": no_debt_sum + lead_no_debt_sum,
                "debt_sum": debt_sum + lead_debt_sum,
            }
        }

        return Response(response_data)


class BulkUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.get('lids', [])

        if not data:
            raise ValidationError("No lids data provided.")

        serializer = LidSerializer()

        try:
            updated_lids = serializer.update_bulk_lids(data)
            return Response({"message": "Bulk update successful.", "updated_lids": updated_lids},
                            status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LidStatistics(ListAPIView):
    serializer_class = LidSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ["first_name", "last_name", "phone_number", ]
    filterset_fields = [
        "student_type",
        "education_lang",
        "filial",
        "marketing_channel",
        "lid_stage_type",
        "lid_stages",
        "ordered_stages",
        "is_dubl",
        "is_archived",
    ]

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Lid.objects.none()

        queryset = Lid.objects.all()
        filial = self.request.query_params.get("filial")

        if user.role == "CALL_OPERATOR" or user.is_call_center:
            queryset = queryset.filter(
                Q(filial__in=user.filial.all()) | Q(filial__isnull=True),
                Q(call_operator=user) | Q(call_operator__isnull=True)
            )
        else:
            queryset = queryset.filter(
                Q(filial_id=filial) | Q(filial__isnull=True)
            )

        is_archived = self.request.query_params.get("is_archived")
        search_term = self.request.query_params.get("search", "")
        course_id = self.request.query_params.get("course")
        call_operator_id = self.request.query_params.get("call_operator")
        service_manager = self.request.query_params.get("service_manager")
        sales_manager = self.request.query_params.get("sales_manager")
        teacher = self.request.query_params.get("teacher")
        channel = self.request.query_params.get("channel")
        subject = self.request.query_params.get("subject")
        is_student = self.request.query_params.get("is_student")

        if is_archived == "True":
            queryset = queryset.filter(is_archived=True)

        if channel:
            queryset = queryset.filter(marketing_channel__id=channel)

        if service_manager:
            queryset = queryset.filter(service_manager_id=service_manager)

        if sales_manager:
            queryset = queryset.filter(sales_manager_id=sales_manager)

        if teacher:
            queryset = queryset.filter(lids_group__group__teacher_id=teacher)

        if subject:
            queryset = queryset.filter(subject_id=subject)

        if is_student == "false":
            queryset = queryset.filter(is_student=False)

        if call_operator_id:
            queryset = queryset.filter(call_operator_id=call_operator_id)

        if course_id:
            queryset = queryset.filter(lids_group__group__course_id=course_id)

        if search_term:
            try:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(phone_number__icontains=search_term)
                )
            except FieldError as e:
                print(f"FieldError: {e}")

        # ✅ Date Filtering
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        elif start_date:
            try:
                start_date = parse_datetime(start_date).date()
                queryset = queryset.filter(created_at__gte=start_date)
            except ValueError:
                pass
        elif end_date:
            try:
                end_date = parse_datetime(end_date).date()
                queryset = queryset.filter(created_at__lte=end_date)
            except ValueError:
                pass

        return queryset
