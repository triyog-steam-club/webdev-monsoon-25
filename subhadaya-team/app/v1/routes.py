# chat/resources.py
import os
from flask import request
from flask_restful import Resource
from flasgger import swag_from
from marshmallow import ValidationError

from .services import ChatService
from .schemas import ChatSendSchema, ChatHistoryQuerySchema, AnalyticsQuerySchema

chat_send_schema = ChatSendSchema()
history_schema = ChatHistoryQuerySchema()
analytics_schema = AnalyticsQuerySchema()

class ChatSendResource(Resource):

    yaml_path = os.path.join(os.path.dirname(__file__), 'docs', 'chat_send.yml')

    @swag_from(yaml_path)
    def post(self):
        try:
            data = chat_send_schema.load(request.get_json())
        except ValidationError as err:
            return {'errors': err.messages}, 400

        user_id = data['user_id']
        message = data['message']

        chat_service = ChatService()
        result = chat_service.get_reply_and_sentiment(user_id, message)
        
        if 'error' not in result:
            ChatService.record_chat(
                user_id=user_id,
                user_message=message,
                bot_reply=result.get('reply'),
                sentiment=result.get('sentiment')
            )
        
        return result, 201

class ChatHistoryResource(Resource):

    yaml_path = os.path.join(os.path.dirname(__file__), 'docs', 'chat_history.yml')

    @swag_from(yaml_path)
    def get(self):
        try:
            args = history_schema.load(request.args)
        except ValidationError as err:
            return {'errors': err.messages}, 400

        history = ChatService.get_chat_history(args['user_id'], args['limit'])
        return {'history': history}, 200

class SentimentAnalyticsResource(Resource):

    yaml_path = os.path.join(os.path.dirname(__file__), 'docs', 'sentiment_analytics.yml')

    @swag_from(yaml_path)
    def get(self):
        try:
            args = analytics_schema.load(request.args)
        except ValidationError as err:
            return {'errors': err.messages}, 400
            
        analytics = ChatService.get_sentiment_analytics(
            args['start_date'].isoformat(), 
            args['end_date'].isoformat()
        )
        return analytics, 200