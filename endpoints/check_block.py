import json
from database import get_item


def lambda_handler(event, context):
    try:
        # Parse the event body from JSON string to a dictionary
        request_body = json.loads(event['body'])

        # Check if the necessary parameters are present
        if 'userId' not in request_body or 'isBlockedUserId' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing required parameters. Must contain 'userId' and 'otherUserId'."})
            }

        user_id = request_body['userId']
        is_blocked_user_id = request_body['isBlockedUserId']

        # Get the user's data from the database
        user_id = get_item(user_id)

        # Check if the user is in the other user's 'blockedUsers' list
        is_blocked = is_blocked_user_id in user_id.get('blockedUsers', [])

        return {
            'statusCode': 200,
            'body': json.dumps({'isBlocked': is_blocked})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON format in the request body."})
        }
