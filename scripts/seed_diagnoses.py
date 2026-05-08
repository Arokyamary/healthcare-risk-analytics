import pandas as pd
from sqlalchemy import create_engine
import uuid, random

engine = create_engine('postgresql://postgres:postgres@127.0.0.1:5432/healthcare_db')
patients_df = pd.read_sql('SELECT id FROM patients', engine)

ICD_CODES = ['E11.9','I10','J44.1','N18.3','Z79.899','E78.5','I25.10']
diagnoses = []
for _, pat in patients_df.iterrows():
    for _ in range(random.randint(1, 5)):
        diagnoses.append({
            'id': str(uuid.uuid4()),
            'patient_id': str(pat['id']),
            'icd10_code': random.choice(ICD_CODES),
            'chronic_flag': random.random() < 0.6,
            'description': 'Auto generated'
        })

dx_df = pd.DataFrame(diagnoses)
dx_df.to_sql('diagnoses', engine, if_exists='append', index=False)
print(f'Inserted {len(dx_df)} diagnoses')