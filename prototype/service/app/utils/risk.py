# -----------------------------------------------------------------------------------------------------------------

import json

# -----------------------------------------------------------------------------------------------------------------

CATEGORIES = [
    'personal',
    'lifestyle',
    'family',
    'health'
]

COMBINATIONS = [
    'family_health',
    'family_lifestyle',
    'health_lifestyle'
]

# -----------------------------------------------------------------------------------------------------------------

def load_weights() -> tuple[dict, list[dict]]:
    '''
    Loads the risk weights for the options of each question and possible combinations
    '''
    data_folder = 'app/data/weights'
    all_weights = {}
    for category in CATEGORIES:
        with open(f"{data_folder}/{category}.json", 'r') as file:
            weights = json.load(file)
        all_weights.update(weights)
    all_combinations = []
    for combination in COMBINATIONS:
        with open(f"{data_folder}/combinations/{combination}.json", 'r') as file:
            combinations = json.load(file)
        all_combinations += combinations
    return all_weights, all_combinations

# -----------------------------------------------------------------------------------------------------------------

def detect_combination(answers : dict, combination : dict) -> bool:
    '''
    Looks for a combination of factors with certain values within the answers
    '''
    for factor, choices in combination['combination'].items():
        if factor not in answers or answers[factor] not in choices:
            return False
    return True

# -----------------------------------------------------------------------------------------------------------------

def mortality_risk(answers : dict, weights : dict, combinations : list[dict]) -> int:
    '''
    Assigns a mortality risk score to a set of answers
    '''
    final_score = 0
    for factor, answer in answers.items():
        score = weights[factor][answer]
        final_score += score
    for item in combinations:
        if detect_combination(answers, item):
            final_score += item['weight']
    return final_score

# -----------------------------------------------------------------------------------------------------------------

def identify_risks(answers : dict, weights : dict) -> list[str]:
    '''
    Identifies the present risks in a set of answers
    '''
    factors = []
    for factor, answer in answers.items():
        score = weights[factor][answer]
        if score > 0:
            factors.append(factor)
    return factors

# -----------------------------------------------------------------------------------------------------------------