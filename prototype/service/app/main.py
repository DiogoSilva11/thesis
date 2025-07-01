# -----------------------------------------------------------------------------------------------------------------

import os
import json
import shutil

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel
from typing import Optional, List, Dict
from pathlib import Path

from app.utils.captioning import load_captioning_model
from app.utils.rag import load_embedding_model
from app.entities.applicant import Applicant
from app.entities.agent import Agent

# -----------------------------------------------------------------------------------------------------------------

app = FastAPI()

# -----------------------------------------------------------------------------------------------------------------

load_dotenv()
instance = AzureOpenAI(
    azure_endpoint=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview"
)
model = os.getenv("DEPLOYMENT_NAME")
embeddings = load_embedding_model()
processor, captioner = load_captioning_model()

# -----------------------------------------------------------------------------------------------------------------

app_mode = 'traditional'
applicants : dict[str, Applicant] = {}
agents : dict[str, Agent]= {}

# -----------------------------------------------------------------------------------------------------------------

class ApplicantRequest(BaseModel):
    id : str

class QuestionnaireRequest(BaseModel):
    id : str
    category : str

class HealthRequest(BaseModel):
    id: str
    health_records: Optional[Dict] = {}
    daily_steps: Optional[int] = None

class QuestionRequest(BaseModel):
    id : str
    question_index : int

class AnswerRequest(BaseModel):
    id : str
    factor : str
    answer : int

class ModeRequest(BaseModel):
    mode : str

# -----------------------------------------------------------------------------------------------------------------

@app.get("/")
async def get_status() -> dict:
    '''
    Returns the app status
    '''
    status = 'running'
    return {'status': status}

@app.get("/mode")
async def get_mode() -> dict:
    '''
    Returns the current mode ("traditional" or "dynamic")
    '''
    return {'mode': app_mode}

