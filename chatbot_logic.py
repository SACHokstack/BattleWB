import json
import os
import logging
import traceback
from groq import Groq
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Initialize Groq client with API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    logging.error("GROQ_API_KEY not found in environment variables")
    raise ValueError("GROQ_API_KEY not found")  # Better to stop execution
else:
    logging.debug("GROQ_API_KEY found in environment variables")

client = Groq(api_key=groq_api_key)

# Track conversation state
conversation_history = []
resume_data = {}

def process_message(user_message):
    global conversation_history
    global resume_data

    try:
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_message})
        logging.debug(f"Added user message to conversation history. Total messages: {len(conversation_history)}")

        # Load the system prompt
        try:
            with open('prompt_template.txt', 'r') as file:
                system_prompt = file.read()
            logging.debug("Successfully loaded prompt template")
        except Exception as e:
            logging.error(f"Error loading prompt template: {str(e)}")
            system_prompt = (
                "You are an AI assistant that helps users create a professional resume. "
                "Engage in a conversation to collect resume details (name, title, contact information, summary, skills, experience, education, certifications). "
                "Store the information incrementally. "
                "When sufficient data is collected or the user requests it, return the resume data as a JSON object inside a code block like this:\n"
                "```json\n"
                "{\n"
                '    "name": "John Doe",\n'
                '    "title": "Software Engineer",\n'
                '    "contact": {\n'
                '        "email": "john.doe@example.com",\n'
                '        "phone": "+1-555-555-5555"\n'
                "    },\n"
                '    "summary": "Experienced software engineer with a background in developing scalable web applications and working across the full stack.",\n'
                '    "skills": ["Python", "JavaScript", "AWS", "Docker"],\n'
                '    "experience": [\n'
                "        {\n"
                '            "position": "Developer",\n'
                '            "company": "Tech Corp",\n'
                '            "start_date": "2020-01",\n'
                '            "end_date": "Present",\n'
                '            "description": "Led development of cloud-based solutions using AWS and Python."\n'
                "        }\n"
                "    ],\n"
                '    "education": [\n'
                "        {\n"
                '            "degree": "B.S. in Computer Science",\n'
                '            "institution": "State University",\n'
                '            "start_date": "2014-09",\n'
                '            "end_date": "2018-05"\n'
                "        }\n"
                "    ],\n"
                '    "certifications": [\n'
                '        "AWS Certified Developer – Associate"\n'
                "    ]\n"
                "}\n"
                "```"
            )

        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history
        ]

        # Call the model
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
        )

        assistant_response = response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": assistant_response})

        # Try to extract resume data if available
        if "```json" in assistant_response or "```" in assistant_response:
            try:
                json_content = assistant_response.split("```")[1]
                if json_content.startswith("json"):
                    json_content = json_content[4:].strip()
                resume_data = json.loads(json_content)
            except Exception as e:
                logging.error(f"Error extracting JSON: {str(e)}")

        return assistant_response, resume_data

    except Exception as e:
        logging.error(f"Error in process_message: {traceback.format_exc()}")
        return "Sorry, something went wrong.", None

def reset_conversation():
    global conversation_history
    global resume_data
    conversation_history = []
    resume_data = {}
