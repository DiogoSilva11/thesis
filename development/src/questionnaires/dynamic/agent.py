# -----------------------------------------------------------------------------------------------------------------

import json
import math

import pandas as pd

from openai import AzureOpenAI
from openai import ChatCompletion
from typing import List
from PIL import Image

from rag import *
from applicant import Applicant

# -----------------------------------------------------------------------------------------------------------------

CATEGORIES = [
    'personal',
    'lifestyle',
    'family',
    'health'
]

GEO_INDICATORS = [
    'mortality',
    'morbidity',
    'healthcare',
    'lifestyle',
    'education',
    'socioeconomic',
    'environment',
    'infrastructure',
    'security'
]

SOURCES = {
    "info": "Basic user information",
    "geo": "Indicators from the user's city",
    "health": "Data from the user's health records",
    "posts": "Images from the user's social media"
}

MAX_ATTEMPTS = 3

# -----------------------------------------------------------------------------------------------------------------

class Agent:
    def __init__(
        self,
        id : str,
        instance : AzureOpenAI,
        model : str,
        embeddings : SentenceTransformer
    ) -> None:
        '''
        Initializes an automated agent for life insurance underwriting tasks
        '''
        self.id = id
        self.instance = instance
        self.model = model
        self.embeddings = embeddings
        self.conversation = []
        self.user_insights = ''
        self.chosen_factors = []
        self.load_questions()

    # -------------------------------------------------------------------------------------------------------------

    def load_questions(self) -> None:
        '''
        Loads life risks and respective questions regarding different questionnaire sections
        '''
        self.questions = {}
        for category in CATEGORIES:
            with open(f"../../../data/questionnaires/questions/{category}.json", 'r', encoding='utf-8') as file:
                self.questions[category] = json.load(file)
        self.all_factors = []
        for category in CATEGORIES[1:]:
            self.all_factors += list(self.questions[category].keys())
    
    # -------------------------------------------------------------------------------------------------------------

    def save_answer(self, applicant : Applicant, factor : str, answer : int) -> str:
        '''
        Saves the applicant's answer to a question
        '''
        applicant.answers[factor] = answer
        category = factor.split('_', 1)[0]
        question = self.questions[category][factor]['question']
        options = self.questions[category][factor]['options']
        return f"{question}\n- {options[answer]}\n"

    # -------------------------------------------------------------------------------------------------------------

    def collect_basic_info(self, applicant : Applicant) -> None:
        '''
        Collects basic information about the applicant
        '''
        basic_info = []
        for key, value in applicant.answers.items():
            if 'personal' in key:
                factor = key.split('_', 1)[1]
                options = self.questions['personal'][key]['options']
                answer = options[value]
                basic_info.append(f"{factor}: {answer}")
        applicant.basic_info = basic_info

    # -------------------------------------------------------------------------------------------------------------

    def collect_geo_indicators(self, applicant : Applicant, municipality : str) -> None:
        '''
        Fetches the main risk indicators from the applicant's municipality
        '''
        demographics = {}
        for indicator in GEO_INDICATORS:
            content = pd.read_csv(f"../../../data/demographics/processed/{indicator}.csv", encoding='utf-8')
            if municipality in content['municipality'].values:
                data = content[content['municipality'] == municipality].iloc[0]
                for column in data.index[1:]:
                    value = data[column]
                    if value in ['very low', 'very high']:
                        demographics[column] = value
        applicant.geo_indicators = [f"{key}: {value}" for key, value in demographics.items()]

    # -------------------------------------------------------------------------------------------------------------

    def collect_health_records(self, applicant : Applicant, health_records : dict, daily_steps : int) -> None:
        '''
        Processes data from the applicant's health records
        '''
        health = []
        if health_records:
            sections = [
                'allergies',
                'careplans',
                'conditions',
                'devices',
                'encounters',
                'imagings',
                'immunizations',
                'medications',
                'procedures'
            ]
            for section in sections:
                health += health_records[section]
            for observation in health_records['observations']:
                health.append(
                    f"{observation[0]}: {observation[1]} {observation[2]}"
                )
        if daily_steps is not None:
            health.append(f"Average Physical Activity: {daily_steps} steps/day")
        applicant.health_records = list(set(health))

    # -------------------------------------------------------------------------------------------------------------

    def collect_social_media_posts(self, applicant : Applicant, posts : List[str]) -> None:
        '''
        Collects descriptions from the images posted by the applicant on social media
        '''
        applicant.posts = posts

    # -------------------------------------------------------------------------------------------------------------

    def generate_geo_indices(self, applicant : Applicant) -> None:
        '''
        Generates FAISS indices for the applicant storing geographical data
        '''
        if applicant.geo_indicators:
            geo_embeddings = generate_embeddings(self.embeddings, applicant.geo_indicators)
            applicant.geo_index = generate_faiss_indices(geo_embeddings)

    # -------------------------------------------------------------------------------------------------------------

    def generate_health_indices(self, applicant : Applicant) -> None:
        '''
        Generates FAISS indices for the applicant storing health data
        '''
        if applicant.health_records:
            health_embeddings = generate_embeddings(self.embeddings, applicant.health_records)
            applicant.health_index = generate_faiss_indices(health_embeddings)
        
    # -------------------------------------------------------------------------------------------------------------

    def generate_posts_indices(self, applicant : Applicant) -> None:
        '''
        Generates FAISS indices for the applicant storing social media data
        '''
        if applicant.posts:
            posts_embeddings = generate_embeddings(self.embeddings, applicant.posts)
            applicant.posts_index = generate_faiss_indices(posts_embeddings)

    # -------------------------------------------------------------------------------------------------------------

    def gather_user_insights(self, applicant : Applicant) -> None:
        '''
        Gathers relevant user insights
        '''
        indices = applicant.get_all_indices()
        data = applicant.get_all_data()
        insights = ''
        for source, description in SOURCES.items():
            if source in data:
                if source == 'info':
                    results = data[source]
                else:
                    top_k = 3 if source == 'health' else 1
                    results = self.gather_insights(
                        indices[source],
                        data[source],
                        self.all_factors,
                        top_k
                    )
                info = "\n".join(f"- {result}" for result in results)
                insights += f"{description}:\n{info}\n\n"
        self.user_insights = insights
    
    # -------------------------------------------------------------------------------------------------------------

    def gather_insights(self, index : faiss.IndexFlatL2, docs : list[str], factors : list[str], top_k : int) -> list[str]:
        '''
        Retrieves contextual information from documents regarding certain factors
        '''
        results = []
        for factor in factors:
            query = factor.split('_', 1)[1]
            query = query.replace('_', ' ')
            results += query_faiss(self.embeddings, index, docs, query, top_k)
        results = list(set(results))
        return results
    
    # -------------------------------------------------------------------------------------------------------------

    def start_conversation(self) -> None:
        '''
        Starts the conversation with the agent by explaining the main task
        '''
        self.conversation = []
        factor_list = ''
        for factor in self.all_factors:
            factor_list += f"{factor}\n"
        system = f"""You are a life insurance expert in mortality risk assessment.
You will be provided with user insights.
Your task is to identify all risk factors present in a negative or risky way.
Find as many factors as you can, even if they are not so obvious.
You are only allowed to select from this exact list of risk factors (delimited by triple backticks).
```
{factor_list}```

Simply return in this JSON format:
[
    "factor_a",
    "factor_b", 
    "factor_c"
]"""
        self.conversation.append({'role': 'system', 'content': system})
        self.chosen_factors = []

    # -------------------------------------------------------------------------------------------------------------

    def is_json_convertible(self, string : str) -> bool:
        '''
        Verifies if a string is convertible to JSON format
        '''
        try:
            json.loads(string)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    # -------------------------------------------------------------------------------------------------------------

    def process_factors(self, factors : list[str]) -> list[str]:
        '''
        Process factors to remove invalid ones
        '''
        processed = []
        for factor in factors:
            category = factor.split('_', 1)[0]
            if category in self.questions and factor in self.questions[category]:
                processed.append(factor)
        return processed
    
    # -------------------------------------------------------------------------------------------------------------

    def identify_factors(self, applicant : Applicant) -> None:
        '''
        Identifies the risk factors in the user data
        '''
        self.gather_user_insights(applicant)
        self.conversation.append({'role': 'user', 'content': self.user_insights})
        for _ in range(MAX_ATTEMPTS):
            response = self.instance.chat.completions.create(
                model=self.model, 
                messages=self.conversation,
                temperature=0
            )
            choices = response.choices[0].message.content.strip()
            if self.is_json_convertible(choices):
                factors = json.loads(choices)
                if isinstance(factors, list):
                    valid = True
                    for factor in factors:
                        category = factor.split('_', 1)[0]
                        if category not in self.questions or factor not in self.questions[category]:
                            valid = False
                            break
                    if valid:
                        self.chosen_factors = factors
                        self.conversation.append({'role': 'assistant', 'content': choices})
                        return
        print(f"[AGENT] Error - invalid factors: {choices}")
        processed = []
        if self.is_json_convertible(choices):
            factors = json.loads(choices)
            if isinstance(factors, list):
                processed = self.process_factors(factors)
        self.chosen_factors = processed
        self.conversation.append({'role': 'assistant', 'content': json.dumps(processed, indent=4)})
    
    # -------------------------------------------------------------------------------------------------------------

    def predict_answer(self, question : str, option_list : list[str]) -> tuple[ChatCompletion, dict]:
        """
        Uses GPT to predict the answer of a multiple-choice question
        """
        options = "\n".join([f"{i}. {g}" for i, g in enumerate(option_list)])
        prediction_prompt = """Predict the correct answer. Simply return in this JSON format:
{
    "answer": 0,
    "explanation": "Brief reasoning behind the prediction."
}"""
        note = "Note: These are only some of the insights, other details may be missing.\n"
        prompt = f"""{self.user_insights + note}
Question for the user:
{question}
{options}

{prediction_prompt}"""
        response = None
        for _ in range(MAX_ATTEMPTS):
            response = self.instance.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                logprobs=True
            )
            prediction = response.choices[0].message.content.strip()
            if self.is_json_convertible(prediction):
                return response, json.loads(prediction)
        print(f"[AGENT] Error - invalid prediction: {prediction}")
        return response, {}

    # -------------------------------------------------------------------------------------------------------------

    def get_prediction_confidence(self, response : ChatCompletion) -> float:
        """
        Extracts the predicted option and respective token confidence
        """
        token_index = 6
        token = response.choices[0].logprobs.content[token_index]
        confidence = round(math.exp(token.logprob), 3)
        return confidence
    
    # -------------------------------------------------------------------------------------------------------------

    def make_factor_predictions(self, applicant : Applicant) -> list[dict]:
        '''
        Makes predictions for each question of the pre-selected factors
        '''
        predictions = []
        for factor in self.chosen_factors:
            category = factor.split('_', 1)[0]
            question = self.questions[category][factor]['question']
            options = self.questions[category][factor]['options']
            content = {
                'factor': factor,
                'question': question,
                'options': options
            }
            applicant.questions.append(content)
            response, prediction = self.predict_answer(question, options)
            content['prediction'] = prediction['answer']
            content['confidence'] = self.get_prediction_confidence(response)
            content['explanation'] = prediction['explanation']
            applicant.answers[factor] = prediction['answer']
            predictions.append(content)
        return predictions
    
    # -------------------------------------------------------------------------------------------------------------

    def build_record(self, applicant : Applicant) -> None:
        '''
        Builds the applicant's questionnaire record
        '''
        record = []
        for item in applicant.questions:
            content = item
            content['answer'] = applicant.answers[item['factor']]
            record.append(content)
        applicant.record = record

    # -------------------------------------------------------------------------------------------------------------

    def record_text(self, applicant : Applicant) -> str:
        '''
        Creates a string containing the questions and answers
        '''
        text = ''
        for item in applicant.questions:
            factor = item['factor']
            question = item['question']
            answer = item['options'][applicant.answers[factor]]
            text += f"{question}\n- {answer}\n\n"
        return text

    # -------------------------------------------------------------------------------------------------------------

    def change_conversation(self) -> None:
        '''
        Changes the conversation to suit dynamic question selection
        '''
        self.conversation = []
        system = """You are assisting with selecting questions for a life insurance applicant.

You will receive:
- a partially completed questionnaire
- a list of remaining risk factors

Select a risk factor only if at least one of the following is true:
- the factor is impactful for assessing mortality risk
- there is a realistic chance the applicant's response may be negative or unhealthy

Then, take one of the following actions:
1. If at least one factor meets the above conditions:
   - reply with the factor name only (exactly as listed)

2. If none of the remaining factors meet the conditions:
   - reply with 'exit' only"""
        self.conversation.append({'role': 'system', 'content': system})

    # -------------------------------------------------------------------------------------------------------------

    def select_question(self, applicant : Applicant) -> tuple[str, int]:
        '''
        Selects a new factor to address in the questionnaire
        '''
        text = self.record_text(applicant)
        remaining_factors = ''
        for factor in self.all_factors:
            if factor not in self.chosen_factors:
                category = factor.split('_', 1)[0]
                if category != 'health':
                    remaining_factors += f"{factor}\n"
        prompt = f"""Here is the life insurance questionnaire, delimited by triple backticks.

```
{text}```

Remaining risk factors:
{remaining_factors}"""
        for attempt in range(MAX_ATTEMPTS):
            response = self.instance.chat.completions.create(
                model=self.model, 
                messages=self.conversation+[{'role': 'user', 'content': prompt}],
                max_tokens=10,
                temperature=0
            )
            factor = response.choices[0].message.content.strip()
            if factor == 'exit':
                return factor, attempt
            category = factor.split('_', 1)[0]
            if category in self.questions and factor in self.questions[category] and factor not in self.chosen_factors:
                self.chosen_factors.append(factor)
                return factor, attempt
        print(f"[AGENT] Error - invalid factor: {factor}")
        return 'exit', MAX_ATTEMPTS
    
    # -------------------------------------------------------------------------------------------------------------

    def produce_next_question(self, applicant : Applicant, index : str = 0) -> tuple[dict, int]:
        '''
        Produces the next question given the current questionnaire progress
        '''
        factor, errors = self.select_question(applicant)
        content = {}
        if factor != 'exit':
            category = factor.split('_', 1)[0]
            question = self.questions[category][factor]['question']
            option_list = self.questions[category][factor]['options']
            content = {
                'questionId': index + 1,
                'factor': factor,
                'question': question,
                'options': option_list
            }
            applicant.questions.append(content)
        return content, errors

# -----------------------------------------------------------------------------------------------------------------