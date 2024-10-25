from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

# Set up logger
logger = logging.getLogger(__name__)

# Initialize Groq client from Django settings
groq_client = settings.GROQ_CLIENT
client = groq_client

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def music_recommendation(request):
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

            # Call Groq API to get music recommendations based on mood
            processed_input = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Based on my current mood of '{user_mood}', suggest Indian music recommendations. "
                               f"Provide only one song with the title  and give one hyperlink to the audio file. "
                               f"Focus on music that is uplifting and helpful for someone suffering from dementia."
                               f"do not give any description or detailed explanation of the song"
                               f"give the response ,title ,the link in different lines"
                }],
                model="llama3-8b-8192",
                temperature=0.7,
                max_tokens=300,
                top_p=1
            )

            # Log the Groq API response
            logger.info(f"Groq API response: {processed_input}")

            # Extract the content from the Groq API response
            recommendations = processed_input.choices[0].message.content.strip()

            # Return the recommendations in the response
            return JsonResponse({'recommendations': recommendations}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error processing music recommendation: {str(e)}")
            return JsonResponse({'error': f'Error processing music recommendation: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
