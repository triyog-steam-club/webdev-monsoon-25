from marshmallow import Schema, fields, validate

class ChatSendSchema(Schema):
    user_id = fields.Str(required=True, description="The unique identifier for the user.")
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))

class ChatHistoryQuerySchema(Schema):
    limit = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    user_id = fields.Str(required=True)

class AnalyticsQuerySchema(Schema):
    start_date = fields.Date(format='iso', required=True)
    end_date = fields.Date(format='iso', required=True)