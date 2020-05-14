import re
import json
import os

import boto3
import botocore
from boto3.dynamodb.conditions import Key

import api_responses


USER_TABLE_NAME = os.environ['DYNAMODB_USER_TABLE']
POST_TABLE_NAME = os.environ['DYNAMODB_POST_TABLE']
USER_FOLLOWING_TABLE_NAME = os.environ['DYNAMODB_USERFOLLOWING_TABLE']
ERROR_MESSAGE = 'An error occured when trying to get followed users posts'
NO_USER_WITH_SUCH_ID_ERROR_MESSAGE = 'No user with given user id'
NOT_A_VALID_UUID = 'Url parameter is not a valid uuid'
UUID_MATCH_REGEX = r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'


def get_followed_user_posts(event, context):
    dynamodb = boto3.resource('dynamodb')
    post_table = dynamodb.Table(POST_TABLE_NAME)
    user_following_table = dynamodb.Table(USER_FOLLOWING_TABLE_NAME)
    user_table = dynamodb.Table(USER_TABLE_NAME)
    user_uuid = event['pathParameters']['user_uuid']
    if not re.match(UUID_MATCH_REGEX, user_uuid):
        return api_responses.get_error_response(400, NOT_A_VALID_UUID)

    try:
        user = user_table.get_item(
            Key={
                'user_uuid': user_uuid
            }
        )
        if 'Item' not in user:
            return api_responses.get_error_response(400, NO_USER_WITH_SUCH_ID_ERROR_MESSAGE)


        followed_users = user_following_table.query(
            KeyConditionExpression=Key('follower_uuid').eq(user_uuid)
        )
        posts = []
        if 'Items' in followed_users:
            for followed_user in followed_users['Items']:
                more_posts = post_table.query(
                    KeyConditionExpression=Key('user_uuid').eq(followed_user['followed_uuid'])
                )
                posts.extend(map(lambda post: { 'user_uuid': post['user_uuid'], 'post': post['post']  }, more_posts['Items']))
        return api_responses.get_success_response(200, json.dumps(posts))

    except botocore.exceptions.ClientError as error:
        print(ERROR_MESSAGE)
        print(str(error))
        return api_responses.get_error_response(500, ERROR_MESSAGE)
