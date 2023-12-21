# routes.py
from __future__ import print_function
from flask import render_template, request, jsonify, session, Blueprint
from app.models.OpenAI import OpenAI as OpenAIModel
from app.extensions import redis_client
import uuid
from pdfminer.high_level import extract_text
import io
from app.models.pro_writing_aid import check_grammar

main = Blueprint('main', __name__)
open_ai_model = OpenAIModel()

@main.route('/')
def home_page():
    gpt_model = open_ai_model.get_openai_model()
    print("GPT Model:", gpt_model) 
    return render_template('index.html', gpt_model=gpt_model)

@main.route('/get_session_id', methods=['GET'])
def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return jsonify(session_id=session['session_id'])

@main.route('/generate_letter', methods=['POST'])
def generate_cover_letter():
    data = request.get_json()
    session_id = data.get('session_id')

    if not session_id:
        return jsonify(error='Session ID not provided'), 400

    try:
        cover_letter = open_ai_model.generate_cover_letter(session_id)
        if not cover_letter:
            return jsonify(error='Error generating cover letter'), 500
        return jsonify(cover_letter=cover_letter)
    except Exception as e:
        print(f"Error during cover letter generation: {e}")
        return jsonify(error='Internal server error'), 500

@main.route('/check_grammar', methods=['POST'])
def check_grammar_route():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify(error='No text provided'), 400

    try:
        # Assuming you have a method in your OpenAIModel for checking grammar
        grammar_issues = check_grammar(text)
        return jsonify(grammar_issues=grammar_issues)
    except Exception as e:
        print(f"Error checking grammar: {e}")
        return jsonify(error='Internal error'), 500
    
@main.route('/set_resume', methods=['POST'])
def set_resume():
    data = request.get_json()
    resume = data.get('resume')
    session_id = data.get('session_id')
    if resume and session_id:
        resume_key = f"{session_id}_resume"
        redis_client.setex(resume_key, 1800, resume)
        return jsonify(message='Resume saved successfully in Redis')
    else:
        return jsonify(error='No resume data or session ID provided'), 400

@main.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify(error='No file part'), 400
        file = request.files['resume']
        if file.filename == '':
            return jsonify(error='No selected file'), 400
        if file and file.filename.endswith('.pdf'):
            session_id = request.form.get('session_id')

            # Read the file stream and extract text using PdfReader
            file_stream = io.BytesIO(file.read())
            # pdf_reader = PdfReader(file_stream)
            # text = ''
            # for page in pdf_reader.pages:
            #     text += page.extract_text()
            text = extract_text(file_stream)

            # Save extracted text to Redis
            resume_key = f"{session_id}_resume"
            redis_client.setex(resume_key, 1800, text)
            return jsonify(message='Resume uploaded and saved successfully')
        else:
            return jsonify(error='Invalid file format'), 400
    except Exception as e:
        return jsonify(error=str(e)), 500


@main.route('/set_job_description', methods=['POST'])
def set_job_description():
    data = request.get_json()
    job_description = data.get('job_description')
    session_id = data.get('session_id')
    if job_description and session_id:
        job_description_key = f"{session_id}_job_description"
        redis_client.setex(job_description_key, 1800, job_description)
        return jsonify(message='Job description saved successfully in Redis')
    else:
        return jsonify(error='No job description data provided'), 400

@main.route('/set_job_role', methods=['POST'])
def set_role():
    data = request.get_json()
    job_role = data.get('job_role')
    session_id = data.get('session_id')
    if job_role and session_id:
        job_role_key = f"{session_id}_job_role"
        redis_client.setex(job_role_key, 1800, job_role)
        return jsonify(message='Job role saved successfully in Redis')
    else:
        return jsonify(error='No job role data provided'), 400
    
