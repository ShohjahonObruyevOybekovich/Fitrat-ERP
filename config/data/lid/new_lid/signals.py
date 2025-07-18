import random
import string
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from ..new_lid.models import Lid
from ...account.models import CustomUser
from ...finances.finance.models import SaleStudent
from ...parents.models import Relatives
from ...student.attendance.models import Attendance
from ...student.student.models import Student
from ...student.student.sms import SayqalSms
from ...student.studentgroup.models import StudentGroup, SecondaryStudentGroup

sms = SayqalSms()

@receiver(pre_save, sender=Lid)
def on_pre_save(sender, instance, **kwargs):
    """
    Before saving a Lid instance, check if:
    - The lid_stage_type is changing from 'NEW_LID' to 'ORDERED_LID'
    - The call_operator field is None, then assign the first available call operator.
    """

    if not instance._state.adding:  # Ensure it's an update, not a new instance
        # Fetch previous value of `lid_stage_type` before update
        previous_instance = sender.objects.get(pk=instance.pk)

        if (
                previous_instance.lid_stage_type == "NEW_LID"
                and instance.lid_stage_type == "ORDERED_LID"
                and instance.call_operator is None
        ):
            call_operator = CustomUser.objects.filter(role="CALL_OPERATOR").first()
            if call_operator:
                instance.call_operator = call_operator  # Corrected assignment

                # Ensure atomic transaction to avoid partially updated data
                with transaction.atomic():
                    instance.save(update_fields=["call_operator"])


@receiver(post_save, sender=Lid)
def on_details_create(sender, instance: Lid, created, **kwargs):
    """
    Signal to create or update a Student when a Lid is created or updated,
    provided `is_student=True` and `phone_number` is available.
    """
    if not created:
        if instance.lid_stage_type == "NEW_LID":
            if instance.lid_stages == "YANGI_LEAD":
                instance.lid_stages = "KUTULMOQDA"
        if instance.lid_stage_type == "ORDERED_LID":
            if instance.ordered_date == None:
                instance.ordered_date = datetime.now()
            if instance.ordered_stages == "YANGI_BUYURTMA":
                instance.ordered_stages = "KUTULMOQDA"

        if instance.is_expired:
            instance.is_expired = False
            instance.save()

        if instance.is_student and instance.filial :
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            student, student_created = Student.objects.get_or_create(
                phone=instance.phone_number,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "photo": instance.photo,
                    "password": make_password(password),
                    "middle_name": instance.middle_name,
                    "date_of_birth": instance.date_of_birth,
                    "education_lang": instance.education_lang,
                    "student_type": instance.student_type,
                    "edu_class": instance.edu_class,
                    "edu_level": instance.edu_level,
                    "subject": instance.subject,
                    "balance": instance.balance,
                    "ball": instance.ball,
                    "filial": instance.filial,
                    "marketing_channel": instance.marketing_channel,
                    "call_operator": instance.call_operator,
                    "service_manager": instance.service_manager,
                    "sales_manager":instance.sales_manager,
                    "new_student_date":datetime.now(),
                },
            )

            # sms.send_sms(
            #     number=student.phone,
            #     message=f"""
            #     Fitrat Student ilovasiga muvaffaqiyatli ro‘yxatdan o‘tdingiz!
            #
            #     Login: {student.phone}
            #     Parol: {password}
            #
            #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
            #     """
            # )

            if not student_created:
                student.first_name = instance.first_name
                student.last_name = instance.last_name
                student.photo = instance.photo
                student.middle_name = instance.middle_name
                student.date_of_birth = instance.date_of_birth
                student.password = make_password(password)
                student.education_lang = instance.education_lang
                student.student_type = instance.student_type
                student.edu_class = instance.edu_class
                student.edu_level = instance.edu_level
                student.subject = instance.subject
                student.ball = instance.ball
                student.filial = instance.filial
                student.marketing_channel = instance.marketing_channel
                student.call_operator = instance.call_operator
                student.service_manager = instance.service_manager
                student.sales_manager = instance.sales_manager
                student.balance = instance.balance if instance.balance == 0 else student.balance + instance.balance
                student.save()

                # sms.send_sms(
                #     number=student.phone,
                #     message=f"""
                #     Fitrat Student ilovasida muvaffaqiyatli ma'lumotlaringiz yangilandi!
                #
                #     Login: {student.phone}
                #     Parol: {password}
                #
                #     Iltimos, ushbu ma’lumotlarni hech kimga bermang. Ilovaga kirib bolangizning natijalarini kuzatishingiz mumkin.
                #     """
                # )

            StudentGroup.objects.filter(lid=instance).update(student=student,lid=None)

            if SecondaryStudentGroup.objects.filter(lid=instance):
                SecondaryStudentGroup.objects.filter(lid=instance).update(student=student,lid=None)

            Attendance.objects.filter(lid=instance).update(student=student, lid=None)

            SaleStudent.objects.filter(lid=instance).update(student=student, lid=None)

            Relatives.objects.filter(lid=instance).update(student=student)
            # Archive the Lid
            post_save.disconnect(on_details_create, sender=Lid)
            instance.is_archived = True
            instance.save()
            post_save.connect(on_details_create, sender=Lid)

        else:
            if instance.filial is None:
                print("This lead's education branch is not updated, please add education branch.")

            post_save.disconnect(on_details_create, sender=Lid)
            instance.save()
            post_save.connect(on_details_create, sender=Lid)


@receiver(post_save, sender=Lid)
def on_expired_delete(sender, instance: Lid, created, **kwargs):
    if not created:
        if instance.is_expired:
            instance.is_expired = False
            instance.save()

    if created:
        if (instance.lid_stage_type != None and instance.lid_stages == None):
            instance.lid_stages = "YANGI_LEAD"
            instance.save()
