from django.utils.timezone import now
from rest_framework import serializers

from data.student.attendance.models import SecondaryAttendance
from data.student.attendance.serializers import AttendanceSerializer
from data.student.groups.models import SecondaryGroup
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer
from data.student.subject.models import Theme
from data.student.subject.serializers import ThemeSerializer


class SecondaryAttendanceBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        ids = [item.get("id") for item in validated_data if item.get("id")]
        duplicates = set(
            SecondaryAttendance.objects.filter(id__in=ids).values_list("id", flat=True)
        )
        if duplicates:
            raise serializers.ValidationError(
                f"Duplicate ID(s) already exist: {', '.join(map(str, duplicates))}"
            )

        instances = []
        for item in validated_data:
            item.pop("id", None)  # Prevent manual ID conflict

            # ✅ call child.create() with already validated data
            instance = self.child.create(item)
            instances.append(instance)

        return instances


class SecondaryAttendanceSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    group = serializers.PrimaryKeyRelatedField(queryset=SecondaryGroup.objects.all(), allow_null=True)
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)

    class Meta:
        model = SecondaryAttendance
        fields = [
            "id", "student", "group", "theme", "reason",
            "remarks", "updated_at"
        ]
        list_serializer_class = SecondaryAttendanceBulkSerializer
        extra_kwargs = {
            "id": {"read_only": True}
        }

    def get_teacher(self, obj):
        # Optional helper if you use it externally
        return obj.group.teacher.full_name if obj.group and obj.group.teacher else None

    def validate(self, attrs):
        student = attrs.get("student")
        group = attrs.get("group")
        today = now().date()

        if student and group:
            already_exists = SecondaryAttendance.objects.filter(
                student=student,
                group=group,
                created_at__date=today
            ).exists()
            if already_exists:
                raise serializers.ValidationError(
                    f"Student {student} is already marked present in this group today."
                )
        return attrs

    def create(self, validated_data):
        return SecondaryAttendance.objects.create(**validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Always safe, even during bulk POST
        try:
            rep['theme'] = ThemeSerializer(instance.theme, context=self.context).data
        except Exception:
            rep['theme'] = None

        try:
            rep['student'] = StudentSerializer(instance.student, context=self.context).data
        except Exception:
            rep['student'] = None

        return rep