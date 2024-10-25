from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_user(request):
    user = request.user
    return JsonResponse({
        'first_name': user.first_name,
        'last_name': user.last_name
    })
