from django.conf.urls import url
from .views import UserAPIs


urlpatterns = [
    url(r'^info.*$', UserAPIs.as_view(), name='application'),
]