import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:postgres@127.0.0.1:5432/healthcare_db"
engine = create_engine(DB_URL)

print("Building feature table...")

# STEP 1: Base patient info
sql_patients = text("""
    SELECT p.id AS patient_id,
    EXTRACT(YEAR FROM AGE(p.date_of_birth))::INTEGER AS age_years,
    p.gender,
    CASE p.insurance_type WHEN 'Medicaid' THEN 1 ELSE 0 END AS insurance_medicaid,
    CASE p.insurance_type WHEN 'Uninsured' THEN 1 ELSE 0 END AS insurance_uninsured,
    p.insurance_type
    FROM patients p WHERE p.is_active = TRUE
""")
df = pd.read_sql(sql_patients, engine)
print(f"Base patients: {len(df)}")

# STEP 2: Encounter features + target from inpatient readmission
sql_enc = text("""
    SELECT patient_id,
    COUNT(*) FILTER (WHERE encounter_type='inpatient'
        AND admit_date >= NOW() - INTERVAL '365 days') AS num_admissions_12m,
    COUNT(*) FILTER (WHERE encounter_type='emergency'
        AND admit_date >= NOW() - INTERVAL '180 days') AS num_ed_visits_6m,
    AVG(los_days) FILTER (WHERE encounter_type='inpatient') AS avg_los_12m,
    MAX(los_days) FILTER (WHERE encounter_type='inpatient') AS max_los,
    COUNT(*) FILTER (WHERE encounter_type='inpatient') AS total_inpatient,
    MAX(CASE WHEN readmission_flag AND encounter_type='inpatient'
        THEN 1 ELSE 0 END) AS readmission_30d,
    EXTRACT(DAY FROM (NOW() - MAX(admit_date)))::INTEGER AS days_since_last_visit
    FROM encounters GROUP BY patient_id
""")
enc_df = pd.read_sql(sql_enc, engine)
df = df.merge(enc_df, on='patient_id', how='left')

# STEP 3: Diagnosis features
sql_dx = text("""
    SELECT patient_id, COUNT(*) AS num_diagnoses,
    COUNT(*) FILTER (WHERE chronic_flag) AS num_chronic_dx,
    MAX(CASE WHEN icd10_code LIKE 'E11%' THEN 1 ELSE 0 END) AS has_diabetes,
    MAX(CASE WHEN icd10_code LIKE 'I10%' THEN 1 ELSE 0 END) AS has_hypertension,
    MAX(CASE WHEN icd10_code LIKE 'J44%' THEN 1 ELSE 0 END) AS has_copd
    FROM diagnoses GROUP BY patient_id
""")
dx_df = pd.read_sql(sql_dx, engine)
df = df.merge(dx_df, on='patient_id', how='left')

# STEP 4: Latest vitals
sql_vitals = text("""
    SELECT DISTINCT ON (patient_id) patient_id,
    systolic_bp AS last_systolic_bp, bmi AS last_bmi, oxygen_sat AS last_spo2
    FROM vitals ORDER BY patient_id, recorded_at DESC
""")
vit_df = pd.read_sql(sql_vitals, engine)
df = df.merge(vit_df, on='patient_id', how='left')

# STEP 5: Medication count
sql_meds = text("""
    SELECT patient_id, COUNT(*) AS num_medications
    FROM medications WHERE status = 'active' GROUP BY patient_id
""")
med_df = pd.read_sql(sql_meds, engine)
df = df.merge(med_df, on='patient_id', how='left')

# STEP 6: Fill missing values
fill_zeros = ['num_admissions_12m','num_ed_visits_6m','num_diagnoses',
              'num_chronic_dx','num_medications','readmission_30d',
              'has_diabetes','has_hypertension','has_copd',
              'total_inpatient']
for col in fill_zeros:
    df[col] = df[col].fillna(0).astype(int)

fill_medians = ['avg_los_12m','max_los','last_systolic_bp','last_bmi',
                'last_spo2','days_since_last_visit']
for col in fill_medians:
    df[col] = df[col].fillna(df[col].median())

# STEP 7: Save
df['patient_id'] = df['patient_id'].astype(str)
df.to_sql('patient_features', engine, if_exists='replace', index=False)
df.to_parquet('ml_pipeline/features_train.parquet', index=False)
print(f"Feature table saved: {len(df)} patients x {len(df.columns)} features")
print(f"Default rate: {df.readmission_30d.mean()*100:.1f}%")
print("Columns:", df.columns.tolist())