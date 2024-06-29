import json
import uuid
from datetime import datetime

from database import get_item, put_item, update_item, exists


def lambda_handler(event, context):
    try:
        # Parse the event body from JSON string to a dictionary
        request_body = json.loads(event['body'])

        # Check if the necessary parameters are present
        if 'senderId' not in request_body or 'receiverId' not in request_body or 'message' not in request_body:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {'error': "Missing required parameters. Must contain 'senderId', 'receiverId', and 'message'."})
            }

        sender_id = request_body['senderId']
        receiver_id = request_body['receiverId']
        message = request_body['message']

        if not exists(sender_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"Sender with ID {sender_id} not found."})
            }
        if not exists(receiver_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"Receiver with ID {receiver_id} not found."})
            }

        # Check if the sender is blocked by the receiver
        receiver = get_item(receiver_id)

        if receiver['type'] == 'user':
            if sender_id in receiver.get('blockedUsers', []):
                return {
                    'statusCode': 403,
                    'body': json.dumps({'error': "The sender is blocked by the receiver."})
                }

        messages = receiver['messages']

        message_item = {
            'from': sender_id,
            'date': str(datetime.now()),
            'content': message
        }

        messages.append(message_item)

        update_item(receiver_id, "SET messages = :messages", {':messages': messages})

        return {
            'statusCode': 200,
            'body': json.dumps({'message': "Message sent successfully."})
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON format in the request body."})
        }
