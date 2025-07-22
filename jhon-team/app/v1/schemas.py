from app import ma
from app.models import User, Question, QuestionPaper

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class QuestionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        load_instance = True
        include_fk = True

class QuestionPaperSchema(ma.SQLAlchemyAutoSchema):
    questions = ma.Nested(QuestionSchema, many=True)
    
    class Meta:
        model = QuestionPaper
        load_instance = True
        include_fk = True 

user_schema = UserSchema()
users_schema = UserSchema(many=True)

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

question_paper_schema = QuestionPaperSchema()
question_papers_schema = QuestionPaperSchema(many=True)