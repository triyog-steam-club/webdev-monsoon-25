# chat/services.py
import os
import json
from datetime import datetime
from flask import current_app
import google.generativeai as genai
from sqlalchemy import func

from app import db
from .models import ChatMessage

class ChatService:
    def __init__(self):
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def get_reply_and_sentiment(self, user_id: str, message: str) -> dict:
        prompt = f"""
        Analyze the following user message and provide a response in JSON format.
        The user's message is: "{message}"

        Your response must be a single JSON object with two keys:
        1. "reply": A helpful, friendly, and concise response to the user's message.
        2. "sentiment": Analyze the sentiment of the user's message. It must be one of three strings: "POSITIVE", "NEGATIVE", or "NEUTRAL".
        
        JSON response:
        """
        try:
            response = self.model.generate_content(prompt)
            cleaned_text = response.text.strip().replace('```json', '').replace('```', '').strip()
            result = json.loads(cleaned_text)
            
            if result.get("sentiment") == "NEGATIVE":
                result["alert"] = True
            
            return result
        except Exception as e:
            current_app.logger.error(f"Gemini API call failed: {e}")
            return {
                "reply": "I am currently unable to process your request. Please try again later.",
                "sentiment": "NEUTRAL",
                "error": str(e)
            }

    @staticmethod
    def record_chat(user_id: str, user_message: str, bot_reply: str, sentiment: str):
        chat_message = ChatMessage(
            user_id=user_id,
            user_message=user_message,
            bot_reply=bot_reply,
            sentiment=sentiment
        )
        db.session.add(chat_message)
        db.session.commit()
        return chat_message

    @staticmethod
    def get_chat_history(user_id: str, limit: int) -> list:
        messages = ChatMessage.query.filter_by(user_id=user_id)\
                                     .order_by(ChatMessage.timestamp.desc())\
                                     .limit(limit)\
                                     .all()
        return [msg.to_dict() for msg in reversed(messages)]

    @staticmethod
    def get_sentiment_analytics(start_date: str, end_date: str) -> dict:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)

        sentiment_counts = db.session.query(
            func.date(ChatMessage.timestamp).label('date'),
            ChatMessage.sentiment,
            func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.timestamp >= start_datetime,
            ChatMessage.timestamp <= end_datetime
        ).group_by('date', ChatMessage.sentiment).all()

        daily_counts = {}
        for date, sentiment, count in sentiment_counts:
            if date not in daily_counts:
                daily_counts[date] = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            daily_counts[date][sentiment] = count

        return {
            "query_range": {"start_date": start_date, "end_date": end_date},
            "daily_counts": daily_counts
        }