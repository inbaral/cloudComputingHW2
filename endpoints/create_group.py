import json
import uuid
from database import put_item, get_item, update_item, exists


def lambda_handler(event, context):
    try:
        # Parse the event body from JSON string to a dictionary
        request_body = json.loads(event['body'])

        # Check if the necessary parameters are present
        if 'members' not in request_body or 'groupName' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "Missing required parameters. Must contain 'members' and 'groupName'."})
            }

        group_name = request_body['groupName']
        print(request_body['members'])
        members = list(set(request_body['members']))
        print(members)

        # Generate a unique ID for the new group
        group_id = str(uuid.uuid4())

        # Update each member's "groups" field
        for member_id in members:
            if not exists(member_id):
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': f"User with ID {member_id} not found."})
                }
            member = get_item(member_id)
            if 'groups' not in member:
                member['groups'] = []
            member['groups'].append(group_id)
            update_item(member_id, "SET groups = :g", {':g': member['groups']})

        group_info = {
            'id': group_id,
            'type': 'group',
            'groupName': group_name,
            'members': members,
            'messages': []
        }

        put_item(group_info)
        return {
            'statusCode': 200,
            'body': json.dumps({'id': group_id})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON format in the request body."})
        }
