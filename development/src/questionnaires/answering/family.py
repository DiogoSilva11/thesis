# -----------------------------------------------------------------------------------------------------------------

import random

from .health import *

# -----------------------------------------------------------------------------------------------------------------

def family_answer(applicant : dict, factor : str) -> int:
    '''
    Selects the applicant's answer for a given family factor
    '''
    return globals()[factor](applicant)

# -----------------------------------------------------------------------------------------------------------------

def family_cancer(applicant : dict) -> int:
    probabilities = [0.1, 0.1, 0.1, 0.05, 0.05, 0.6]
    child_answer = health_cancer(applicant)
    if child_answer == 5:
        tumors = applicant['demographics'].get('mortality from malignant tumors', '')
        if tumors in ['low', 'very low']:
            probabilities = [0.05, 0.05, 0.05, 0.05, 0.05, 0.75]
        elif tumors in ['high', 'very high']:
            probabilities = [0.2, 0.2, 0.2, 0.1, 0.1, 0.2]
    else:
        probabilities[child_answer] += 0.5
        probabilities[5] -= 0.5
    return random.choices([0, 1, 2, 3, 4, 5], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_heart(applicant: dict) -> int:
    probabilities = [0.1, 0.25, 0.65]
    child_answer = health_heart(applicant)
    if child_answer == 0:
        aging = applicant['demographics'].get('aging index', '')
        if aging in ['low', 'very low']:
            probabilities = [0.35, 0.35, 0.3]
        elif aging in ['high', 'very high']:
            probabilities = [0.05, 0.65, 0.3]
        else:
            probabilities = [0.2, 0.5, 0.3]
    return random.choices([0, 1, 2], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_stroke(applicant : dict) -> int:
    probabilities = [0.1, 0.25, 0.65]
    child_answer = health_stroke(applicant)
    if child_answer == 0:
        aging = applicant['demographics'].get('aging index', '')
        if aging in ['low', 'very low']:
            probabilities = [0.35, 0.35, 0.3]
        elif aging in ['high', 'very high']:
            probabilities = [0.05, 0.65, 0.3]
        else:
            probabilities = [0.2, 0.5, 0.3]
    return random.choices([0, 1, 2], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_diabetes(applicant : dict) -> int:
    probabilities = [0.05, 0.3, 0.65]
    child_answer = health_diabetes(applicant)
    if child_answer == 0:
        probabilities = [0.4, 0.3, 0.3]
    elif child_answer == 1:
        probabilities = [0.05, 0.65, 0.3]
    elif child_answer == 2:
        diabetes = applicant['demographics'].get('diabetes', '')
        mortality = applicant['demographics'].get('diabetes mortality', '')
        if diabetes in ['high', 'very high'] and mortality in ['high', 'very high']:
            probabilities = [0.05, 0.45, 0.5]
        elif diabetes in ['low', 'very low'] and mortality in ['low', 'very low']:
            probabilities = [0.05, 0.15, 0.8]
        elif diabetes == 'very high' or mortality == 'very high':
            probabilities = [0.05, 0.55, 0.4]
    return random.choices([0, 1, 2], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_hypertension(applicant : dict) -> int:
    probabilities = [0.4, 0.6]
    child_answer = health_hypertension(applicant)
    if child_answer == 0:
        probabilities = [0.7, 0.3]
    elif child_answer == 1:
        hypertension = applicant['demographics'].get('high blood pressure', '')
        if hypertension in ['high', 'very high']:
            probabilities = [0.6, 0.4]
        elif hypertension in ['low', 'very low']:
            probabilities = [0.2, 0.8]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_kidney(applicant : dict) -> int:
    probabilities = [0.15, 0.85]
    child_answer = health_kidney(applicant)
    if child_answer == 0:
        probabilities = [0.4, 0.6]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_neurological(applicant : dict) -> int:
    if in_records(["Familial Alzheimer's disease of early onset (disorder)"], applicant['health_records']['records']):
        return 0
    probabilities = [0.15, 0.85]
    child_answer = health_neurological(applicant)
    if child_answer == 0:
        probabilities = [0.6, 0.4]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_epilepsy(applicant : dict) -> int:
    probabilities = [0.05, 0.95]
    targets = [
        'Epilepsy',
        'Seizure disorder',
        'Seizure Count Cerebral Cortex Electroencephalogram (EEG)',
        'History of single seizure (situation)'
    ]
    if in_records(targets, applicant['health_records']['records']) == 0:
        probabilities = [0.7, 0.3]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_longevity(applicant : dict) -> int:
    probabilities = [0.6, 0.4]
    aging = applicant['demographics'].get('aging index', '')
    if aging in ['low', 'very low']:
        probabilities = [0.3, 0.7]
    elif aging in ['high', 'very high']:
        probabilities = [0.7, 0.3]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_death_cause(applicant : dict) -> int:
    probabilities = [0.35, 0.25, 0.15, 0.1, 0.05, 0.1]
    cancer = applicant['demographics'].get('mortality from malignant tumors', '')
    accident = applicant['demographics'].get('road accidents with victims', '')
    if cancer in ['high', 'very high']:
        if accident in ['high', 'very high']:
            probabilities = [0.15, 0.4, 0.05, 0.25, 0.05, 0.1]
        elif accident in ['low', 'very low']:
            probabilities = [0.25, 0.4, 0.15, 0.05, 0.05, 0.1]
        else:
            probabilities = [0.2, 0.4, 0.15, 0.1, 0.05, 0.1]
    elif cancer in ['low', 'very low']:
        if accident in ['high', 'very high']:
            probabilities = [0.35, 0.1, 0.15, 0.25, 0.05, 0.1]
        elif accident in ['low', 'very low']:
            probabilities = [0.35, 0.1, 0.2, 0.05, 0.2, 0.1]
        else:
            probabilities = [0.35, 0.1, 0.2, 0.1, 0.15, 0.1]
    else:
        if accident in ['high', 'very high']:
            probabilities = [0.25, 0.25, 0.1, 0.25, 0.05, 0.1]
        elif accident in ['low', 'very low']:
            probabilities = [0.35, 0.25, 0.15, 0.05, 0.1, 0.1]
    return random.choices([0, 1, 2, 3, 4, 5], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_mental_illness(applicant : dict) -> int:
    probabilities = [0.2, 0.8]
    child_answer = health_mental_illness(applicant)
    if child_answer == 0:
        probabilities = [0.6, 0.4]
    elif child_answer == 1:
        mental = applicant['demographics'].get('hospitalizations for mental illness', '')
        if mental in ['high', 'very high']:
            probabilities = [0.35, 0.65]
        elif mental in ['low', 'very low']:
            probabilities = [0.05, 0.95]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_bones(applicant : dict) -> int:
    probabilities = [0.3, 0.7]
    child_answer = health_bones(applicant)
    if child_answer == 0:
        probabilities = [0.5, 0.5]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_obesity(applicant : dict) -> int:
    probabilities = [0.3, 0.7]
    child_answer = health_weight(applicant)
    if child_answer == 2:
        probabilities = [0.5, 0.5]
    elif child_answer in [0, 1]:
        obesity = applicant['demographics'].get('obesity in population aged 18 and over', '')
        if obesity in ['high', 'very high']:
            probabilities = [0.7, 0.3]
        elif obesity in ['low', 'very low']:
            probabilities = [0.2, 0.8]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_cholesterol(applicant : dict) -> int:
    probabilities = [0.35, 0.65]
    child_answer = health_cholesterol(applicant)
    if child_answer == 0:
        probabilities = [0.8, 0.2]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_liver(applicant : dict) -> int:
    probabilities = [0.1, 0.9]
    drinkers = applicant['demographics'].get('drinkers', '')
    alcohol = applicant['demographics'].get('alcohol-sensitive mortality', '')
    if drinkers in ['high', 'very high'] and alcohol in ['high', 'very high']:
        probabilities = [0.4, 0.6]
    elif drinkers in ['low', 'very low'] and alcohol in ['low', 'very low']:
        probabilities = [0.05, 0.95]
    elif drinkers == 'very high' or alcohol == 'very high':
        probabilities = [0.3, 0.7]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_autoimmune_disease(applicant : dict) -> int:
    probabilities = [0.05, 0.95]
    child_answer = health_autoimmune_disease(applicant)
    if child_answer == 0:
        probabilities = [0.7, 0.3]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_anemia(applicant : dict) -> int:
    probabilities = [0.1, 0.9]
    child_answer = health_anemia(applicant)
    if child_answer == 0:
        probabilities = [0.55, 0.45]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_pregnancy(applicant : dict) -> int:
    probabilities = [0.15, 0.85]
    targets = [
        'Tubal pregnancy',
        'Miscarriage in first trimester',
        'Premature birth of newborn',
        'Blighted ovum',
        'Fetus with unknown complication',
        'Preeclampsia'
    ]
    if in_records(targets, applicant['health_records']['records']):
        probabilities = [0.6, 0.4]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_circulatory(applicant : dict) -> int:
    probabilities = [0.2, 0.8]
    child_answer = health_circulatory(applicant)
    if child_answer == 0:
        probabilities = [0.7, 0.3]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def family_respiratory(applicant : dict) -> int:
    probabilities = [0.25, 0.75]
    child_answer = health_respiratory(applicant)
    if child_answer == 0:
        probabilities = [0.5, 0.5]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------