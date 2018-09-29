from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from core_app.user_decode import decodeUser
from django.contrib.auth.models import User
from user_module.models import UserMapping
from .models import DimCompany
from .serializers import CompanySerializer
from . import message_constants
import json

# Class for get/post company info APIs
# Methods: GET and POST


class CompanyAPIs(APIView):

    def get(self, request, *args):

        # verifying the user
        requester = decodeUser(request)

        if requester is None:
            responseContent = message_constants.FAILURE_MESSAGE
            responseCode = status.HTTP_401_UNAUTHORIZED

        else:
            try:

                # Resolving the requester from user object
                requester = User.objects.filter(id=requester)[0]
                userType = UserMapping.objects.filter(user=requester)

                # Return all the objects if user is admin
                if str(userType[0].userType) == message_constants.ADMIN:
                    companyObjects = CompanySerializer(DimCompany.objects.all(), many=True)

                # Else return only respective company
                else:
                    companyObjects = CompanySerializer(userType[0].company)

                responseContent = companyObjects.data
                responseCode = status.HTTP_200_OK

            except:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_400_BAD_REQUEST

        return JsonResponse(responseContent, status=responseCode, safe=False)

    def post(self, request, *args):

        # verifying the user
        requester = decodeUser(request)

        if requester is None:
            responseContent = message_constants.FAILURE_MESSAGE
            responseCode = status.HTTP_401_UNAUTHORIZED

        else:
            try:

                # Trying to parse the request body
                payload = request.body.decode('utf-8')
                payload = json.loads(payload)

                # resolving the requester and his user mappings
                requester = User.objects.filter(id=requester)[0]
                userType = UserMapping.objects.filter(user=requester)

                # Save the object if user is admin
                if str(userType[0].userType) == message_constants.ADMIN:

                    serializedPayload = CompanySerializer(data=payload)

                    # Validating and saving the object
                    serializedPayload.is_valid()
                    serializedPayload.save()

                    responseContent = message_constants.SUCCESS_MEASSAGE
                    responseCode = status.HTTP_201_CREATED

                # Else return Unauthorized
                else:
                    responseContent = message_constants.FAILURE_MESSAGE
                    responseCode = status.HTTP_401_UNAUTHORIZED

            except:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_400_BAD_REQUEST

        return JsonResponse(responseContent, status=responseCode, safe=False)

    def delete(self, request, *args):

        # Verify the user
        requester = decodeUser(request)

        if requester is None:
            responseContent = message_constants.FAILURE_MESSAGE
            responseCode = status.HTTP_401_UNAUTHORIZED

        else:
            try:

                # Trying to get the company id from query param
                companyToBeDeleted = int(request.GET['company'])

                # Resolving and getting user mappings for requester
                requester = User.objects.filter(id=requester)[0]
                userType = UserMapping.objects.filter(user=requester)

                # Save the object if user is admin
                if str(userType[0].userType) == message_constants.ADMIN\
                        and\
                        companyToBeDeleted in list(DimCompany.objects.all().values_list('id', flat=True)):

                    # Actual delete happens here
                    DimCompany.objects.filter(id=companyToBeDeleted).delete()

                    responseContent = message_constants.SUCCESS_MEASSAGE
                    responseCode = status.HTTP_202_ACCEPTED

                # Else return Unauthorized
                else:
                    responseContent = message_constants.FAILURE_MESSAGE
                    responseCode = status.HTTP_401_UNAUTHORIZED

            except:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_400_BAD_REQUEST

        return JsonResponse(responseContent, status=responseCode, safe=False)
