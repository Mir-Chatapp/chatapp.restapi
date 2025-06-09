import boto3
import json
import os

def lambda_handler(event, context):

    # Initialize the DynamoDB client
    dynamodb = boto3.resource('dynamodb')
    
    # Specify the table name from environment variable
    table_name = os.getenv('USERS_TABLE_NAME')
    table = dynamodb.Table(table_name)

    try:
        # Scan the table to get items with pagination
        response = table.scan(Limit=20)
        users = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey')

        result = {
            'users': users,
            'lastEvaluatedKey': last_evaluated_key
        }

        return {
            'statusCode': 200,
            'body': result
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }