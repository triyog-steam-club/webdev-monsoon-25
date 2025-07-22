from flask import Blueprint
from flask_restful import Api

from .routes import (
    ChatSendResource, 
    ChatHistoryResource, 
    SentimentAnalyticsResource
)

v1_blueprint = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(v1_blueprint)

api.add_resource(ChatSendResource, '/chat/send')
api.add_resource(ChatHistoryResource, '/chat/history')
api.add_resource(SentimentAnalyticsResource, '/analytics/sentiment')