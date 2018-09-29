from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status
from core_app.user_decode import decodeUser
from django.contrib.auth.models import User
from .models import UserMapping, DimUserType
from company_module.models import DimCompany
from . import message_constants
import json

# Function to return user object and related mapping values
# Param : userId


def get_user(userId):
    userObject = User.objects.filter(id=userId)
    try:
        userMapping = UserMapping.objects.filter(user=userObject[0])
        userType = str(userMapping[0].userType)
        userCompany = str(userMapping[0].company)
        userCompanyId = userMapping[0].company.id
    except:
        userType = None
        userCompany = None
        userCompanyId = None

    userObject = {
        'id': userObject[0].id,
        'username': userObject[0].username,
        'first_name': userObject[0].first_name,
        'last_name': userObject[0].last_name,
        'user_type': userType,
        'company_name': userCompany,
        'company_id': userCompanyId
    }

    return userObject

# Function to return multiple user object
# Param : userIds list


def get_users(userIds):
    userObjects = []
    for userId in userIds:
        userObjects.append(get_user(userId))

    return userObjects

# Class for get/post/put/delete methods for user info APIs
# Methods: GET, POST, PUT, DELETE


class UserAPIs(APIView):

    # Method GET
    def get(self, request, *args):

        try:
            # Verifying the user
            requester = decodeUser(request)
            if requester is None:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_401_UNAUTHORIZED

            else:
                try:
                    try:
                        # Trying to get query parameter
                        userId = int(request.GET['user'])
                    except:
                        userId = None

                    # getting user level info
                    requester = User.objects.filter(id=requester)[0]
                    userType = UserMapping.objects.filter(user=requester)

                    # if param not present - send all the list
                    if userId is None:

                        # Return all the objects if user is admin
                        if str(userType[0].userType) == message_constants.ADMIN:
                            userIds = User.objects.values_list('id', flat=True)

                        # Return all the objects under a company if user is company admin
                        elif str(userType[0].userType) == message_constants.COMPANY_ADMIN:
                            userIds = UserMapping.objects.filter(company = userType[0].company).values_list('user', flat=True)

                        userObjects = get_users(userIds)

                    else:
                        userObjects = get_user(userId)

                    responseContent = userObjects
                    responseCode = status.HTTP_200_OK

                except:
                    responseContent = message_constants.FAILURE_MESSAGE
                    responseCode = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            responseContent = {"erason" : str(e)}
            responseCode = status.HTTP_400_BAD_REQUEST
        return JsonResponse(responseContent, status=responseCode, safe=False)


    # Method POST - to create user
    def post(self, request, *args):

        # verify the user
        requester = decodeUser(request)

        if requester is None:
            responseContent = message_constants.FAILURE_MESSAGE
            responseCode = status.HTTP_401_UNAUTHORIZED

        else:
            try:
                # Trying to parse the body
                payload = request.body.decode('utf-8')
                payload = json.loads(payload)

                # creating user
                userObject = User.objects.create_user(
                    username=payload['username'],
                    first_name=payload['first_name'],
                    last_name=payload['last_name'],
                    password=payload['password'])

                # creating user mappings
                UserMapping.objects.create(
                    userType=DimUserType.objects.filter(id=payload['user_type'])[0],
                    user=userObject,
                    company=DimCompany.objects.filter(id=payload['company_id'])[0])

                responseContent = message_constants.SUCCESS_MEASSAGE
                responseCode = status.HTTP_201_CREATED

            except:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_400_BAD_REQUEST


        return JsonResponse(responseContent, status=responseCode, safe=False)


    # Method PUT - to update user
    def put(self, request, *args):

        # verify user
        requester = decodeUser(request)

        if requester is None:
            responseContent = message_constants.FAILURE_MESSAGE
            responseCode = status.HTTP_401_UNAUTHORIZED

        else:
            try:
                # Trying to parse the request body
                payload = request.body.decode('utf-8')
                payload = json.loads(payload)

                userObject = User.objects.filter(id=payload['id'])

                # Update/create user mappings
                userMapping = UserMapping.objects.update_or_create(user=userObject[0])[0]
                userMapping.company = DimCompany.objects.filter(id=payload['company_id'])[0]
                userMapping.userType = DimUserType.objects.filter(id=payload['user_type'])[0]
                userMapping.save()

                # Update user info
                userObject.update(username=payload['username'],
                           first_name=payload['first_name'],
                           last_name=payload['last_name'])

                # updating password
                if payload['password'] is not None:
                    userObject = User.objects.get(id=payload['id'])
                    userObject.set_password(payload['password'])
                    userObject.save()

                responseContent = message_constants.SUCCESS_MEASSAGE
                responseCode = status.HTTP_202_ACCEPTED

            except:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_400_BAD_REQUEST

        return JsonResponse(responseContent, status=responseCode, safe=False)


    # Method DELETE - to remove user
    def delete(self, request, *args):

        # verifying user
        requester = decodeUser(request)

        if requester is None:
            responseContent = message_constants.FAILURE_MESSAGE
            responseCode = status.HTTP_401_UNAUTHORIZED

        else:
            try:

                # trying to get query params
                userToBeDeleted = int(request.GET['user'])

                # filtering the requester and user type
                requester = User.objects.filter(id=requester)[0]
                userType = UserMapping.objects.filter(user=requester)

                # initializing response
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_422_UNPROCESSABLE_ENTITY


                # Delete employee if requester is admin and target is not admin
                # OR
                # Delete employee if requester is company admin and target is company employee
                if (str(userType[0].userType) == message_constants.ADMIN
                        and userToBeDeleted!=requester.id)\
                        or\
                        (str(userType[0].userType) == message_constants.COMPANY_ADMIN
                            and userToBeDeleted in list(UserMapping.objects.filter(
                        company = userType[0].company).values_list('user', flat=True))):

                    # actual delete happens here
                    User.objects.filter(id=userToBeDeleted).delete()

                    responseContent = message_constants.SUCCESS_MEASSAGE
                    responseCode = status.HTTP_202_ACCEPTED

            except:
                responseContent = message_constants.FAILURE_MESSAGE
                responseCode = status.HTTP_400_BAD_REQUEST

        return JsonResponse(responseContent, status=responseCode, safe=False)

