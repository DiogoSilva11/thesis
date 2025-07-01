# -----------------------------------------------------------------------------------------------------------------

import random

from .utils import *

# -----------------------------------------------------------------------------------------------------------------

def health_answer(applicant : dict, factor : str) -> int:
    '''
    Selects the applicant's answer for a given health factor
    '''
    return globals()[factor](applicant)

# -----------------------------------------------------------------------------------------------------------------

def health_cancer(applicant : dict) -> int:
    targets = [
        'Non-small cell lung cancer (disorder)',
        'Small cell carcinoma of lung (disorder)',
        'Non-small cell carcinoma of lung  TNM stage 1 (disorder)',
        'Primary small cell malignant neoplasm of lung  TNM stage 1 (disorder)'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 0
    if in_records(['Malignant neoplasm of breast (disorder)'], applicant['health_records']['records']):
        return 1
    targets = [
        'Metastasis from malignant tumor of prostate (disorder)',
        'Carcinoma in situ of prostate (disorder)',
        'Neoplasm of prostate'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 2
    targets = [
        'Malignant tumor of colon',
        'Primary malignant neoplasm of colon',
        'Secondary malignant neoplasm of colon',
        'Overlapping malignant neoplasm of colon'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 3
    observations = [
        'HER2 [Presence] in Breast cancer specimen by FISH',
        'Site of distant metastasis in Breast tumor',
        'HER2 [Presence] in Breast cancer specimen by Immune stain',
    ]
    breast = False
    for observation in applicant['health_records']['observations']:
        for obs in observations:
            if observation[0] == obs:
                breast = True
                break
    if breast:
        return 1
    observations = [
        'Tumor marker Cancer',
        'Treatment status Cancer',
        'Response to cancer treatment',
        'Stage group.clinical Cancer',
        'Primary tumor.clinical [Class] Cancer',
        'Distant metastases.clinical [Class] Cancer',
        'Regional lymph nodes.clinical [Class] Cancer',
        'Size.maximum dimension in Tumor',
        'Polyp size greatest dimension by CAP cancer protocols'
    ]
    cancer = False
    for observation in applicant['health_records']['observations']:
        for obs in observations:
            if observation[0] == obs:
                cancer = True
                break
    if cancer or in_records(['Cancer care plan'], applicant['health_records']['records']):
        return 4
    return 5

# -----------------------------------------------------------------------------------------------------------------

def health_heart(applicant : dict) -> int:
    targets = [
        'Coronary Heart Disease',
        'Myocardial Infarction',
        'Cardiac Arrest',
        'Heart failure self management plan',
        'Chronic congestive heart failure (disorder)',
        'History of myocardial infarction (situation)',
        'Coronary artery stent (physical object)',
        'Atrial Fibrillation'
    ]
    heart = in_records(targets, applicant['health_records']['records'])
    return 0 if heart else 1

# -----------------------------------------------------------------------------------------------------------------

def health_stroke(applicant : dict) -> int:
    if in_records(['Stroke'], applicant['health_records']['records']):
        return 0
    return 1

# -----------------------------------------------------------------------------------------------------------------

def health_diabetes(applicant : dict) -> int:
    targets = [
        'Neuropathy due to type 2 diabetes mellitus (disorder)',
        'Diabetic retinopathy associated with type II diabetes mellitus (disorder)',
        'Microalbuminuria due to type 2 diabetes mellitus (disorder)',
        'Proliferative diabetic retinopathy due to type II diabetes mellitus (disorder)',
        'Nonproliferative diabetic retinopathy due to type 2 diabetes mellitus (disorder)',
        'Macular edema and retinopathy due to type 2 diabetes mellitus (disorder)'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 1
    targets = [
        'Diabetes',
        'Prediabetes',
        'Hyperglycemia (disorder)',
        'Diabetic renal disease (disorder)'
    ]
    diabetes = in_records(targets, applicant['health_records']['records'])
    return random.choices([0, 1], [0.1, 0.9])[0] if diabetes else 2

# -----------------------------------------------------------------------------------------------------------------

def health_hypertension(applicant : dict) -> int:
    targets = [
        'Hypertension',
        'Lifestyle education regarding hypertension',
        'Hypertension follow-up encounter'
    ]
    hypertension = in_records(targets, applicant['health_records']['records'])
    return 0 if hypertension else 1

# -----------------------------------------------------------------------------------------------------------------

def health_weight(applicant : dict) -> int:
    targets = [
        'Body mass index 40+ - severely obese (finding)',
        'Body mass index 30+ - obesity (finding)'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 2
    bmi = ''
    for observation in applicant['health_records']['observations']:
        if observation[0] == 'Body Mass Index':
            bmi = observation[1]
    if bmi:
        bmi = float(bmi)
        if bmi < 18.5:
            return 0
        elif bmi >= 18.5 and bmi <= 24.9:
            return 1
        else:
            return 2
    obesity = applicant['demographics'].get('obesity in population aged 18 and over', '')
    if applicant['age'] < 18:
        obesity = applicant['demographics'].get('obesity in children and adolescents', '')
    if obesity in ['high', 'very high']:
        probabilities = [0.05, 0.35, 0.6]
    elif obesity in ['low', 'very low']:
        probabilities = [0.2, 0.7, 0.1]
    else:
        probabilities = [0.05, 0.55, 0.4]
    return random.choices([0, 1, 2], probabilities)[0]

# -----------------------------------------------------------------------------------------------------------------

def health_respiratory(applicant : dict) -> int:
    targets = [
        'Childhood asthma',
        'Asthma self management',
        'Asthma follow-up',
        'Emergency hospital admission for asthma',
        'Respiratory therapy',
        'Pneumonia',
        'Pulmonary emphysema (disorder)',
        'Chronic obstructive bronchitis (disorder)',
        'Chronic sinusitis (disorder)',
    ]
    respiratory = in_records(targets, applicant['health_records']['records'])
    return 0 if respiratory else 1

# -----------------------------------------------------------------------------------------------------------------

def health_kidney(applicant : dict) -> int:
    targets = [
        'Renal dialysis (procedure)',
        'Chronic kidney disease stage 1 (disorder)',
        'Chronic kidney disease stage 2 (disorder)',
        'Diabetic renal disease (disorder)'
    ]
    kidney = in_records(targets, applicant['health_records']['records'])
    return 0 if kidney else 1

# -----------------------------------------------------------------------------------------------------------------

def health_anemia(applicant : dict) -> int:
    if in_records(['Anemia (disorder)'], applicant['health_records']['records']):
        return 0
    return 1

# -----------------------------------------------------------------------------------------------------------------

def health_neurological(applicant : dict) -> int:
    targets = [
        'Demential management',
        'Seizure disorder',
        "Alzheimer's disease (disorder)",
        'posttraumatic stress disorder',
        'Child attention deficit disorder'
    ]
    neurological = in_records(targets, applicant['health_records']['records'])
    return 0 if neurological else 1

# -----------------------------------------------------------------------------------------------------------------

def health_mental_illness(applicant : dict) -> int:
    targets = [
        'Major depression disorder',
        'Major depression  single episode',
        'Depression screening',
        'Major depressive disorder clinical management plan',
        'positive screening for depression on phq9',
        'posttraumatic stress disorder',
        'Mental health care plan',
        'Initial Psychiatric Interview with mental status evaluation'
    ]
    mental = in_records(targets, applicant['health_records']['records'])
    return 0 if mental else 1

# -----------------------------------------------------------------------------------------------------------------

def health_liver(applicant : dict) -> int:
    liver = in_records(['Alcoholism'], applicant['health_records']['records'])
    return random.choices([0, 1], [0.2, 0.8])[0] if liver else 1

# -----------------------------------------------------------------------------------------------------------------

def health_cholesterol(applicant : dict) -> int:
    if in_records(['Hyperlipidemia'], applicant['health_records']['records']):
        return 0
    hdl, ldl = '', ''
    for observation in applicant['health_records']['observations']:
        if observation[0] == 'High Density Lipoprotein Cholesterol':
            hdl = observation[1]
        elif observation[0] == 'Low Density Lipoprotein Cholesterol':
            ldl = observation[1]
    if hdl and ldl:
        hdl, ldl = float(hdl), float(ldl)
        if ldl >= 160 and hdl < 45:
            return 0
    return 1

# -----------------------------------------------------------------------------------------------------------------

def health_autoimmune_disease(applicant : dict) -> int:
    autoimmune = in_records(['Rheumatoid arthritis'], applicant['health_records']['records'])
    return 0 if autoimmune else 1

# -----------------------------------------------------------------------------------------------------------------

def health_infections(applicant : dict) -> int:
    targets = [
        'Escherichia coli urinary tract infection',
        'Urinary tract infection care',
        'Recurrent urinary tract infection',
        'Sinusitis (disorder)',
        'Chronic sinusitis (disorder)',
        'Acute bacterial sinusitis (disorder)',
        'Viral sinusitis (disorder)',
        'Nasal sinus endoscopy (procedure)',
        'Streptococcal sore throat (disorder)',
        'Pneumonia',
        'Acute bronchitis (disorder)',
        'Chronic obstructive bronchitis (disorder)'
    ]
    infections = in_records(targets, applicant['health_records']['records'])
    return 0 if infections else 1

# -----------------------------------------------------------------------------------------------------------------

def health_pregnancy(applicant : dict) -> int:
    targets = [
        'Childbirth',
        'Tubal pregnancy',
        'Induced termination of pregnancy',
        'Miscarriage in first trimester',
        'Pregnancy termination care',
        'Premature birth of newborn',
        'Counseling for termination of pregnancy',
        'Blighted ovum',
        'Excision of fallopian tube and surgical removal of ectopic pregnancy',
        'Physical exam following abortion',
        'Cesarean section',
        'Medical induction of labor',
        'Spontaneous breech delivery',
        'Physical examination following birth',
        'Episiotomy',
        'Augmentation of labor'
    ]
    if in_records(targets, applicant['health_records']['records']):
        if applicant['age'] >= 40:
            return 2
        else:
            return random.choices([1, 2], [0.9, 0.1])[0]
    targets = [
        'Normal pregnancy',
        'Fetus with unknown complication',
        'Preeclampsia',
        'Prenatal visit',
        'Routine antenatal care',
        'Fetal anatomy study',
        'Prenatal initial visit',
        'Auscultation of the fetal heart'
    ]
    pregnancy = in_records(targets, applicant['health_records']['records'])
    return 0 if pregnancy else 2

# -----------------------------------------------------------------------------------------------------------------

def health_bones(applicant : dict) -> int:
    targets = [
        'Osteoporosis (disorder)',
        'Pathological fracture due to osteoporosis (disorder)',
        'Rheumatoid arthritis',
        'Localized  primary osteoarthritis of the hand',
        'Osteoarthritis of knee',
        'Osteoarthritis of hip',
        'Chronic pain',
        'Gout'
    ]
    bones = in_records(targets, applicant['health_records']['records'])
    return 0 if bones else 1

# -----------------------------------------------------------------------------------------------------------------

def health_circulatory(applicant : dict) -> int:
    targets = [
        'Coronary artery stent (physical object)',
        'Coronary artery bypass grafting',
        'Percutaneous coronary intervention'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 0
    targets = [
        'Stroke',
        'Myocardial Infarction',
        'Coronary Heart Disease'
    ]
    if in_records(targets, applicant['health_records']['records']):
        probabilities = [0.8, 0.2]
    else:
        probabilities = [0.15, 0.85]
    return random.choices([0, 1], probabilities)[0]
            
# -----------------------------------------------------------------------------------------------------------------

def health_injury(applicant : dict) -> int:
    targets = [
        'Brain damage - traumatic',
        'Concussion injury of brain',
        'Concussion with loss of consciousness',
        'Concussion with no loss of consciousness',
        'Admission to trauma surgery department',
        'Head injury rehabilitation'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 0
    targets = [
        'Spinal cord injury rehabilitation',
        'Fracture of the vertebral column with spinal cord injury',
        'Fracture of vertebral column without spinal cord injury'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 1
    targets = [
        'Burn care',
        'Second degree burn',
        'Burn injury(morphologic abnormality)'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 2
    targets = [
        'Bullet wound',
        'Fracture of rib',
        'Chest X-ray',
        'Plain chest X-ray',
        'Plain chest X-ray (procedure)'
    ]
    if in_records(targets, applicant['health_records']['records']) and \
    random.randint(0, 1) == 0:
        return 3
    targets = [
        'Closed fracture of hip',
        'Pelvis X-ray',
        'Digital Radiography: Pelvis'
    ]
    if in_records(targets, applicant['health_records']['records']):
        return 4
    return random.choices([5, 6], [0.1, 0.9])[0]

# -----------------------------------------------------------------------------------------------------------------

def health_digestive_condition(applicant : dict) -> int:
    targets = [
        'Bleeding from anus',
        'Protracted diarrhea',
        'Screening for occult blood in feces (procedure)'
    ]
    digestive = in_records(targets, applicant['health_records']['records'])
    return random.choices([0, 1], [0.2, 0.8])[0] if digestive else 1

# -----------------------------------------------------------------------------------------------------------------