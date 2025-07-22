from datetime import datetime
from app import db  

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(150), nullable=False, index=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_reply = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.user_message,
            "reply": self.bot_reply,
            "sentiment": self.sentiment,
            "timestamp": self.timestamp.isoformat() + "Z"
        }