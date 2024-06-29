import json
from database import get_item, exists


def lambda_handler(event, context):
    try:
        # Parse the event body from JSON string to a dictionary
        request_body = json.loads(event['body'])

        # Check if the necessary parameter 'userId' is present
        if 'userId' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing required parameter. Must contain 'userId'."})
            }

        user_id = request_body['userId']

        if not exists(user_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"User with ID {user_id} not found."})
            }

        # Get the user's messages from the database
        user_info = get_item(user_id)
        messages = user_info.get('messages', [])
        group_messages = []
        groups = user_info.get('groups', [])

        for groupId in groups:
            group = get_item(groupId)
            group_messages.append({groupId: group['messages']})

        return {
            'statusCode': 200,
            'body': json.dumps({'messages': messages, 'group_messages': group_messages})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON format in the request body."})
        }
