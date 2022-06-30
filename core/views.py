import datetime
import math
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from .image_detection import detect_faces
from .permissions import IsMember
from .serializers import (
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    FileSerializer,
    TokenSerializer,
    SubscribeSerializer,
)
from .models import TrackedRequest, Payment
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()


def get_user_from_token(request):
    key = request.META.get("HTTP_AUTHORIZATION").split(" ")[1]
    token = Token.objects.get(key=key)
    user = User.objects.get(id=token.user_id)

    return user


class FileUploadView(APIView):
    permission_classes = (AllowAny,)
    throttle_scope = "demo"

    def post(self, request, *args, **kwargs):

        content_length = request.META.get("CONTENT_LENGTH")
        # limit content length
        if int(content_length) > 5000000:
            return Response(
                {"message": "Image size is greater than 5MB"},
                status=HTTP_400_BAD_REQUEST,
            )

        file_serializer = FileSerializer(data=request.data)
        if file_serializer.is_valid():
            file_serializer.save()
            image_path = file_serializer.data.get("file")
            recognition = detect_faces(image_path)
        return Response(recognition, status=HTTP_200_OK)


class EmailUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        obj = {"email": user.email}
        return Response(obj)


class ChangeEmailView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        email_serializer = ChangeEmailSerializer(data=request.data)
        if email_serializer.is_valid():
            email = email_serializer.data.get("email")
            confirm_email = email_serializer.data.get("confirm_email")
            if email == confirm_email:
                user.email = email
                user.save()
                return Response({"email": email}, status=HTTP_200_OK)
            return Response(
                {"message": "These emails do not match"}, status=HTTP_400_BAD_REQUEST
            )
        return Response(
            {"message": "Did not receive the right data"}, status=HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        password_serializer = ChangePasswordSerializer(data=request.data)
        if password_serializer.is_valid():
            password = password_serializer.data.get("password")
            confirm_password = password_serializer.data.get("confirm_password")
            current_password = password_serializer.data.get("current_password")
            auth_user = authenticate(username=user.username, password=current_password)

            if auth_user is not None:
                if password == confirm_password:
                    auth_user.set_password(password)
                    auth_user.save()
                    return Response(status=HTTP_200_OK)
                else:
                    return Response(
                        {"message": "These passwords do not match"},
                        status=HTTP_400_BAD_REQUEST,
                    )
            return Response(
                {"message": "Incorrect user information"}, status=HTTP_400_BAD_REQUEST
            )
        return Response(
            {"message": "Did not receive the right data"}, status=HTTP_400_BAD_REQUEST
        )


class UserDetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        membership = user.membership
        today = datetime.datetime.now()
        month_start = datetime.date(today.year, today.month, 1)
        tracked_request_count = TrackedRequest.objects.filter(
            user=user, timestamp__gte=month_start
        ).count()

        amount_due = 0
        if user.is_member:
            amount_due = (
                stripe.Invoice.upcoming(customer=user.stripe_customer_id)["amount_due"]
                / 100
            )
        obj = {
            "membershipType": membership.get_type_display(),
            "free_trial_end_date": membership.end_date,
            "next_billing_date": membership.end_date,
            "api_request_count": tracked_request_count,
            "amount_due": amount_due,
        }
        return Response(obj)


class SubscribeView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)

        membership = user.membership

        try:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)
            serializer = SubscribeSerializer(data=request.data)

            if serializer.is_valid():
                stripe_token = serializer.data.get("stripeToken")

                subscription = stripe.Subscription.create(
                    customer=customer.id, items=[{"plan": settings.STRIPE_PLAN_ID}]
                )

                membership.stripe_subscription_id = subscription.id
                membership.stripe_subscription_item_id = subscription["items"]["data"][
                    0
                ]["id"]
                membership.type = "M"
                membership.start_date = datetime.datetime.now()
                membership.end_date = datetime.datetime.fromtimestamp(
                    subscription.current_period_end
                )
                membership.save()

                user.is_member = True
                user.on_free_trial = False
                user.save()

                payment = Payment()
                print(subscription, "111111111")
                payment.amount = subscription.plan.amount / 100
                payment.user = user
                payment.save()
                return Response({"message": "Payment Successful"}, status=HTTP_200_OK)
            else:
                return Response(
                    {"message": "Incorrect data received"}, status=HTTP_400_BAD_REQUEST
                )
        except stripe.error.CardError as e:
            return Response(
                {"message": "Your card was declined"}, status=HTTP_400_BAD_REQUEST
            )

        except stripe.error.StripeError as e:
            return Response(
                {"message": "You have not been charged there was an error"},
                status=HTTP_400_BAD_REQUEST,
            )


class CancelSubscription(APIView):
    # set permisisons
    permission_classes = (IsMember,)

    def post(self, request, *args, **kwargs):
        # get user
        user = get_user_from_token(request)
        # get membership
        membership = user.membership

        # try retrieve stripe subsc
        try:
            sub = stripe.Subscription.retrieve(membership.stripe_subscription_id)
            sub.delete()
        except Exception as e:
            return Response(
                {"message": "There has been an error, we will look into it"},
                status=HTTP_400_BAD_REQUEST,
            )
        # update user model
        user.is_member = False
        user.save()

        # update membership
        membership.type = "N"
        membership.save()

        # return response
        return Response(
            {"message": "Your subscription has been cancelled"},
            status=HTTP_200_OK,
        )


class ImageRecognitionView(APIView):
    permission_classes = (IsMember,)
    throttle_scope = "demo"

    def post(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        membership = user.membership
        file_serializer = FileSerializer(data=request.data)

        usage_record_id = None
        if user.is_member and not user.on_free_trial:
            usage_record = stripe.UsageRecord.create(
                quantity=1,
                timestamp=math.floor(datetime.datetime.now().timestamp()),
                subscription_item=membership.stripe_subscription_item_id,
            )
            usage_record_id = usage_record.id

        tracked_request = TrackedRequest()
        tracked_request.user = user
        tracked_request.usage_record_id = usage_record_id
        tracked_request.endpoint = "/api/image-recognition/"
        tracked_request.save()

        content_length = request.META.get("CONTENT_LENGTH")
        if int(content_length) > 5000000:
            return Response(
                {"message": "Image size is greater than 5MB"},
                status=HTTP_400_BAD_REQUEST,
            )

        if file_serializer.is_valid():
            file_serializer.save()
            image_path = file_serializer.data.get("file")
            recognition = detect_faces(image_path)
            return Response(recognition, status=HTTP_200_OK)
        return Response({"Received incorrect data"}, status=HTTP_400_BAD_REQUEST)


class APIKeyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = get_user_from_token(request)
        token_qs = Token.objects.filter(user=user)
        if token_qs.exists():
            token_serializer = TokenSerializer(token_qs, many=True)
            try:
                return Response(token_serializer.data, status=HTTP_200_OK)
            except:
                return Response(
                    {"message": "Did not receive correct data"},
                    status=HTTP_400_BAD_REQUEST,
                )
        return Response({"message": "User does not exist"}, status=HTTP_400_BAD_REQUEST)
