import difflib

from icecream import ic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.department.marketing_channel.models import MarketingChannel
from data.lid.new_lid.models import Lid
from data.parents.models import Relatives
from data.student.subject.models import Subject


class LidWebhook(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if not data:
            return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)
        marketing_channel=None
        if data.get("channel") and data["channel"] == "Web site":
            marketing_channel = MarketingChannel.objects.filter(name="Web site").first()
        if data.get("channel") and data["channel"] == "bot":
            marketing_channel = MarketingChannel.objects.filter(name="Olimpiadalar").first()
        if not data.get("channel"):
            return Response({'error': 'Marketing channel not found'}, status=status.HTTP_400_BAD_REQUEST)

        # Always initialize subject as None
        subject = None

        if data.get("subject"):
            subject_name = data.get("subject", "").strip().lower()
            all_subjects = Subject.objects.all()

            best_match = difflib.get_close_matches(subject_name, [s.name.lower() for s in all_subjects], n=1, cutoff=0.5)

            if best_match:
                subject = next((s for s in all_subjects if s.name.lower() == best_match[0]), None)

        lid = Lid.objects.create(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            marketing_channel=marketing_channel,
            photo=None,
            subject=subject,
            filial=None,
            lid_stage_type="NEW_LID",
            lid_stages="YANGI_LEAD",
            call_operator=None,
            service_manager=None,
            sales_manager=None,
            student=None
        )

        if data.get("parents_name"):
            ic(data['parents_number'])
            Relatives.objects.create(
                name=data.get("parents_name"),
                phone=data.get('parents_number'),
                lid=lid,
                student=None
            )

        lid.file.set([])

        return Response({'status': 'Thank youu mann!'}, status=status.HTTP_201_CREATED)