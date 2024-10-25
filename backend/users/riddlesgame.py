from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import random

# Set up logger
logger = logging.getLogger(__name__)

# Initialize Groq client from Django settings
groq_client = settings.GROQ_CLIENT
client = groq_client

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def riddle_game(request):
    if request.method == 'POST':
        try:
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User is not authenticated.'}, status=401)

            # Parse the JSON input from the request body
            data = json.loads(request.body)
            user_action = data.get('action')  # Could be 'get_riddle', 'answer', or 'skip'
            user_answer = data.get('answer')
            riddle_id = data.get('riddle_id')  # Used for tracking riddles

            # Initialize game state
            if user_action == 'get_riddle':
                # Call Groq API to get a riddle
                response = client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": "Generate one riddle for a dementia patient. Provide a hint if needed. Just give the riddle as your response."
                    }],
                    model="llama3-8b-8192",
                    temperature=0.7,
                    max_tokens=150,
                    top_p=1
                )

                # Log the Groq API response
                logger.info(f"Groq API response: {response}")

                # Extract riddle and hint from the response
                riddle = response.choices[0].message.content.strip().split('\n')[0]  # Assuming the riddle is the first line
                hint = response.choices[0].message.content.strip().split('\n')[1] if len(response.choices[0].message.content.strip().split('\n')) > 1 else "Think carefully!"

                # Store the correct answer in your logic (could be a dictionary or database)
                correct_answer = "an echo"  # Example; replace with logic to retrieve the correct answer

                return JsonResponse({'riddle': riddle, 'riddle_id': 1, 'correct_answer': correct_answer, 'hint': hint}, status=200)

            elif user_action == 'answer':
                # Retrieve the correct answer from storage or context
                correct_answer = "an echo"  # Replace with dynamic answer retrieval logic

                if user_answer.lower() == correct_answer.lower():
                    return JsonResponse({'result': 'Correct!'}, status=200)
                else:
                    hint = "Think carefully!"  # You may want to provide a dynamic hint here
                    return JsonResponse({'result': 'Wrong answer!', 'hint': hint}, status=200)

            elif user_action == 'skip':
                # Call Groq API to get a new riddle when skipped
                response = client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": "Generate another riddle for a dementia patient. Just give the riddle as your response."
                    }],
                    model="llama3-8b-8192",
                    temperature=0.7,
                    max_tokens=150,
                    top_p=1
                )

                # Log the Groq API response
                logger.info(f"Groq API response on skip: {response}")

                # Extract riddle and hint from the response
                riddle = response.choices[0].message.content.strip().split('\n')[0]  # Assuming the riddle is the first line
                hint = "Think carefully!"  # Default hint; you can modify this as needed

                return JsonResponse({'riddle': riddle, 'riddle_id': 2, 'hint': hint}, status=200)  # Return the new riddle and a new id

            else:
                return JsonResponse({'error': 'Invalid action.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error processing riddle game: {str(e)}")
            return JsonResponse({'error': f'Error processing riddle game: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
