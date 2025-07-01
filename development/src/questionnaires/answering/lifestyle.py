# -----------------------------------------------------------------------------------------------------------------

import random

from .health import *

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_answer(applicant : dict, factor : str) -> int:
    '''
    Selects the applicant's answer for a given lifestyle factor
    '''
    return globals()[factor](applicant)

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_job_hazards(applicant: dict) -> int:
    job = applicant['occupation']
    if job in ["Industrial machinery operator", "Forklift driver", "Assembler (electronics)", 
               "Packaging machine operator", "Welder", "Plumber", "Motor vehicle mechanic"]:
        return 0
    if job in ["Crop farm worker", "Livestock worker", "Farmer", "Forestry worker", 
                 "Beekeeper", "Agricultural technician"]:
        return 1
    if job in ["Hotel front desk clerk", "Waiter"]:
        return 2
    if job in ["Crane operator"]:
        return 3 
    if job in ["Fishery worker", "Naval officer"]:
        return 4
    if job in ["Construction manager", "Electrician", "Carpenter", "Tradesperson"]:
        return 5
    if job in ["Military general", "Combat engineer", "Army medic", "Military police officer", 
                "Special forces operative", "Radar operator", "Air force pilot"]:
        return 6 
    if job in ["Security guard", "Medical laboratory technician", "Engineering technician", 
                 "Pharmacy technician", "Tailor"]:  
        return 7
    return 8

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_smoking(applicant: dict) -> int:
    status = ''
    for observation in applicant['health_records']['observations']:
        if observation[0] == 'Tobacco smoking status NHIS':
            status = observation[1]
    if status in ['Never smoker', 'Former smoker']:
        return 4
    if status == 'Current every day smoker':
        tobacco = applicant['demographics'].get('mortality sensitive to tobacco consumption', '')
        smokers = applicant['demographics'].get('smokers aged 15 and over', '')
        if tobacco in ['high', 'very high'] and smokers in ['high', 'very high']:
            probabilities = [0.05, 0.15, 0.4, 0.4]
        elif tobacco in ['low', 'very low'] and smokers in ['low', 'very low']:
            probabilities = [0.35, 0.35, 0.2, 0.1]
        elif tobacco == 'very high' or smokers == 'very high':
            probabilities = [0.05, 0.3, 0.45, 0.2]
        else:
            probabilities = [0.15, 0.25, 0.4, 0.2]
        return random.choices([0, 1, 2, 3], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_diet(applicant: dict) -> int:
    targets = [
        'cake',
        'sugar',
        'chocolate',
        'fries'
    ]
    bad_diet = in_posts(targets, applicant['posts'])
    targets = [
        'salad',
        'soup',
        'cucumbers',
        'vegetables',
        'seeds',
        'eggs'
    ]
    good_diet = in_posts(targets, applicant['posts'])
    answer = health_weight(applicant)
    if answer == 2:
        if bad_diet:
            probabilities = [0.1, 0.1, 0.8]
        elif good_diet:
            probabilities = [0.3, 0.5, 0.2]
        else:
            probabilities = [0.1, 0.5, 0.4]
    else:
        if bad_diet:
            probabilities = [0.1, 0.3, 0.6]
        elif good_diet:
            probabilities = [0.4, 0.5, 0.1]
        else:
            probabilities = [0.2, 0.5, 0.3]
    return random.choices([0, 1, 2], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_exercise(applicant: dict) -> int:
    targets = [
        'exercise',
        'workout',
        'running',
        'squatting',
        'football',
        'yoga',
        'gym'
    ]
    if in_posts(targets, applicant['posts']) or applicant['steps'] >= 8000:
        probabilities = [0.05, 0.1, 0.55, 0.3]
    elif applicant['steps'] <= 4000:
        probabilities = [0.55, 0.3, 0.1, 0.05]
    else:
        lack_exercise = applicant['demographics'].get('population aged 15 and over who do not exercise', '')
        if lack_exercise in ['high', 'very high']:
            probabilities = [0.45, 0.4, 0.1, 0.05]
        elif lack_exercise in ['low', 'very low']:
            probabilities = [0.1, 0.2, 0.5, 0.2]
        else:
            probabilities = [0.35, 0.3, 0.25, 0.1]
    return random.choices([0, 1, 2, 3], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_alcohol(applicant: dict) -> int:
    alcohol = applicant['demographics'].get('alcohol-sensitive mortality', '')
    drinkers = applicant['demographics'].get('drinkers', '')
    if alcohol in ['high', 'very high'] and drinkers in ['high', 'very high']:
        probabilities = [0.3, 0.25, 0.3, 0.1, 0.05]
    elif alcohol in ['low', 'very low'] and drinkers in ['low', 'very low']:
        probabilities = [0.05, 0.1, 0.25, 0.3, 0.3]
    elif alcohol == 'very high' or drinkers == 'very high':
        probabilities = [0.2, 0.25, 0.35, 0.1, 0.1]
    else:
        probabilities = [0.1, 0.15, 0.4, 0.2, 0.15]
    return random.choices([0, 1, 2, 3, 4], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_drugs(applicant: dict) -> int:
    targets = [
        'Drug overdose',
        'Opioid abuse (disorder)',
        'Drug rehabilitation and detoxification'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 0
    drugs = applicant['demographics'].get('problematic drug use', '')
    if drugs in ['high', 'very high']:
        return random.choices([0, 1], [0.3, 0.7])[0]
    elif drugs in ['low', 'very low']:
        return 1
    return random.choices([0, 1], [0.1, 0.9])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_sleep(applicant: dict) -> int:
    return random.choices([0, 1, 2, 3], [0.05, 0.15, 0.65, 0.15])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_stress(applicant: dict) -> int:
    if in_records(['posttraumatic stress disorder'], applicant['health_records']['records']):
        return 0
    job = applicant['occupation']
    if job in [
        "Military general", "Combat engineer", "Army medic", "Military police officer",
        "Special forces operative", "Radar operator", "Naval officer", "Air force pilot",
        "Chief executive officer", "Finance manager", "Sales manager", "Human resources manager",
        "Restaurant manager", "Construction manager", "Medical doctor", "Civil engineer",
        "Lawyer", "Software developer", "Nurse", "Teacher"
    ]:
        probabilities = [0.7, 0.3]
    elif job in [
        "Medical laboratory technician", "Computer network technician", "Broadcasting technician",
        "Engineering technician", "Pharmacy technician", "Social work associate professional",
        "General office clerk", "Receptionist", "Accounting clerk", "Data entry clerk",
        "Mail carrier", "Secretary (general)", "Office worker", "Call center associate"
    ]:
        probabilities = [0.5, 0.5]
    elif job in [
        "Retail salesperson", "Waiter", "Hairdresser", "Security guard", "Travel attendant",
        "Hotel front desk clerk", "Retail worker", "Crop farm worker", "Livestock worker",
        "Farmer", "Forestry worker", "Fishery worker", "Beekeeper", "Agricultural technician",
        "Electrician", "Plumber", "Welder", "Carpenter", "Tailor", "Motor vehicle mechanic",
        "Tradesperson", "Industrial machinery operator", "Forklift driver", "Textile machine operator",
        "Assembler (electronics)", "Crane operator", "Packaging machine operator"
    ]:
        probabilities = [0.25, 0.75]
    else:
        probabilities = [0.35, 0.65]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_healthcare_access(applicant: dict) -> int:
    healthcare = applicant['demographics'].get('accessibility to primary health care', '')
    hospitals = applicant['demographics'].get('accessibility to public hospitals', '')
    if healthcare in ['high', 'very high'] and hospitals in ['high', 'very high']:
        return 0
    if healthcare in ['low', 'very low'] and hospitals in ['low', 'very low']:
        return 1
    elif healthcare == 'very low' or hospitals == 'very low':
        return random.choices([0, 1], [0.4, 0.6])[0]
    return random.choices([0, 1], [0.8, 0.2])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_health_checkups(applicant: dict) -> int:
    if not applicant['health_records']['encounters']:
        return 2
    consultations = applicant['demographics'].get('family medicine consultations', '')
    if applicant['health_records']['careplans']:
        probabilities = [0.15, 0.2, 0.05, 0.55, 0.05]
    elif consultations in ['high', 'very high']:
        probabilities = [0.55, 0.3, 0.05, 0.05, 0.05]
    elif consultations in ['low', 'very low']:
        probabilities = [0.15, 0.2, 0.3, 0.05, 0.3]
    else:
        probabilities = [0.35, 0.4, 0.05, 0.15, 0.05]
    return random.choices([0, 1, 2, 3, 4], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_socioeconomic_status(applicant: dict) -> int:
    income = applicant['demographics'].get('monthly household income', '')
    poverty = applicant['demographics'].get('poverty-sensitive mortality', '')
    if income in ['low', 'very low'] and poverty in ['high', 'very high']:
        probabilities = [0.5, 0.5]
    elif income in ['high', 'very high'] and poverty in ['low', 'very low']:
        probabilities = [0.1, 0.9]
    elif income == 'very low' or poverty == 'very high':
        probabilities = [0.35, 0.65]
    else:
        probabilities = [0.25, 0.75]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_air_pollution(applicant: dict) -> int:
    air = applicant['demographics'].get('urban green space', '')
    if air in ['high', 'very high']:
        return 0
    if air in ['low', 'very low']:
        return 1
    return random.choices([0, 1], [0.6, 0.4])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_unsafe_sex(applicant: dict) -> int:
    targets = [
        'Gonorrhea infection test',
        'Chlamydia antigen test',
        'Human immunodeficiency virus antigen test',
        'Syphilis infection test'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 0
    return random.choices([0, 1], [0.3, 0.7])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_loneliness(applicant: dict) -> int:
    answer = health_mental_illness(applicant)
    if answer == 0:
        return 0
    probabilities = [0.5, 0.5]
    if applicant['age'] >= 65:
        alone = applicant['demographics'].get('elderly population living alone', '')
        if alone in ['high', 'very high']:
            return 0
        if alone in ['low', 'very low']:
            probabilities = [0.2, 0.8]
        else:
            probabilities = [0.4, 0.6]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_crime(applicant: dict) -> int:
    children = applicant['demographics'].get('violence against children', '')
    domestic = applicant['demographics'].get('domestic violence', '')
    if children == 'very high' or domestic == 'very high':
        return 0
    if children in ['low', 'very low'] and domestic in ['low', 'very low']:
        return 1
    return random.choices([0, 1], [0.25, 0.75])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_natural_disasters(applicant: dict) -> int:
    return random.choices([0, 1, 2, 3], [0.25, 0.15, 0.2, 0.4])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_driving(applicant: dict) -> int:
    accidents = applicant['demographics'].get('road accidents with victims', '')
    alcohol = applicant['demographics'].get('alcohol-sensitive mortality', '')
    drinkers = applicant['demographics'].get('drinkers', '')
    if accidents in ['high', 'very high'] and \
        (alcohol in ['high', 'very high'] or drinkers in ['high', 'very high']):
        probabilities = [0.45, 0.55]
    elif accidents in ['high', 'very high']:
        probabilities = [0.35, 0.65]
    else:
        probabilities = [0.2, 0.8]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_dangerous_hobbies(applicant: dict) -> int:
    targets = [
        'surfboard',
        'skis',
        'ski lift',
        'ski gear'
    ]
    if in_posts(targets, applicant['posts']):
        return 0
    return random.choices([0, 1], [0.1, 0.9])[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_housing(applicant: dict) -> int:
    probabilities = [0.25, 0.75]
    overcrowded = applicant['demographics'].get('unsanitary housing', '')
    unsanitary = applicant['demographics'].get('overcrowded accommodation', '')
    heating = applicant['demographics'].get('accommodation without heating', '')
    humidity = applicant['demographics'].get('accommodation with humidity problems', '')
    if overcrowded == 'very high' or unsanitary == 'very high' or heating == 'very high' or humidity == 'very high':
        probabilities = [0.65, 0.35]
    elif overcrowded in ['low', 'very low'] and unsanitary in ['low', 'very low'] and \
    heating in ['low', 'very low'] and humidity in ['low', 'very low']:
        probabilities = [0.15, 0.95]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def lifestyle_green_spaces(applicant: dict) -> int:
    probabilities = [0.5, 0.5]
    targets = [
        'a tree',
        'trees'
    ]
    trees = in_posts(targets, applicant['posts'])
    green = applicant['demographics'].get('urban green space', '')
    access = applicant['demographics'].get('accessibility to the green space', '')
    if trees:
        if green in ['high', 'very high'] and access in ['high', 'very high']:
            probabilities = [0.9, 0.1]
        elif green in ['low', 'very low'] and access in ['low', 'very low']:
            probabilities = [0.3, 0.7]
        elif green == 'very high' or access == 'very high':
            probabilities = [0.8, 0.2]
        else:
            probabilities = [0.4, 0.6]
    else:
        if green in ['high', 'very high'] and access in ['high', 'very high']:
            probabilities = [0.8, 0.2]
        elif green in ['low', 'very low'] and access in ['low', 'very low']:
            probabilities = [0.15, 0.85]
        elif green == 'very high' or access == 'very high':
            probabilities = [0.65, 0.35]
    return random.choices([0, 1], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------