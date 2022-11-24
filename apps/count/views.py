from django.contrib.auth.models import User
from django.http import HttpResponse

def counter(request):
    count = User.objects.count()
    return HttpResponse(str(count))
