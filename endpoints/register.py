# register/check_block.py
import json
import uuid
from database import put_item

def lambda_handler(event, context):
    # Parse the body field into a dictionary
    body = json.loads(event['body'])

    # Check if the request has the necessary parameters
    if 'username' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Missing required parameters. Must contain 'username'."})
        }

    # Generate a unique ID for the new user
    user_id = str(uuid.uuid4())

    # Store the user's information in the database
    response = put_item({
        'type': 'user',
        'id': user_id,
        'username': body['username'],
        'blockedUsers': [],
        'messages': [],
        'groups': []
    })

    print(response)

    # Return the new user's ID
    return {
        'statusCode': 200,
        'body': json.dumps({'userId': user_id})
    }