@app.get("/applicant/{id}")
async def get_applicant(id : str) -> dict:
    '''
    Returns a specific applicant
    '''
    applicant = applicants.get(id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    data = applicant.to_json()
    return {'applicant': data}

@app.get("/applicants")
async def get_applicants() -> dict:
    '''
    Returns all applicants
    '''
    data = {}
    for id, applicant in applicants.items():
        data[id] = applicant.to_json()
    return {'applicants': data}

@app.get("/conversation/{id}")
async def get_conversation(id : str) -> dict:
    '''
    Returns an applicant-agent conversation (model messages)
    '''
    applicant = applicants.get(id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    conversation = agents[id].conversation
    return {'conversation': conversation}

@app.get("/application/{id}")
async def get_application(id : str) -> dict:
    '''
    Returns a completed insurance application
    '''
    application = {}
    with open(f"app/data/applications/{id}.json", 'r', encoding='utf-8') as file:
        application = json.load(file)
    return {'application': application}

@app.get("/applications")
async def get_applications() -> dict:
    '''
    Retrieves all completed insurance applications
    '''
    folder = Path('app/data/applications')
    data = []
    for path in folder.glob('*.json'):
        with open(path, 'r', encoding='utf-8') as file:
            application = json.load(file)
            data.append(application)
    return {'applications': data}

# -----------------------------------------------------------------------------------------------------------------

@app.post("/applicant")
async def create_applicant(request : ApplicantRequest) -> dict:
    '''
    Creates a new applicant and agent
    '''
    folder = Path('app/data/applications')
    id = str(len(list(folder.glob('*.json'))) + 1)
    applicant = Applicant(id)
    agent = Agent(id, instance, model, processor, captioner, embeddings)
    applicants[id] = applicant
    agents[id] = agent
    return {'id': id}

@app.post("/questionnaire")
async def produce_questionnaire(request : QuestionnaireRequest) -> dict:
    '''
    Produces a static questionnaire
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    questionnaire = agents[request.id].produce_questionnaire(applicant, request.category)
    return {'questionnaire': questionnaire}

@app.post("/demographics")
async def collect_demographics(request : ApplicantRequest) -> dict:
    '''
    Collects geographical indicators
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    agents[request.id].collect_basic_info(applicant)
    municipality = applicant.answers.get('personal_location')
    agents[request.id].collect_geo_indicators(applicant, municipality)
    agents[request.id].generate_geo_indices(applicant)
    return {'geo_indicators': applicant.geo_indicators}

@app.post("/health/upload")
async def upload_health_records(request : HealthRequest) -> dict:
    '''
    Uploads health and steps data
    '''
    folder = f"app/data/applicants/{request.id}"
    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}/health_records.json", 'w', encoding='utf-8') as file:
        json.dump(request.health_records, file, indent=4, ensure_ascii=False)
    steps = {'steps': request.daily_steps}
    with open(f"{folder}/daily_steps.json", 'w', encoding='utf-8') as file:
        json.dump(steps, file, indent=4)
    return {"message": "Health and steps data uploaded successfully"}

@app.post("/health")
async def collect_health_records(request : ApplicantRequest) -> dict:
    '''
    Processes existing health records
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    folder = f"app/data/applicants/{request.id}"
    health_records, daily_steps = {}, None
    if os.path.exists(folder):
        with open(f"{folder}/health_records.json", 'r', encoding='utf-8') as file:
            health_records = json.load(file)
        with open(f"{folder}/daily_steps.json", 'r') as file:
            steps = json.load(file)
            daily_steps = steps['steps']
    agents[request.id].collect_health_records(applicant, health_records, daily_steps)
    agents[request.id].generate_health_indices(applicant)
    return {'health_records': applicant.health_records}

@app.post("/posts/upload")
async def upload_posts(id : str = Form(...), posts : List[UploadFile] = File(...)) -> dict:
    '''
    Uploads social media images
    '''
    folder = f"app/data/applicants/{id}"
    os.makedirs(folder, exist_ok=True)
    for index, post in enumerate(posts):
        _, ext = os.path.splitext(post.filename)
        ext = ext.lower() if ext else '.png'
        file_path = os.path.join(folder, f"post_{index}{ext}")
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(post.file, buffer)
        await post.close()
    return {"message": "Posts uploaded successfully"}

@app.post("/posts")
async def collect_social_media_posts(request : ApplicantRequest) -> dict:
    '''
    Extracts insights from posts
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    folder = f"app/data/applicants/{request.id}"
    posts = []
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                path = os.path.join(folder, filename)
                posts.append(path)
    agents[request.id].collect_social_media_posts(applicant, posts)
    agents[request.id].generate_posts_indices(applicant)
    return {'posts': applicant.posts}

@app.post("/spotting")
async def trigger_spotting(request : ApplicantRequest) -> dict:
    '''
    Switches to risk spotting
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    agents[request.id].start_conversation()
    return {"message": "Switched to risk spotting successfully"}

@app.post("/factors")
async def identify_factors(request : ApplicantRequest) -> dict:
    '''
    Identifies the applicant's risks 
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    agents[request.id].identify_factors(applicant)
    factors = agents[request.id].chosen_factors
    return {'factors': json.dumps(factors)}

@app.post("/predictions")
async def make_predictions(request : ApplicantRequest) -> dict:
    '''
    Predicts answers for spotted risks 
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    predictions = agents[request.id].make_factor_predictions(applicant)
    return {'predictions': predictions}

@app.post("/questioning")
async def trigger_questioning(request : ApplicantRequest) -> dict:
    '''
    Switches to dynamic questioning
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    agents[request.id].change_conversation()
    return {"message": "Switched to dynamic questioning"}

@app.post("/question")
async def produce_next_question(request : QuestionRequest) -> dict:
    '''
    Generates the next question
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    question = agents[request.id].produce_next_question(applicant, request.question_index)
    return {'question': question}

@app.post("/answer")
async def save_answer(request : AnswerRequest) -> dict:
    '''
    Saves the answer to a question
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    agents[request.id].save_answer(applicant, request.factor, request.answer)
    answers = applicant.answers
    return {'answers': answers}

@app.post("/record")
async def build_record(request : ApplicantRequest) -> dict:
    '''
    Builds the application record
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    record = agents[request.id].build_record(applicant)
    return {'record': record}

@app.post("/risk")
async def assess_risk(request : ApplicantRequest) -> dict:
    '''
    Scores the applicant's risk
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    risk = agents[request.id].compute_risk(applicant)
    return {'risk': risk}

@app.post("/discrepancies")
async def detect_discrepancies(request : ApplicantRequest) -> dict:
    '''
    Identifies answer discrepancies
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    discrepancies = agents[request.id].identify_discrepancies(applicant)
    return {'discrepancies': discrepancies}

@app.post("/application")
async def save_application(request : ApplicantRequest) -> dict:
    '''
    Saves the application data
    '''
    applicant = applicants.get(request.id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    data = applicant.to_json()
    with open(f"app/data/applications/{data['id']}.json", 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return {"message": "Application saved successfully"}

# -----------------------------------------------------------------------------------------------------------------

@app.put("/mode")
async def update_mode(new_mode : ModeRequest) -> dict:
    '''
    Updates the mode to "traditional" or "dynamic"
    '''
    global app_mode
    mode = new_mode.mode
    if mode not in ['traditional', 'dynamic']:
        raise HTTPException(status_code=400, detail="Mode must be 'traditional' or 'dynamic'")
    app_mode = mode
    return {'mode': mode}

# -----------------------------------------------------------------------------------------------------------------

@app.delete("/applicant/{id}")
async def delete_applicant(id : str) -> dict:
    '''
    Deletes a specific applicant and agent
    '''
    if id not in applicants:
        raise HTTPException(status_code=404, detail="Applicant not found")
    del applicants[id]
    if id in agents:
        del agents[id]
    return {"message": "Applicant deleted successfully"}

@app.delete("/application/{id}")
async def delete_application(id : str) -> dict:
    '''
    Deletes a saved insurance application
    '''
    file_path = f"app/data/applications/{id}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Application not found")
    try:
        os.remove(file_path)
        return {"message": "Application deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete application: {str(e)}")

# -----------------------------------------------------------------------------------------------------------------