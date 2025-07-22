import spacy
import itertools
from flask import current_app
from app import db
from app.models import User, Question, QuestionPaper
import google.generativeai as genai
import random

api_key_cycler = None

def get_gemini_key_cycler():
    global api_key_cycler
    if api_key_cycler is None:
        keys = current_app.config.get('GEMINI_API_KEYS')
        if not keys or not any(keys):
            raise ValueError("GEMINI_API_KEYS not configured or all keys are empty in config.py")
        api_key_cycler = itertools.cycle(keys)
    return api_key_cycler

nlp = spacy.load("en_core_web_sm")

def get_user_by_id(user_id):
    return User.query.get_or_404(user_id)

def get_all_papers_for_user(user_id):
    user = get_user_by_id(user_id)
    return user.papers

def create_paper_for_user(user_id, title, text_content):
    user = get_user_by_id(user_id)
    if not text_content:
        raise ValueError("Content cannot be empty.")

    new_paper = QuestionPaper(title=title, owner=user)
    db.session.add(new_paper)
    
    doc = nlp(text_content)
    for sent in doc.sents:
        if sent.text.strip():
            question = Question(text=sent.text.strip(), paper=new_paper)
            db.session.add(question)
    
    db.session.commit()
    return new_paper

def _call_gemini_api(prompt, retries=2):
    """
    Calls the Gemini API with a given prompt and handles key rotation on failure.
    """
    key_cycler = get_gemini_key_cycler()
    for _ in range(retries):
        try:
            api_key = next(key_cycler)
            print(f"--- Attempting Gemini API call with key ending in ...{api_key[-4:]} ---")

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content(prompt)
            
            if not response.parts:
                print(f"Warning: Gemini API returned no parts. Finish Reason: {response.prompt_feedback.block_reason}")
                continue

            return response.text.strip()

        except StopIteration:
            raise ValueError("No API keys are available or all have failed.")
        except Exception as e:
            print(f"An error occurred during Gemini API call: {e}")
            continue
    
    raise Exception("Failed to get a valid response from Gemini API after multiple retries.")


def regenerate_question_with_gemini(paper_id, question_id, extra_prompt=None):
    paper = QuestionPaper.query.get_or_404(paper_id)
    question_to_replace = Question.query.with_parent(paper).filter(Question.id == question_id).first_or_404()

    all_questions_text = " ".join([q.text for q in paper.questions])
    
    prompt_template = f"""
    You are an academic assistant designing an exam.
    
    **Full Document Context:**
    "{all_questions_text}"
    
    **Task:**
    Rephrase the following single question. The new question must adhere to these primary rules:
    1.  Be conceptually similar to the original.
    2.  Use different wording and sentence structure.
    3.  Fit naturally within the context of the full document provided above.
    4.  Be a clear, direct question.
    """

    if extra_prompt:
        prompt_template += f"""
    **HIGH-PRIORITY INSTRUCTION:** You must also follow this specific instruction: "{extra_prompt}"
    """

    prompt_template += f"""
    **Original Question to Rephrase:**
    "{question_to_replace.text}"
    
    **New Question:**
    """
    
    new_text = _call_gemini_api(prompt_template)
    
    if not new_text:
        raise ValueError("AI model did not return any text.")

    question_to_replace.text = new_text
    db.session.commit()
    return question_to_replace


def generate_new_question_from_context(paper_id):
    paper = QuestionPaper.query.get_or_404(paper_id)
    if not paper.questions:
        raise ValueError("Cannot generate a question for an empty paper.")

    all_questions_text = " ".join([q.text for q in paper.questions])

    prompt = f"""
    You are an academic assistant designing an exam.
    
    **Existing Questions in Document:**
    "{all_questions_text}"
    
    **Task:**
    Analyze the existing questions and generate one completely new question that is relevant to the topics covered but is NOT a rephrase of any existing question.
    The new question should explore a related concept or test the material in a different way.
    
    **New Question:**
    """
    
    new_question_text = _call_gemini_api(prompt)

    if not new_question_text:
        raise ValueError("AI model did not return any text.")
        
    new_question = Question(text=new_question_text, paper=paper)
    db.session.add(new_question)
    db.session.commit()
    return new_question