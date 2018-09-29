from django.db import models
from django.contrib.auth.models import User
from company_module.models import DimCompany

# UserType model
# Required to store type of users and their description


class DimUserType(models.Model):

    id = models.AutoField('id', primary_key=True)
    userType = models.CharField('user_type', max_length=50)
    description = models.TextField('description', max_length=100, null=True)

    def __str__(self):
        return self.userType

# Model for user - user type mapping


class UserMapping(models.Model):
    id = models.AutoField('id', primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userType = models.ForeignKey(DimUserType, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(DimCompany, on_delete=models.CASCADE, null=True, blank=True)

