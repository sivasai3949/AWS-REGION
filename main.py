from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import boto3
import json
import os
from botocore.exceptions import ClientError  # Import ClientError

app = FastAPI()

# Load environment variables from .env file
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = "meta.llama3-70b-instruct-v1:0"

# Initialize AWS Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Enable session handling
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Initial questions
questions = [
    "To gain further understanding, can you please describe your educational experience?",
    "What are your aspirations and higher education goals (e.g., want to study abroad or at elite universities)?",
    "Please describe if there are any financial constraints?"
]

# Options to present after initial questions
final_options = [
    "Would you like a detailed roadmap to achieve your career goals considering your academics, financial status, and study locations?",
    "Do you want personalized career guidance based on your academic performance, financial status, and desired study locations?",
    "Do you need other specific guidance like scholarship opportunities, study programs, or financial planning?",
    "Other"
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Reset session variables
    request.session.clear()
    request.session['question_index'] = 0
    request.session['user_responses'] = []

    # Render template with introductory message
    return templates.TemplateResponse("chat.html", {"request": request, "intro_message": "Hi I am Naavi, your personal coach and navigator for higher education...😊"})

@app.post("/process_chat")
async def process_chat(request: Request, user_input: str = Form(...)):
    question_index = request.session.get('question_index', 0)
    user_responses = request.session.get('user_responses', [])

    # Ensure to store user input if not the first question
    if question_index > 0:
        user_responses.append(user_input)
        request.session['user_responses'] = user_responses

    if question_index < len(questions):
        next_question = questions[question_index]
        request.session['question_index'] = question_index + 1
        return JSONResponse({'question': next_question})
    else:
        request.session['question_index'] = len(questions)  # Ensure index is at the end
        return JSONResponse({'options': final_options})

@app.post("/process_final_option")
async def process_final_option(request: Request, user_input: str = Form(...)):
    user_responses = request.session.get('user_responses', [])
    user_responses.append(user_input)  # Add the option chosen by the user
    bot_response = await get_ai_response(user_responses, user_input)
    return JSONResponse({'response': bot_response})

async def get_ai_response(user_responses, final_option):
    messages = "\n".join([f"user\n{response}\n" for response in user_responses])

    final_prompt = "Based on the information provided, generate three distinct pathways for achieving the user's educational and career goals. Each pathway should be clearly separated and include step-by-step guidance."

    if "roadmap" in final_option:
        final_prompt = "Generate a detailed roadmap to achieve the user's career goals considering their academics, financial status, and study locations."
    elif "career guidance" in final_option:
        final_prompt = "Provide personalized career guidance based on the user's academic performance, financial status, and desired study locations."
    elif "specific guidance" in final_option:
        final_prompt = "Offer specific guidance like scholarship opportunities, study programs, or financial planning."
    elif "Other" in final_option:
        final_prompt = "Generate pathways based on user selection for achieving their educational and career goals."

    messages += f"assistant\n{final_prompt}\n"

    try:
        native_request = {
            "prompt": messages,
            "max_gen_len": 2048,
            "temperature": 0.6,
        }
        response = bedrock_client.invoke_model(modelId=MODEL_ID, body=json.dumps(native_request))
        model_response = json.loads(response["body"].read())
        return model_response["generation"]
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error invoking model: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
