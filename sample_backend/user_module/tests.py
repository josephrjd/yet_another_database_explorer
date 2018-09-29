from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from . import message_constants
from .models import DimUserType, UserMapping, DimCompany
import json


class UserTestCases(TestCase):

    # Initialising with 3 user
    def setUp(self):

        self.djangoAdminUser = 'django_admin'
        self.djangoAdminPass = 'password'
        self.companyAdminUser = 'company admin'
        self.companyAdminPass = 'password'
        self.employeeUser = 'employee'
        self.employeePass = 'password'
        self.companyName = 'some company'
        self.host = 'http://localhost'
        self.port = '8000'
        self.loginUrl = '/login'
        self.userInfoUrl = '/user/info'

        # Create a admin
        User.objects.create_user(
            username=self.djangoAdminUser,
            password=self.djangoAdminPass)

        # Create a company admin
        User.objects.create_user(
            username=self.companyAdminUser,
            password=self.companyAdminPass)

        # Create a company employee
        User.objects.create_user(
            username=self.employeeUser,
            password=self.employeePass)

        # Populate DIM user type
        DimUserType.objects.create(userType=message_constants.COMPANY_ADMIN) #1
        DimUserType.objects.create(userType=message_constants.EMPLOYEE) #2
        DimUserType.objects.create(userType=message_constants.ADMIN) #3

        # Populate DIM company
        DimCompany.objects.create(companyName=self.companyName) #1

        # Mark  admin
        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.ADMIN)[0],
            user=User.objects.filter(username=self.djangoAdminUser)[0],
            company=None)

        # Mark company admin
        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.COMPANY_ADMIN)[0],
            user=User.objects.filter(username=self.djangoAdminUser)[0],
            company=DimCompany.objects.filter(companyName=self.companyName)[0])

        # Mark company employee
        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.EMPLOYEE)[0],
            user=User.objects.filter(username=self.djangoAdminUser)[0],
            company=DimCompany.objects.filter(companyName=self.companyName)[0])


    # Login tests
    # 1. Authentic login
    def test_login_authentic(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                        {'username': self.djangoAdminUser, 'password': self.djangoAdminPass}, format='json')
        self.assertEqual(loginResponse.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in loginResponse.data)


    # 2. Non-authentic login
    def test_login_non_authentic(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                        {'username': self.djangoAdminUser, 'password': self.djangoAdminPass + 'fail'}, format='json')
        self.assertEqual(loginResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # 3. Login with missing fields
    def test_login_missing_fields(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                        {'username': self.djangoAdminUser}, format='json')
        self.assertEqual(loginResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # Create user tests
    # 1. Trying to create user - Authorised
    def test_create_user(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        createUserResponse = self.client.post(self.host + ':' + self.port + self.userInfoUrl,
                                              {
                                                  "username": "some name",
                                                  "first_name": "",
                                                  "last_name": "",
                                                  "password": "a",
                                                  "user_type": \
                                                      DimUserType.objects.filter(userType=message_constants.COMPANY_ADMIN)[0].id, # for company admin
                                                  "company_id": \
                                                      DimCompany.objects.filter(companyName=self.companyName)[0].id # for company
                                              },
                                              HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(createUserResponse.status_code, status.HTTP_201_CREATED)


    # 2. Trying to create user - Unauthorised
    def test_create_user_unauthorised(self):

        employeeAuth = 'Bearer randomtoken'

        createUserResponse = self.client.post(self.host + ':' + self.port + self.userInfoUrl,
                                              {
                                                  "username": "random employee",
                                                  "first_name": "",
                                                  "last_name": "",
                                                  "password": "password",
                                                  "user_type": \
                                                      DimUserType.objects.filter(userType=message_constants.EMPLOYEE)[0].id,  # for employee
                                                  "company_id": \
                                                      DimCompany.objects.filter(companyName=self.companyName)[0].id # for company
                                              },
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(createUserResponse.status_code, status.HTTP_401_UNAUTHORIZED)


    # 3. Trying to create user with missing mandatory fields
    def test_create_user_missing_fields(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        createUserResponse = self.client.post(self.host + ':' + self.port + self.userInfoUrl,
                                              {
                                                  "first_name": "",
                                                  "last_name": "",
                                                  "password": "a",
                                                  "user_type": \
                                                      DimUserType.objects.filter(
                                                          userType=message_constants.COMPANY_ADMIN)[0].id,
                                              # for company admin
                                                  "company_id": \
                                                      DimCompany.objects.filter(companyName=self.companyName)[0].id
                                              # for company
                                              },
                                              HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(createUserResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # Update user tests
    # 1. Trying to update user - Authorized
    def test_update_user(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.employeeUser, 'password': self.employeePass},
                                         format='json')
        employeeAuth = 'Bearer ' + loginResponse.data['token']

        updateUserResponse = self.client.put(self.host + ':' + self.port + self.userInfoUrl,
                                             {
                                                 "id": User.objects.filter(username=self.employeeUser)[0].id,
                                                 "username": "employee name change",
                                                 "first_name": "JJ",
                                                 "last_name": "",
                                                 "password": "changed password",
                                                 "user_type": DimUserType.objects.filter(
                                                          userType=message_constants.COMPANY_ADMIN)[0].id,
                                                 "company_id": DimCompany.objects.filter(companyName=self.companyName)[0].id
                                             },
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(updateUserResponse.status_code, status.HTTP_202_ACCEPTED)


    # 2. Trying to update user - Unauthorized
    def test_update_user_unauthorized(self):

        employeeAuth = 'Bearer randomtoken'

        updateUserResponse = self.client.put(self.host + ':' + self.port + self.userInfoUrl,
                                             {
                                                 "id": User.objects.filter(username=self.employeeUser)[0].id,
                                                 "username": "employee name change",
                                                 "first_name": "JJ",
                                                 "last_name": "",
                                                 "password": "changed password",
                                                 "user_type": DimUserType.objects.filter(
                                                          userType=message_constants.COMPANY_ADMIN)[0].id,
                                                 "company_id": DimCompany.objects.filter(companyName=self.companyName)[0].id
                                             },
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(updateUserResponse.status_code, status.HTTP_401_UNAUTHORIZED)


    # 3. Trying to update user with missing mandatory fields
    def test_update_user_missing_fields(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.employeeUser, 'password': self.employeePass},
                                         format='json')
        employeeAuth = 'Bearer ' + loginResponse.data['token']

        updateUserResponse = self.client.put(self.host + ':' + self.port + self.userInfoUrl,
                                             {
                                                 "id": User.objects.filter(username=self.employeeUser)[0].id,
                                                 "username": "employee name change",
                                                 "first_name": "JJ",
                                                 "password": "changed password",
                                                 "user_type": DimUserType.objects.filter(
                                                          userType=message_constants.COMPANY_ADMIN)[0].id,
                                                 "company_id": DimCompany.objects.filter(companyName=self.companyName)[0].id
                                             },
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(updateUserResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # Get user tests
    # 1. Get list of users - Authorzed
    def test_get_user_list(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        getUserResponse = self.client.get(self.host + ':' + self.port + self.userInfoUrl,
                                              HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(getUserResponse.content)), 3) # checking for all the users(3)


    # 2. Get list of user - Unauthorized
    def test_get_user_list_unauthorized(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.employeeUser, 'password': self.employeePass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        getUserResponse = self.client.get(self.host + ':' + self.port + self.userInfoUrl,
                                              HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # 3. Get specific user - Authorized
    def test_get_user(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.companyAdminUser, 'password': self.companyAdminPass},
                                         format='json')
        employeeAuth = 'Bearer ' + loginResponse.data['token']

        userId = User.objects.filter(username=self.employeeUser)[0].id

        getUserResponse = self.client.get(self.host + ':' + self.port + self.userInfoUrl + '/?user=' + str(userId),
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_200_OK)

        requiredKeys = ['id', 'username', 'first_name', 'last_name', 'user_type', 'company_name', 'company_id']
        self.assertIs(all(key in json.loads(getUserResponse.content) for key in requiredKeys), True)


    # 4. Get specific user - Unauthorized
    def test_get_user_unauthorized(self):

        employeeAuth = 'Bearer randomtoken'

        userId = User.objects.filter(username=self.djangoAdminUser)[0].id

        getUserResponse = self.client.get(self.host + ':' + self.port + self.userInfoUrl + '/?user=' + str(userId),
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_401_UNAUTHORIZED)


    # Delete user tests
    # 1. Delete genuine user - Authorised
    def test_delete_user(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.companyAdminUser, 'password': self.companyAdminPass},
                                         format='json')
        companyAdminAuth = 'Bearer ' + loginResponse.data['token']

        user = User.objects.filter(username=self.companyAdminUser)[0]

        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.COMPANY_ADMIN)[0],
            user=user,
            company=DimCompany.objects.filter(companyName=self.companyName)[0])

        getUserResponse = self.client.delete(self.host + ':' + self.port + self.userInfoUrl + '/?user=' + str(user.id),
                                              HTTP_AUTHORIZATION=companyAdminAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_202_ACCEPTED)


    # 2. Delete genuine user - Unauthorized
    def test_delete_user_unauthorized(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.employeeUser, 'password': self.employeePass},
                                         format='json')
        employeeAuth = 'Bearer ' + loginResponse.data['token']

        user = User.objects.filter(username=self.companyAdminUser)[0]

        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.EMPLOYEE)[0],
            user=user,
            company=DimCompany.objects.filter(companyName=self.companyName)[0])

        getUserResponse = self.client.delete(self.host + ':' + self.port + self.userInfoUrl + '/?user=' + str(user.id),
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # 3. Delete with missing param
    def test_delete_user_bad_user(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        employeeAuth = 'Bearer ' + loginResponse.data['token']

        getUserResponse = self.client.delete(self.host + ':' + self.port + self.userInfoUrl,
                                              HTTP_AUTHORIZATION=employeeAuth, content_type='application/json')

        self.assertEqual(getUserResponse.status_code, status.HTTP_400_BAD_REQUEST)
