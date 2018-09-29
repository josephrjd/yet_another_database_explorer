from rest_framework.permissions import IsAuthenticated

def decodeUser(request):
    permission_classes = (IsAuthenticated,)
    return(request.user.id)