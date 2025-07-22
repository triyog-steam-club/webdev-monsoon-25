from flask import request, jsonify, Blueprint
from . import services
from .schemas import user_schema, question_paper_schema, question_papers_schema, question_schema
from app import db
from app.models import User

from . import api_v1_bp

@api_v1_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user.
    ---
    tags:
      - Users
    summary: Register a new user in the system.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
          properties:
            username:
              type: string
              description: A unique username for the new user.
              example: 'teacher_jane'
    responses:
      201:
        description: User created successfully.
        schema:
          $ref: '#/definitions/User'
      400:
        description: Bad request (e.g., username is missing or already exists).
    """
    data = request.get_json()
    if not data or not data.get('username'):
        return jsonify({"error": "Username is required."}), 400
    
    username = data.get('username')
    if User.query.filter_by(username=username).first():
        return jsonify({"error": f"Username '{username}' already exists."}), 400

    new_user = User(username=username)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(user_schema.dump(new_user)), 201


@api_v1_bp.route('/users/<int:user_id>/papers', methods=['POST'])
def create_paper_for_user_route(user_id):
    """
    Create a new question paper from text for a specific user.
    The provided content is automatically parsed into individual questions based on sentence structure.
    ---
    tags:
      - Question Papers
    summary: Create a new question paper for a user.
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The ID of the user who will own this paper.
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - content
          properties:
            title:
              type: string
              description: The title of the question paper.
              example: "World History Midterm"
            content:
              type: string
              description: The full text content to be parsed into questions.
              example: "What was the primary cause of World War I? Who was the leader of the Soviet Union during the Cuban Missile Crisis?"
    responses:
      201:
        description: Question paper created successfully.
        schema:
          $ref: '#/definitions/QuestionPaper'
      400:
        description: Bad request (e.g., content is missing).
      404:
        description: User not found.
    """
    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({"error": "The 'content' field is required."}), 400
    
    try:
        new_paper = services.create_paper_for_user(
            user_id=user_id,
            title=data.get('title', 'Untitled Paper'),
            text_content=data.get('content')
        )
        return jsonify(question_paper_schema.dump(new_paper)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@api_v1_bp.route('/users/<int:user_id>/papers', methods=['GET'])
def get_user_papers(user_id):
    """
    List all question papers belonging to a specific user.
    ---
    tags:
      - Question Papers
    summary: Retrieve all papers for a user.
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: The ID of the user whose papers are to be retrieved.
    responses:
      200:
        description: A list of the user's question papers.
        schema:
          type: array
          items:
            $ref: '#/definitions/QuestionPaper'
      404:
        description: User not found.
    """
    try:
        papers = services.get_all_papers_for_user(user_id)
        return jsonify(question_papers_schema.dump(papers)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@api_v1_bp.route('/papers/<int:paper_id>/questions/<int:question_id>/regenerate', methods=['PUT'])
def regenerate_question(paper_id, question_id):
    """
    Regenerate a specific question using the Gemini AI model.
    An optional extra prompt can be provided to guide the generation process.
    ---
    tags:
      - Questions
    summary: Regenerate a single question using AI.
    parameters:
      - name: paper_id
        in: path
        type: integer
        required: true
        description: The ID of the paper containing the question.
      - name: question_id
        in: path
        type: integer
        required: true
        description: The ID of the question to regenerate.
      - in: body
        name: body
        schema:
          type: object
          properties:
            extra_prompt:
              type: string
              description: "A specific instruction to guide the AI, e.g., 'Make it easier' or 'Focus on the year 1929'."
              example: "Rephrase this for a 5th-grade student."
    responses:
      200:
        description: Question regenerated successfully.
        schema:
          $ref: '#/definitions/Question'
      404:
        description: Paper or question not found.
      500:
        description: AI service error or other processing failure.
    """
    data = request.get_json() or {}
    extra_prompt = data.get('extra_prompt')

    try:
        updated_question = services.regenerate_question_with_gemini(paper_id, question_id, extra_prompt)
        return jsonify(question_schema.dump(updated_question)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v1_bp.route('/papers/<int:paper_id>/questions/generate', methods=['POST'])
def generate_new_question(paper_id):
    """
    Generate a completely new question based on the context of an entire paper.
    The AI analyzes all existing questions to create a new, relevant one.
    ---
    tags:
      - Questions
    summary: Generate a new question from the paper's context.
    parameters:
      - name: paper_id
        in: path
        type: integer
        required: true
        description: The ID of the paper to use as context for generating a new question.
    responses:
      201:
        description: New question generated and added to the paper successfully.
        schema:
          $ref: '#/definitions/Question'
      404:
        description: Paper not found.
      500:
        description: AI service error or other processing failure.
    """
    try:
        new_question = services.generate_new_question_from_context(paper_id)
        return jsonify(question_schema.dump(new_question)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v1_bp.route('/schemas', methods=['GET'])
def get_schemas():
    """
    This endpoint is hidden and used by Flasgger to define the API's data schemas.
    ---
    definitions:
      User:
        type: object
        properties:
          id:
            type: integer
            description: The unique identifier for the user.
          username:
            type: string
            description: The user's chosen username.
      Question:
        type: object
        properties:
          id:
            type: integer
            description: The unique identifier for the question.
          text:
            type: string
            description: The text of the question.
          question_paper_id:
            type: integer
            description: The ID of the paper this question belongs to.
      QuestionPaper:
        type: object
        properties:
          id:
            type: integer
            description: The unique identifier for the question paper.
          title:
            type: string
            description: The title of the paper.
          user_id:
            type: integer
            description: The ID of the user who owns this paper.
          created_at:
            type: string
            format: date-time
            description: The timestamp when the paper was created.
          questions:
            type: array
            items:
              $ref: '#/definitions/Question'
    """
    return "", 204