import boto3
import json
import os
import uuid
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
user_conversation_mapper_table_name = os.getenv('CHAT_CONVERSATION_MAPPER_TABLE_NAME')
chat_history_table_name = os.getenv('CHAT_HISTORY_TABLE_NAME')
conversation_mapper_table = dynamodb.Table(user_conversation_mapper_table_name)
chat_history_table = dynamodb.Table(chat_history_table_name)

def lambda_handler(event, context):

    # Log the entire event object for debugging
    #print(event)

    # Ensure queryStringParameters exists
    query_params = event.get('queryStringParameters')
    from_user_id = query_params.get('from_user_id')
    to_user_id = query_params.get('to_user_id')

    # Extract the 'sub' from the event's authorizer claims
    user_sub = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('sub')
    if user_sub != from_user_id:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Forbidden: User is not authorized to access this resource'})
        }

    # Extract the last evaluated key from the request, if provided
    last_evaluated_key = event.get('queryStringParameters', {}).get('lastEvaluatedKey')
    if last_evaluated_key:
        last_evaluated_key = json.loads(last_evaluated_key)

    # Call the function to get the conversation ID
    conversation_id = get_conversation_id(
        from_user_id,
        to_user_id
    )

    try:
        # Query the table to get the last 20 chat conversations based on time with pagination
        query_params = {
            'Limit': 20,
            'ScanIndexForward': False,  # Sort in descending order by time
            'KeyConditionExpression': boto3.dynamodb.conditions.Key('conversation_id').eq(conversation_id)
        }
        if last_evaluated_key:
            query_params['ExclusiveStartKey'] = last_evaluated_key

        response = chat_history_table.query(**query_params)
        chat_history = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey')

        # Sort chat history by time if it has values
        if chat_history:
            chat_history.sort(key=lambda x: x['time'], reverse=False)

        result = {
            'chatHistory': chat_history,
            'lastEvaluatedKey': last_evaluated_key
        }

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
def get_conversation_id(user1_id, user2_id):
    # Query existing conversation
    response = conversation_mapper_table.query(
        KeyConditionExpression=Key('user1_id').eq(user1_id) & Key('user2_id').eq(user2_id)
    )

    items = response.get('Items', [])
    if items:
        return items[0]['conversation_id']  # Return existing conversation_id

    # Create a new conversation_id
    conversation_id = str(uuid.uuid4())

    # Insert mirrored records
    with conversation_mapper_table.batch_writer() as batch:
        batch.put_item(Item={
            'user1_id': user1_id,
            'user2_id': user2_id,
            'conversation_id': conversation_id
        })
        batch.put_item(Item={
            'user1_id': user2_id,
            'user2_id': user1_id,
            'conversation_id': conversation_id
        })

    return conversation_id  # Return new conversation_id