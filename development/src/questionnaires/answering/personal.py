# -----------------------------------------------------------------------------------------------------------------

import random

# -----------------------------------------------------------------------------------------------------------------

def personal_answer(applicant : dict, factor : str) -> int | str:
    '''
    Selects the applicant's answer for a given personal factor
    '''
    return globals()[factor](applicant)

# -----------------------------------------------------------------------------------------------------------------

def personal_age(applicant: dict) -> int:
    age = applicant['age']
    if age <= 24:
        return 0
    if age >= 25 and age <= 39:
        return 1
    if age >= 40 and age <= 59:
        return 2
    if age >= 60:
        return 3

# -----------------------------------------------------------------------------------------------------------------

def personal_gender(applicant: dict) -> int:
    gender = applicant['gender']
    if gender == 'male':
        return 0
    if gender == 'female':
        return 1
    return 2

# -----------------------------------------------------------------------------------------------------------------
    
def personal_marital(applicant: dict) -> int:
    marital = applicant['health_records']['patient']['MARITAL']
    if marital == 'S':
        return 0
    if marital == 'M':
        return 1
    age = applicant['age']
    if age >= 40 and age < 70:
        return random.choice([2, 4])
    if age >= 70:
        return random.choice([2, 3, 4])
    return 0

# -----------------------------------------------------------------------------------------------------------------

def personal_location(applicant: dict) -> int:
    municipalities = [
        "Alfândega da Fé",
        "Amares",
        "Braga",
        "Bragança",
        "Gondomar",
        "Maia",
        "Matosinhos",
        "Monção",
        "Paredes",
        "Penafiel",
        "Porto",
        "Póvoa de Lanhoso",
        "Santo Tirso",
        "Valença",
        "Valongo",
        "Viana do Castelo",
        "Vila Nova de Famalicão",
        "Vila Pouca de Aguiar",
        "Vila Real",
        "Alenquer",
        "Coimbra",
        "Figueira da Foz",
        "Guarda",
        "Lourinhã",
        "Lousã",
        "Miranda do Corvo",
        "Pombal",
        "Soure",
        "Tábua",
        "Torres Vedras",
        "Alcochete",
        "Almada",
        "Amadora",
        "Barreiro",
        "Lisboa",
        "Loures",
        "Montijo",
        "Odivelas",
        "Oeiras",
        "Palmela",
        "Seixal",
        "Sesimbra",
        "Setúbal",
        "Vila Franca de Xira",
        "Almodôvar",
        "Alvito",
        "Avis",
        "Azambuja",
        "Barrancos",
        "Beja",
        "Chamusca",
        "Cuba",
        "Golegã",
        "Grândola",
        "Odemira",
        "Serpa",
        "Viana do Alentejo",
        "Vidigueira",
        "Castro Marim",
        "Lagoa",
        "Loulé",
        "Monchique",
        "Portimão",
        "Tavira",
        "Calheta (Açores)",
        "Lagoa (Açores)",
        "Ponta Delgada (Açores)",
        "Ribeira Grande (Açores)",
        "São Roque do Pico (Açores)",
        "Porto Santo (Madeira)"
    ]
    return municipalities.index(applicant['municipality'])

# -----------------------------------------------------------------------------------------------------------------

def personal_occupation(applicant: dict) -> int:
    occupations = [
        "Student",
        "Retired",
        "Military general", 
        "Combat engineer", 
        "Army medic", 
        "Military police officer",
        "Special forces operative", 
        "Radar operator", 
        "Naval officer", 
        "Air force pilot",
        "Chief executive officer", 
        "Finance manager", 
        "Sales manager", 
        "Human resources manager",
        "Restaurant manager", 
        "Construction manager",
        "Medical doctor", 
        "Civil engineer", 
        "Lawyer", 
        "Software developer",
        "Nurse", 
        "Teacher",
        "Medical laboratory technician", 
        "Computer network technician", 
        "Broadcasting technician",
        "Engineering technician", 
        "Pharmacy technician", 
        "Social work associate professional",
        "General office clerk", 
        "Receptionist", 
        "Accounting clerk", 
        "Data entry clerk",
        "Mail carrier", 
        "Secretary (general)", 
        "Office worker", 
        "Call center associate",
        "Retail salesperson", 
        "Waiter", 
        "Hairdresser", 
        "Security guard", 
        "Travel attendant",
        "Hotel front desk clerk", 
        "Retail worker",
        "Crop farm worker", 
        "Livestock worker", 
        "Farmer", 
        "Forestry worker",
        "Fishery worker", 
        "Beekeeper", 
        "Agricultural technician",
        "Electrician", 
        "Plumber", 
        "Welder", 
        "Carpenter", 
        "Tailor",
        "Motor vehicle mechanic", 
        "Tradesperson",
        "Industrial machinery operator", 
        "Forklift driver", 
        "Textile machine operator",
        "Assembler (electronics)", 
        "Crane operator", 
        "Packaging machine operator"
    ]
    return occupations.index(applicant['occupation'])

# -----------------------------------------------------------------------------------------------------------------