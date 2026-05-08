import pandas as pd
import numpy as np
from faker import Faker
from sqlalchemy import create_engine
import uuid, random
from datetime import datetime, timedelta

fake = Faker('en_IN')
np.random.seed(42)
random.seed(42)

DB_URL = "postgresql://postgres:postgres@127.0.0.1:5432/healthcare_db"
engine = create_engine(DB_URL)

N_PATIENTS = 5000
print(f"Generating {N_PATIENTS} synthetic patients...")

INSURANCE = ['Medicare', 'Medicaid', 'Commercial', 'Uninsured']
GENDERS = ['Male', 'Female', 'Other']
RACES = ['White', 'Black', 'Hispanic', 'Asian', 'Other']

patients = []
for i in range(N_PATIENTS):
    dob = fake.date_of_birth(minimum_age=18, maximum_age=95)
    patients.append({
        'id': str(uuid.uuid4()),
        'mrn': f'MRN{100000 + i}',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'date_of_birth': dob,
        'gender': random.choice(GENDERS),
        'race': random.choice(RACES),
        'zip_code': fake.postcode(),
        'insurance_type': random.choice(INSURANCE),
        'is_active': True,
    })

patients_df = pd.DataFrame(patients)
patients_df.to_sql('patients', engine, if_exists='append', index=False)
print(f"Inserted {len(patients_df)} patients")

print("Generating encounters...")
encounters = []
for _, pat in patients_df.iterrows():
    n_enc = np.random.poisson(3)
    for _ in range(max(1, n_enc)):
        admit = fake.date_time_between(start_date='-2y', end_date='now')
        los = max(1, np.random.exponential(4))
        enc_type = random.choices(
            ['inpatient','outpatient','emergency'],
            weights=[0.25, 0.55, 0.20])[0]
        encounters.append({
            'id': str(uuid.uuid4()),
            'patient_id': pat['id'],
            'encounter_type': enc_type,
            'admit_date': admit,
            'discharge_date': admit + timedelta(days=los) if enc_type == 'inpatient' else admit,
            'primary_dx_code': random.choice(['E11.9','I10','J44.1','N18.3','Z79.899']),
            'los_days': round(los, 1) if enc_type == 'inpatient' else 0,
            'readmission_flag': random.random() < 0.12,
            'total_cost': round(random.uniform(500, 80000), 2),
        })

enc_df = pd.DataFrame(encounters)
enc_df.to_sql('encounters', engine, if_exists='append', index=False)
print(f"Inserted {len(enc_df)} encounters")

print("Generating vitals...")
vitals = []
for _, pat in patients_df.sample(3000).iterrows():
    for _ in range(random.randint(1, 5)):
        bmi = round(np.random.normal(27.5, 5), 1)
        vitals.append({
            'id': str(uuid.uuid4()),
            'patient_id': pat['id'],
            'recorded_at': fake.date_time_between(start_date='-1y', end_date='now'),
            'systolic_bp': int(np.random.normal(130, 20)),
            'diastolic_bp': int(np.random.normal(82, 12)),
            'heart_rate': int(np.random.normal(78, 15)),
            'oxygen_sat': round(np.random.normal(97.5, 1.5), 1),
            'weight_kg': round(np.random.normal(75, 18), 1),
            'bmi': max(15, min(50, bmi)),
        })

vit_df = pd.DataFrame(vitals)
vit_df.to_sql('vitals', engine, if_exists='append', index=False)
print(f"Inserted {len(vit_df)} vitals")

print("Seed data complete!")