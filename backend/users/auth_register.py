from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')  # Get the name from the request
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        dob = data.get('dob')  # Get the date of birth from the request

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        # Create a user and save to database
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name  # Store name in first_name field
        user.save()

        # Save additional information (like phone and dob) if you're using a custom user model
        # Example: profile = Profile(user=user, phone=phone, dob=dob)
        # profile.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
