from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required

# Set up logger
logger = logging.getLogger(__name__)

# Initialize Groq client from Django settings
groq_client = settings.GROQ_CLIENT
client = groq_client

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activity_suggestion(request):
    if request.method == 'POST':
        try:
            # Parse the JSON input from request body
            data = json.loads(request.body)
            user_mood = data.get('mood')

            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User is not authenticated.'}, status=401)

            if not user_mood:
                return JsonResponse({'error': 'Mood is required.'}, status=400)

            # Call Groq API to get activity suggestions based on mood
            processed_input = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Based on the my current mood of '{user_mood}', suggest an activity. "
                               f"The suggestions should consider my mood  and recommend  useful for any person suffering from dementia."
                               f"suggest only one simple,short and fun activity"
                            

                }],
                model="llama3-8b-8192",
                temperature=0.7,
                max_tokens=150,
                top_p=1
            )

            # Log the Groq API response
            logger.info(f"Groq API response: {processed_input}")

            # Extract the content from the Groq API response
            suggestion = processed_input.choices[0].message.content.strip()

            # Return the suggestion in the response
            return JsonResponse({'suggestion': suggestion}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error processing activity suggestion: {str(e)}")
            return JsonResponse({'error': f'Error processing activity suggestion: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
