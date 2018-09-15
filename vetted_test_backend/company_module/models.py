from django.db import models

# Company model


class DimCompany(models.Model):

    id = models.AutoField('id', primary_key=True)
    companyName = models.CharField('company_name', max_length=50, unique=True)
    description = models.TextField('description', max_length=100, null=True)

    def __str__(self):
        return self.companyName