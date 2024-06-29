import json
from database import get_item, update_item


def lambda_handler(event, context):
    try:
        # Parse the event body from JSON string to a dictionary
        request_body = json.loads(event['body'])

        # Check if the necessary parameters are present
        if 'userId' not in request_body or 'blockedUserId' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing required parameters. Must contain 'userId' and 'blockedUserId'."})
            }

        user_id = request_body['userId']
        blocked_user_id = request_body['blockedUserId']

        # Add the blocked user to the user's 'blockedUsers' list
        update_item(user_id, "SET blockedUsers = list_append(blockedUsers, :i)", {':i': [blocked_user_id]})

        return {
            'statusCode': 200,
            'body': json.dumps({'message': "User blocked successfully."})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON format in the request body."})
        }
