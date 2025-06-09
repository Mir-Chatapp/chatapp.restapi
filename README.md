# ChatApp REST API

This repository contains the Lambda functions for the ChatApp REST API. These functions interact with AWS DynamoDB to provide various functionalities for the application.

## Functions

### 1. Get Users
- **Path**: `src/get_users/lambda_function.py`
- **Description**: Fetches a list of users from the `users` DynamoDB table with pagination support.
- **Environment Variables**:
  - `USERS_TABLE_NAME`: The name of the DynamoDB table containing user data.
- **Headers**:
  - `Authorization`: Access token required for authentication.

### 2. Get Chat History
- **Path**: `src/get_chat_history/lambda_function.py`
- **Description**: (To be implemented) Fetches the chat history between users from the DynamoDB table.

## Setup

1. Ensure you have AWS credentials configured to allow access to DynamoDB.
2. Set the required environment variables for each Lambda function.
3. Deploy the Lambda functions using your preferred deployment method.

## Example Request

### Get Users
**Request**:
```http
GET /get-users
Authorization: Bearer <access_token>
```

**Response**:
```json
{
    "users": [
        {
            "userName": "ice-cream",
            "createdat": "2025-06-05T19:03:55.509736",
            "email": "faiem.ict.learning@gmail.com",
            "userId": "5881b3d0-00e1-705c-b4e2-18b764530b78"
        }
    ],
    "lastEvaluatedKey": null
}
```

## License

This project is licensed under the MIT License.
