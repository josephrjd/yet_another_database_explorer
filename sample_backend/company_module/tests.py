from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from . import message_constants
from user_module.models import DimUserType, DimCompany, UserMapping
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
        self.companyInfoUrl = '/company/info'

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


    # Create company tests
    # 1. Create company - authorized
    def test_create_company(self):
        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.ADMIN)[0],
            user=User.objects.filter(username=self.djangoAdminUser)[0],
            company=None)

        createCompanyResponse = self.client.post(self.host + ':' + self.port + self.companyInfoUrl,
                                                 {
                                                     "companyName": "test company",
                                                     "description": "asd"
                                                 },
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(createCompanyResponse.status_code, status.HTTP_201_CREATED)


    # 2. Create a company - unauthorized
    def test_create_company_unauthorized(self):

        djangoAdminAuth = 'Bearer randomtoken'

        createCompanyResponse = self.client.post(self.host + ':' + self.port + self.companyInfoUrl,
                                                 {
                                                     "companyName": "test company",
                                                     "description": "asd"
                                                 },
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(createCompanyResponse.status_code, status.HTTP_401_UNAUTHORIZED)


    # 3. Create a company - duplicate name
    def test_create_company_duplicate_name(self):
        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.ADMIN)[0],
            user=User.objects.filter(username=self.djangoAdminUser)[0],
            company=None)

        createCompanyResponse = self.client.post(self.host + ':' + self.port + self.companyInfoUrl,
                                                 {
                                                     "companyName": "some company",
                                                     "description": "asd"
                                                 },
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(createCompanyResponse.status_code, status.HTTP_400_BAD_REQUEST)


    # 4. Create a company - missing fields
    def test_create_company_missing_field(self):
        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        UserMapping.objects.create(
            userType=DimUserType.objects.filter(userType=message_constants.ADMIN)[0],
            user=User.objects.filter(username=self.djangoAdminUser)[0],
            company=None)

        createCompanyResponse = self.client.post(self.host + ':' + self.port + self.companyInfoUrl,
                                                 {
                                                     "companyName": "some company",
                                                 },
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(createCompanyResponse.status_code, status.HTTP_400_BAD_REQUEST)

    # Get company tests
    # 1. Get company list
    def test_get_company_list(self):
        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        getCompanyListResponse = self.client.get(self.host + ':' + self.port + self.companyInfoUrl,
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(getCompanyListResponse.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(getCompanyListResponse.content)), 1)  # checking for length of list (1)


    # 2. Get company list unauthorized
    def test_get_company_list_unauthorized(self):

        djangoAdminAuth = 'Bearer randomtoken'

        getCompanyListResponse = self.client.get(self.host + ':' + self.port + self.companyInfoUrl,
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(getCompanyListResponse.status_code, status.HTTP_401_UNAUTHORIZED)


    # 3. Get corresponding company
    def test_get_corresponding_company(self):
        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        djangoAdminAuth = 'Bearer ' + loginResponse.data['token']

        companyId = DimCompany.objects.filter(companyName=self.companyName)[0].id

        getCompanyListResponse = self.client.get(self.host + ':' + self.port + self.companyInfoUrl + '/?company=' + str(companyId),
                                                 HTTP_AUTHORIZATION=djangoAdminAuth, content_type='application/json')

        self.assertEqual(getCompanyListResponse.status_code, status.HTTP_200_OK)
        requiredKeys = ['id', 'companyName', 'description']
        self.assertIs(all(key in json.loads(getCompanyListResponse.content)[0] for key in requiredKeys), True)


    # Delete company tests
    # 1. Delete company - authorized
    def test_delete_company(self):

        loginResponse = self.client.post(self.host + ':' + self.port + self.loginUrl,
                                         {'username': self.djangoAdminUser, 'password': self.djangoAdminPass},
                                         format='json')
        companyAdminAuth = 'Bearer ' + loginResponse.data['token']

        companyId = DimCompany.objects.filter(companyName=self.companyName)[0].id

        deleteCompanyRespose = self.client.delete(self.host + ':' + self.port + self.companyInfoUrl + '/?company=' + str(companyId),
                                              HTTP_AUTHORIZATION=companyAdminAuth, content_type='application/json')

        self.assertEqual(deleteCompanyRespose.status_code, status.HTTP_202_ACCEPTED)


    # 2. Delete company - unauthorized
    def test_delete_company_unauthorized(self):

        companyAdminAuth = 'Bearer randomtoken'

        companyId = DimCompany.objects.filter(companyName=self.companyName)[0].id

        deleteCompanyRespose = self.client.delete(self.host + ':' + self.port + self.companyInfoUrl + '/?company=' + str(companyId),
                                              HTTP_AUTHORIZATION=companyAdminAuth, content_type='application/json')

        self.assertEqual(deleteCompanyRespose.status_code, status.HTTP_401_UNAUTHORIZED)