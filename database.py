# database.py
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('userTable-674088a')

def exists(id):
    try:
        response = table.get_item(Key={'id': id})
        return 'Item' in response
    except ClientError as e:
        print(e.response['Error']['Message'])

def get_item(key):
    try:
        response = table.get_item(Key={'id': key})
        print(response)
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']

def put_item(item):
    try:
        table.put_item(Item=item)
    except ClientError as e:
        print(e.response['Error']['Message'])

def update_item(key, update_expression, expression_attribute_values):
    try:
        table.update_item(
            Key={'id': key},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
    except ClientError as e:
        print(e.response['Error']['Message'])

def delete_item(key):
    try:
        table.delete_item(Key={'id': key})
    except ClientError as e:
        print(e.response['Error']['Message'])
