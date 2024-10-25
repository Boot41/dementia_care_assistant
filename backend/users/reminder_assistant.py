from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from .models import Reminder  # Assuming you have a Reminder model set up in models.py
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

# Fetch Reminders View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reminders(request):
    if request.method == 'GET':
        try:
            user = request.user  # Get the logged-in user
            reminders = Reminder.objects.filter(user=user)  # Fetch reminders for this user

            # Create a list of reminders with date and text
            reminder_list = [
                {'date': reminder.date.strftime('%Y-%m-%d'), 'reminder_text': reminder.reminder_text} 
                for reminder in reminders
            ]
            return JsonResponse({'reminders': reminder_list}, status=200)

        except Exception as e:
            logger.error(f"Error fetching reminders: {str(e)}")
            return JsonResponse({'error': f'Error fetching reminders: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Save Reminder View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_reminder(request):
    if request.method == 'POST':
        try:
            # Parse JSON input from request body
            data = json.loads(request.body)
            date_str = data.get('date')
            reminder_text = data.get('reminder_text')

            if not date_str or not reminder_text:
                return JsonResponse({'error': 'Date and reminder text are required.'}, status=400)

            # Convert date string to a datetime object
            try:
                reminder_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Expected YYYY-MM-DD.'}, status=400)

            # Check if a reminder already exists for the selected date and user
            user = request.user
            reminder, created = Reminder.objects.get_or_create(user=user, date=reminder_date)

            # Update the reminder text
            reminder.reminder_text = reminder_text
            reminder.save()

            if created:
                message = 'Reminder created successfully!'
            else:
                message = 'Reminder updated successfully!'

            return JsonResponse({'message': message}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error saving reminder: {str(e)}")
            return JsonResponse({'error': f'Error saving reminder: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
