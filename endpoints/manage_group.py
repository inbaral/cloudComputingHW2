import json
from database import get_item, update_item, exists


def lambda_handler(event, context):
    try:
        # Parse the event body from JSON string to a dictionary
        request_body = json.loads(event['body'])

        # Check if the necessary parameters are present
        if 'groupId' not in request_body or 'userId' not in request_body or 'action' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {'error': "Missing required parameters. Must contain 'groupId', 'userId', and 'action'."})
            }

        group_id = request_body['groupId']
        user_id = request_body['userId']
        action = request_body['action']

        if not exists(user_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"User with ID {user_id} not found."})
            }

        if not exists(group_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"Group with ID {group_id} not found."})
            }

        # Get the group's data from the database
        group = get_item(group_id)
        user = get_item(user_id)

        if action == 'add':
            # Add the user to the group's 'members' list
            if user_id not in group.get('members', []):
                group['members'].append(user_id)
                user['groups'].append(group_id)

        elif action == 'remove':
            # Remove the user from the group's 'members' list
            if user_id in group.get('members', []):
                group['members'].remove(user_id)
                user['groups'].remove(group_id)

        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Invalid action. Must be 'add' or 'remove'."})
            }

        # Update the group's data in the database
        update_item(group_id, "SET members = :m", {':m': group['members']})
        update_item(user_id, "SET groups = :g", {':g': user['groups']})

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f"User {action}ed successfully."})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON format in the request body."})
        }
