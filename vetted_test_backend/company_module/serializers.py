from rest_framework import serializers
from .models import DimCompany


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = DimCompany
        fields = '__all__'
