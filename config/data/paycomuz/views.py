# payments/views.py
# django
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db.models import Q
from rest_framework import serializers
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from data.paycomuz.methods_subscribe_api import PayComResponse  # your custom PayComResponse
from data.paycomuz.serializers import GeneratePaymentLinkSerializer
from . import Paycom
from .authentication import authentication
from .check_order import CheckOrder
# project
from .models import Transaction
from .serializers.payme_operation import PaycomOperationSerialzer
from .serializers.serializers import PaycomuzSerializer
from .status import *
from ..clickuz.models import Order
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


class MerchantAPIView(APIView):
    permission_classes = [AllowAny]
    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    CHECK_TRANSACTION = 'CheckTransaction'
    CANCEL_TRANSACTION = 'CancelTransaction'
    GET_STATEMENT = 'GetStatement'

    http_method_names = ['post']
    authentication_classes = []
    VALIDATE_CLASS: Paycom = None
    reply = None
    ORDER_KEY = KEY = settings.PAYCOM_SETTINGS['ACCOUNTS']['KEY']

    def __init__(self):
        self.METHODS = {
            self.CHECK_PERFORM_TRANSACTION: self.check_perform_transaction,
            self.CREATE_TRANSACTION: self.create_transaction,
            self.PERFORM_TRANSACTION: self.perform_transaction,
            self.CHECK_TRANSACTION: self.check_transaction,
            self.CANCEL_TRANSACTION: self.cancel_transaction,
            self.GET_STATEMENT: self.get_statement
        }

        self.REPLY_RESPONSE = {
            ORDER_FOUND: self.order_found,
            ORDER_NOT_FOUND: self.order_not_found,
            INVALID_AMOUNT: self.invalid_amount
        }

        super(MerchantAPIView, self).__init__()

    def post(self, request):
        check = authentication(request)
        if check is False or not check:
            return Response(AUTH_ERROR)
        serializer = PaycomOperationSerialzer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        method = serializer.validated_data['method']
        self.METHODS[method](serializer.validated_data)

        assert self.reply != None
        return Response(self.reply)

    def check_perform_transaction(self, validated_data):
        assert self.VALIDATE_CLASS is not None
        validate_class: Paycom = self.VALIDATE_CLASS()

        order_key = validated_data["params"]["account"].get(self.ORDER_KEY)

        # Step 1: Validate account (order existence)
        result = validate_class.check_order(**validated_data["params"])
        if result != validate_class.ORDER_FOUND:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "error": {
                    "code": -31050,
                    "message": {
                        "uz": "Buyurtma topilmadi",
                        "ru": "Заказ не найден",
                        "en": "Order not found"
                    },
                    "data": None
                }
            }
            return

        # Step 2: Validate amount
        amount = validated_data["params"].get("amount", 0)
        if amount <= 1000 or amount >= 999999999:
            return self.invalid_amount(validated_data)

        # ✅ Everything valid
        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "result": {
                "allow": True
            }
        }

    def create_transaction(self, validated_data):
        order_key = validated_data['params']['account'].get(self.ORDER_KEY)
        if not order_key:
            raise serializers.ValidationError(f"{self.ORDER_KEY} is required")

        validate_class: Paycom = self.VALIDATE_CLASS()
        result = validate_class.check_order(**validated_data['params'])

        # Step 1: Check invalid account
        if result != ORDER_FOUND:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "error": {
                    "code": -31050,
                    "message": {
                        "uz": "Buyurtma mavjud emas",
                        "ru": "Счёт не существует",
                        "en": "Account not found"
                    },
                    "data": None
                }
            }
            return

        # Step 2: Create transaction
        _id = validated_data['params']['id']
        amount = validated_data['params']['amount'] / 100
        now = int(datetime.now().timestamp() * 1000)

        existing_tx = Transaction.objects.filter(_id=_id).first()
        if existing_tx:
            self.reply = {
                "jsonrpc": "2.0",
                "id": validated_data["id"],
                "result": {
                    "create_time": int(existing_tx.created_datetime),
                    "transaction": str(existing_tx._id),
                    "state": existing_tx.state
                }
            }
            return

        tx = Transaction.objects.create(
            request_id=validated_data['id'],
            _id=_id,
            amount=amount,
            order_key=order_key,
            state=CREATE_TRANSACTION,
            created_datetime=now,
            status=Transaction.PROCESSING
        )

        from data.clickuz.models import Order

        student = None
        lid = None

        if Student.objects.filter(id=order_key).exists():
            student=order_key
        if Lid.objects.filter(id=lid).exists():
            lid=order_key

        Order.objects.create(
            lid=lid,
            student=student,
            type="Payme",
            amount=amount,
            paid=False,
        )

        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "result": {
                "create_time": now,
                "transaction": str(tx._id),
                "state": CREATE_TRANSACTION
            }
        }

    def perform_transaction(self, validated_data):
        _id = validated_data['params']['id']
        request_id = validated_data['id']

        try:
            obj = Transaction.objects.get(_id=_id)

            if obj.state == CLOSE_TRANSACTION:
                self.reply = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "transaction": str(obj._id),
                        "perform_time": int(obj.perform_datetime),
                        "state": CLOSE_TRANSACTION
                    }
                }
                return

            if obj.state in [CANCEL_TRANSACTION_CODE, PERFORM_CANCELED_CODE]:
                obj.status = Transaction.FAILED
                obj.save()

                self.reply = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": UNABLE_TO_PERFORM_OPERATION,
                        "message": UNABLE_TO_PERFORM_OPERATION_MESSAGE,
                        "data": None
                    }
                }
                return

            if obj.state == CREATE_TRANSACTION:
                current_time = datetime.now()
                perform_time = int(current_time.timestamp() * 1000)

                obj.state = CLOSE_TRANSACTION
                obj.status = Transaction.SUCCESS
                obj.perform_datetime = perform_time

                self.VALIDATE_CLASS().successfully_payment(validated_data['params'], obj)

                order = Order.objects.filter(Q(lid=obj.order_key) | Q(student=obj.order_key)).first()
                if order and order.amount == obj.amount:
                    order.paid = True
                    order.save()

                obj.save()

                self.reply = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "transaction": str(obj._id),
                        "perform_time": perform_time,
                        "state": CLOSE_TRANSACTION
                    }
                }
                return

            # fallback
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": UNABLE_TO_PERFORM_OPERATION,
                    "message": UNABLE_TO_PERFORM_OPERATION_MESSAGE,
                    "data": None
                }
            }

        except Transaction.DoesNotExist:
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": TRANSACTION_NOT_FOUND,
                    "message": TRANSACTION_NOT_FOUND_MESSAGE,
                    "data": None
                }
            }

    def check_transaction(self, validated_data):
        _id = validated_data['params']['id']
        request_id = validated_data['id']

        try:
            transaction = Transaction.objects.get(_id=_id)

            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "create_time": int(transaction.created_datetime) if transaction.created_datetime else 0,
                    "perform_time": int(transaction.perform_datetime) if transaction.perform_datetime else 0,  # ✅ Fixed
                    "cancel_time": int(transaction.cancel_datetime) if transaction.cancel_datetime else 0,
                    "transaction": str(transaction._id),
                    "state": transaction.state,
                    "reason": transaction.reason
                }
            }

        except Transaction.DoesNotExist:
            self.reply = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": TRANSACTION_NOT_FOUND,
                    "message": TRANSACTION_NOT_FOUND_MESSAGE,
                    "data": None
                }
            }

    def cancel_transaction(self, validated_data):
        self.context_id = validated_data["id"]  # ✅ Ensure correct response ID
        tx_id = validated_data['params']['id']
        reason = validated_data['params']['reason']

        try:
            transaction = Transaction.objects.get(_id=tx_id)
            if transaction.state == 1:
                transaction.state = CANCEL_TRANSACTION_CODE
            elif transaction.state == 2:
                transaction.state = PERFORM_CANCELED_CODE
                self.VALIDATE_CLASS().cancel_payment(validated_data['params'], transaction)

            transaction.reason = reason
            transaction.status = Transaction.CANCELED

            now_ms = int(datetime.now().timestamp() * 1000)
            if not transaction.cancel_datetime:
                transaction.cancel_datetime = now_ms

            transaction.save()

            self.response_check_transaction(transaction)

        except Transaction.DoesNotExist:
            self.reply = {
                "jsonrpc": "2.0",
                "id": self.context_id,
                "error": {
                    "code": TRANSACTION_NOT_FOUND,
                    "message": TRANSACTION_NOT_FOUND_MESSAGE
                }
            }


    def get_statement(self, validated_data):
        from_d = validated_data.get('params').get('from')
        to_d = validated_data.get('params').get('to')

        filtered_transactions = Transaction.objects.filter(
            created_datetime__gte=from_d,
            created_datetime__lte=to_d
        )

        transactions_json = [
            dict(
                id=obj._id,
                time=int(obj.created_datetime),
                amount=obj.amount,
                account=dict(
                    order_id=obj.order_key
                ),
                create_time=int(obj.created_datetime) if obj.created_datetime else 0,
                perform_time=int(obj.perform_datetime) if obj.perform_datetime else 0,
                cancel_time=int(obj.cancel_datetime) if obj.cancel_datetime else 0,
                transaction=obj.request_id,
                state=obj.state,
                reason=obj.reason,
            )

            for obj in filtered_transactions]

        response = dict(
            result=dict(
                transactions=transactions_json
            )
        )

        self.reply = response


    def order_found(self, validated_data):
        self.reply = dict(result=dict(allow=True))


    def order_not_found(self, validated_data):
        self.reply = dict(error=dict(
            id=validated_data['id'],
            code=ORDER_NOT_FOUND,
            message=ORDER_NOT_FOUND_MESSAGE
        ))


    def invalid_amount(self, validated_data):
        self.reply = {
            "jsonrpc": "2.0",
            "id": validated_data["id"],
            "error": {
                "code": INVALID_AMOUNT,  # usually -31001
                "message": INVALID_AMOUNT_MESSAGE,  # should be a dict with uz/ru/en
                "data": None
            }
        }


    def response_check_transaction(self, transaction: Transaction):
        self.reply = dict(result=dict(
            create_time=int(transaction.created_datetime) if transaction.created_datetime else 0,
            perform_time=int(transaction.perform_datetime) if transaction.perform_datetime else 0,
            cancel_time=int(transaction.cancel_datetime) if transaction.cancel_datetime else 0,
            transaction=str(transaction._id),
            state=transaction.state,
            reason=transaction.reason
        ))


class PaycomWebhookView(MerchantAPIView):
    VALIDATE_CLASS = CheckOrder


class TransactionAPIView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = PaycomuzSerializer


class GeneratePaymeURLView(APIView):
    def post(self, request):

        from root.settings import PAYCOM_SETTINGS

        print(request.data)

        # Correct way to access nested keys
        data = request.data.get("params", {})  # ✅ fix

        print(data)

        amount = data.get('amount')
        account = settings.PAYCOM_SETTINGS.get("KASSA_ID")
        order_id = account.get('order_id')
        return_url = request.data.get("return_url", None)  # Optional

        print(amount, order_id, return_url)

        if not all([amount, order_id]):
            return Response({"detail": "Missing required fields."}, status=400)

        paycom = PayComResponse()
        url = paycom.create_initialization(
            amount=Decimal(amount),
            order_id=str(order_id),
            return_url=return_url
        )

        return Response({'payment_url': url}, status=status.HTTP_200_OK)
