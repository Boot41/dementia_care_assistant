from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
import logging
import uuid  # For generating unique IDs
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
def process_user_input(request):
    if request.method == 'POST':
        try:
            # Parse JSON input from request body
            data = json.loads(request.body)
            user_input = data.get('input')

            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User is not authenticated.'}, status=401)

            user = request.user  # Get the current logged-in user

            if not user_input:
                return JsonResponse({'error': 'Input is required.'}, status=400)

            # Call Groq API to process the user input and generate an SQL query
            processed_input = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"Translate the following instruction into a single SQL query: {user_input}. "
                               f"Only return one SQL query. The users_usermemory table contains id, key, value, user_id.pass the user_id as<your_user_id> "
                               f"do not use pronouns in key names while storing updating or retreiving "
                               f"store all the key value names in lowercase only"
                }],
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=150,
                top_p=1
            )

            # Log Groq API response
            logger.info(f"Groq API response: {processed_input}")

            # Extract the content from the Groq response
            groq_response = processed_input.choices[0].message.content.strip()
            sql_query = extract_sql_query(groq_response)

            if sql_query:
                logger.info(f"Extracted SQL Query: {sql_query}")
                return execute_sql_query(user, sql_query)

            return JsonResponse({'error': 'Failed to extract SQL query from the response.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return JsonResponse({'error': f'Error processing data: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def extract_sql_query(groq_response):
    # Extract the first valid SQL query from the Groq response
    sql_query_start = groq_response.find("SELECT")
    insert_query_start = groq_response.find("INSERT")
    update_query_start = groq_response.find("UPDATE")
    delete_query_start = groq_response.find("DELETE")

    # Determine the start of the SQL query based on which one is found first
    if sql_query_start != -1:
        return groq_response[sql_query_start:groq_response.find(";", sql_query_start) + 1]
    elif insert_query_start != -1:
        return groq_response[insert_query_start:groq_response.find(";", insert_query_start) + 1]
    elif update_query_start != -1:
        return groq_response[update_query_start:groq_response.find(";", update_query_start) + 1]
    elif delete_query_start != -1:
        return groq_response[delete_query_start:groq_response.find(";", delete_query_start) + 1]

    return None


def execute_sql_query(user, sql_query):
    from django.db import connection

    user_id = user.id

    try:
        # Replace placeholders in the SQL query
        sql_query = sql_query.replace("<your_user_id>", str(user_id)).replace("None", "NULL").replace("?", "NULL")

        if sql_query.strip().lower().startswith("insert"):
            # Modify the query to exclude the `id` field and allow the DB to auto-generate it
            if "id" in sql_query:
                # Remove the id from the field list and corresponding value in the INSERT query
                sql_query = sql_query.replace("id, ", "").replace("NULL, ", "")

            # Add ON CONFLICT to update the value if key exists for the same user_id
            sql_query = sql_query.rstrip(';') + " ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value;"

        elif sql_query.strip().lower().startswith("delete"):
            # Add condition to delete specific records for the user
            sql_query = sql_query.rstrip(';') 
        # Log the SQL query
        logger.info(f"Executing SQL Query: {sql_query}")
        print(sql_query)

        with connection.cursor() as cursor:
            cursor.execute(sql_query)

            if sql_query.strip().lower().startswith("select"):
                # Fetch all results from the SELECT query
                results = cursor.fetchall()
                value=results[0][0]

                # Log the raw results
                logger.info(f"Raw SQL Results: {results}")
                print(f"Raw Results: {results}")

                # If results are empty, return a message indicating no data
                if not results:
                    return JsonResponse({'message': 'I don\'t have an idea.could you please tell now'}, status=200)

                # Get column names
               
                return JsonResponse({'value': value}, status=200)

            connection.commit()
            return JsonResponse({'message': 'Okay!!'}, status=200)

    except Exception as e:
        logger.error(f"SQL execution error: {str(e)}")
        return JsonResponse({'error': 'Error executing SQL query.'}, status=500)
