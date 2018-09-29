from django.conf.urls import url
from .views import CompanyAPIs


urlpatterns = [
    url(r'^info.*$', CompanyAPIs.as_view(), name='application'),
]