# app/models/OpenAI.py
import os
from openai import OpenAI as OpenAIClient
from app.extensions import redis_client
# from app.models.pro_writing_aid import check_grammar

def generate_cover_letter_prompt(resume, job_description, job_role=None, company=None, user_story=None):
    # default_story = "[Three sentences mentioning recent, relevant company news or achievements of the company, then showing the applicant's connection and interest in relation of their experience on their resume.]"
    
    return f"""
    Resume: {resume}
    Job Description: {job_description}
    Role: {job_role}
    User Story: {user_story}


    Cover Letter Framework:
    1. Analyze and identify hard skills and soft skills from the resume and the user story, relevant to the job description.
    2. Craft a cover letter that integrates these skills, specifically tailored for the specified role at the company. Ensure the letter is around 37 lines but does not exceed one page.
    3. Maintain a tone that is engaging, personalized, enthusiastic, friendly and aligned with user story, company's value, company's mission, and job description. The letter should be truthful and avoid any fictional elements or skills.Don’t regurgitate exactly from the resume and job description, but instead use synonyms or rephrase to match the tone.
    4. Use the user story to highlight the applicant's skills, experience, and achievement relevant to the company's mission and/or values, and the job description. Keep it at or below 4 sentences.
    5. Browse the internet for the company to find relevant news or information that makes the cover letter stand out.


    Format:
    [Applicant's Name]
    [Applicant's Phone]
    [Applicant's Email]
    
    {company}


    Dear Hiring Manager,


    [Introduction: In two-three sentences, begin with an engaging and authentic expression of excitement about the role at the company. Highlight how the company's mission or achievements resonate with the applicant.]


    [User Story Paragraph: Directly incorporate the provided user story to demonstrate the applicant's adaptability and problem-solving skills. The first sentence should transition the story into the cover letter smoothly.]


    [Make transition sentence into the bullet-point section below. Example, do not copy "I am proud to highlight some key achievements that reflect my suitability for this role"
    List 2-3 bullet points (use • as bullet-point) from the resume that are relevant to the job's skills/requirements. First list the skill that the bullet point is focusing on, then relate that skill with an example from resume and relate to the job description requirements. Add a space between each bullet-point.
    ]


    [Closing Paragraph: Express enthusiasm about joining the company and confidence in contributing meaningfully. Keep this section to one paragraph.]


    Warm regards,
    [space here]
    [Applicant's Name]
    """

class OpenAI:
    def __init__(self):
        """Initialize the OpenAI class."""
        self.conversation_history = []
        
    @staticmethod
    def is_gpt4_enabled():
        return os.getenv('OPENAI_MODEL') == 'gpt-4'

    @staticmethod
    def get_openai_model():
        return os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

    def generate_cover_letter(self, session_id):
        # return "Testd Covr ZLetter", []
        resume_key = f"{session_id}_resume"
        job_description_key = f"{session_id}_job_description"
        job_role_key = f"{session_id}_job_role"
        company_key = f"{session_id}_company"
        story_key = f"{session_id}_story"
        # job_url_key = f"{session_id}_job_url"

        resume = redis_client.get(resume_key).decode('utf-8') if redis_client.get(resume_key) else None
        job_description = redis_client.get(job_description_key).decode('utf-8') if redis_client.get(job_description_key) else None
        job_role = redis_client.get(job_role_key).decode('utf-8') if redis_client.get(job_role_key) else None
        company = redis_client.get(company_key).decode('utf-8') if redis_client.get(company_key) else None
        user_story_raw = redis_client.get(story_key).decode('utf-8') if redis_client.get(story_key) else None
        # job_url = redis_client.get(job_url_key).decode('utf-8') if redis_client.get(job_url_key) else None

        user_story = ""
        if user_story_raw:
            user_story = f"Use the following story: {user_story_raw}. Relate it directly back to one or more requirements in the job description: {job_description}"

        # if self.is_gpt4_enabled():
        #     job_description = self.browse_and_extract(job_url)
        #     redis_client.setex(job_description_key, 900, job_description)

        if not resume or not job_description:
            return "We don't have enough information to proceed.", []

        query = generate_cover_letter_prompt(resume, job_description, job_role, company, user_story)
        cover_letter = self.get_ai_answer(query)

        if not cover_letter:
            return "Error in generating cover letter"

        print(f"Returning cover letter: {cover_letter}")
        return cover_letter
    
    def get_ai_answer(self, query: str = None):
        if not query:
            return "I'm sorry, I didn't receive any input. Could you please repeat your question?"

        if query.strip().lower() == "clear history":
            self.conversation_history.clear()
            return "Conversation history has been cleared."

        self.conversation_history.append({"role": "user", "content": query})
        
        try:
            print("AI is thinking...")
            client = OpenAIClient(api_key=os.getenv('OPENAI_API_KEY'))
            chat_completion = client.chat.completions.create(
                messages=self.conversation_history,  
                model=self.get_openai_model(),
            )

            message = chat_completion.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": message})
            return message
        except Exception as e:
            print(f"An error occurred while generating a response: {e}")
            self.conversation_history.clear()
            return "There was an issue generating a response. Please try again later."
        
    
        
# Instantiate OpenAI class
open_ai = OpenAI()

# Check if GPT-4 is enabled and print the result
if open_ai.is_gpt4_enabled():
    print("GPT-4 is enabled.")
else:
    print("GPT-4 is not enabled. Current model:", open_ai.get_openai_model())
    
# def browse_site(job_url):
#     """
#     Function to retrieve job details from a specified URL.

#     Return the company name, job name/role, and job posting details including role responsibilities, required skills, 'nice-to-have' skills, and any other essential information for applicants.
#     """

# def browse_and_extract(self, session_id, job_url):
    #     query = self.construct_browsing_prompt(job_url)
    #     response = self.get_ai_answer(query)

    #     # Logic to parse the response to extract job_role, company, and job_description
    #     job_role, company, job_description = self.parse_extraction(response)

    #     # Save to Redis
    #     if job_role and company and job_description:
    #         redis_client.setex(f"{session_id}_job_role", 900, job_role)
    #         redis_client.setex(f"{session_id}_company", 900, company)
    #         redis_client.setex(f"{session_id}_job_description", 900, job_description)
    #         return "Information extracted and saved successfully"
    #     else:
    #         return "Failed to extract information"

    # def construct_browsing_prompt(self, job_url):
    #     return f"""
    #     Visit the webpage at {job_url}. 
    #     Summarize the job description, 
    #     identify the company name, 
    #     and describe the job role in a structured format:
    #     Company Name: 
    #     Job Role: 
    #     Job Description: 
    #     """

    # def parse_extraction(self, response):
    #     try:
    #         # Splitting the response into lines
    #         lines = response.split('\n')

    #         # Initializing variables
    #         job_role, company, job_description = None, None, None

    #         # Iterating through each line and extracting information
    #         for line in lines:
    #             if line.startswith('Company Name:'):
    #                 company = line.split('Company Name:')[1].strip()
    #             elif line.startswith('Job Role:'):
    #                 job_role = line.split('Job Role:')[1].strip()
    #             elif line.startswith('Job Description:'):
    #                 job_description = line.split('Job Description:')[1].strip()
            
    #         return job_role, company, job_description
    #     except Exception as e:
    #         print(f"Error in parsing: {e}")
    #         return None, None, None
