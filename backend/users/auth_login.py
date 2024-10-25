from django.contrib.auth import authenticate
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Check if user exists and authenticate
        user = authenticate(username=email, password=password)
        
        if user is not None:
            # User authenticated successfully
            return JsonResponse({'success': True, 'message': 'Login successful'})
        else:
            # Invalid credentials
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
    
    # If method is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=405)