@main.route('/set_company', methods=['POST'])
def set_company():
    data = request.get_json()
    company = data.get('company')
    session_id = data.get('session_id')
    if company and session_id:
        company_key = f"{session_id}_company"
        redis_client.setex(company_key, 1800, company)
        return jsonify(message='Company saved successfully in Redis')
    else:
        return jsonify(error='No company data provided'), 400

@main.route('/set_story', methods=['POST'])
def set_story():
    data = request.get_json()
    story = data.get('story')
    session_id = data.get('session_id')
    if story and session_id:
        story_key = f"{session_id}_story"
        redis_client.setex(story_key, 1800, story)
        return jsonify(message='Professional story saved successfully to Redis')
    else:
        return jsonify(error='No professional story data provided'), 400
    
@main.route('/wake_up')
def wake_up():
    return 'Backend active', 200

# @main.route('/set_job_url', methods=['POST'])
# def set_job_url():
#     data = request.get_json()
#     job_url = data.get('job_url')
#     session_id = data.get('session_id')
#     print(job_url)
#     if job_url and session_id:
#         job_url_key = f"{session_id}_job_url"
#         redis_client.setex(job_url_key, 900, job_url)
#         return jsonify(message='Job URL saved successfully in Redis')
#     else:
#         return jsonify(error='No job URL or session ID provided'), 400
    
# @main.route('/extract_and_save', methods=['POST'])
# def extract_and_save():
#     data = request.get_json()
#     session_id = data.get('session_id')

#     if not session_id:
#         return jsonify(error='Session ID not provided'), 400

#     job_url_key = f"{session_id}_job_url"
#     job_url = redis_client.get(job_url_key).decode('utf-8') if redis_client.get(job_url_key) else None

#     if not job_url:
#         return jsonify(error='Job URL not found in Redis'), 400

#     message = open_ai_model.browse_and_extract(session_id, job_url)
#     return jsonify(message=message)


# @main.route('/scrape_and_save', methods=['POST'])
# def scrape_and_save():
#     data = request.get_json()
#     url = data.get('url')
#     session_id = data.get('session_id')

#     if not url or not session_id:
#         return jsonify(error="URL or Session ID not provided"), 400

#     job_role, company, job_description = scrape_website(url)

#     if job_role and company and job_description:
#         # Save the scraped data to Redis
#         redis_client.setex(f"{session_id}_job_role", 900, job_role)
#         redis_client.setex(f"{session_id}_company", 900, company)
#         redis_client.setex(f"{session_id}_job_description", 900, job_description)
#         return jsonify(message="Data scraped and saved successfully")

#     return jsonify(error="Failed to scrape data or save to Redis"), 500

# @main.route('/browse_site', methods=['POST'])
# def browse_site_route():
#     data = request.get_json()
#     session_id = data.get('session_id')
#     job_url = data.get('job_url')

#     if not session_id or not job_url:
#         return jsonify(error='Session ID or Job URL not provided'), 400

#     job_role, company, job_description = open_ai_model.browse_and_extract(job_url)

#     # Save the extracted data to Redis
#     redis_client.setex(f"{session_id}_job_role", 900, job_role)
#     redis_client.setex(f"{session_id}_company", 900, company)
#     redis_client.setex(f"{session_id}_job_description", 900, job_description)

#     return jsonify(message='Data extracted and saved successfully')

# @main.route('/send_message', methods=['POST'])
# def handle_chat_message():
#     data = request.get_json()
#     user_message = data.get('message')
#     session_id = data.get('session_id')
#     if user_message and session_id:
#         response = open_ai_model.get_ai_answer(user_message)
#         return jsonify(response=response)
#     else:
#         return jsonify(error='No message provided'), 400

# @main.route('/set_tone')
# def set_tone():
#     data = request.get_json()
#     tone = data.get('tone')
#     if tone:
#         tone_key = f"{session['session_id']}_tone"
#         redis_client.setex('tone', 1800, tone)
#         return jsonify(message='tone saved successfully in Redis')
#     else:
#         return jsonify(error='No tone data provided'), 400
    