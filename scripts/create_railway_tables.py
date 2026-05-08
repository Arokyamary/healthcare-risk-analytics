from sqlalchemy import create_engine, text

DB = "postgresql://postgres:uykweXXcynlmeYaXItiNbmbGcWxDlLMg@turntable.proxy.rlwy.net:19990/railway"
engine = create_engine(DB)

tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS encounters (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        patient_id UUID NOT NULL REFERENCES patients(id),
        encounter_type VARCHAR(50) NOT NULL,
        admit_date TIMESTAMPTZ NOT NULL,
        discharge_date TIMESTAMPTZ,
        primary_dx_code VARCHAR(20),
        los_days NUMERIC(5,1),
        discharge_dispo VARCHAR(50),
        readmission_flag BOOLEAN DEFAULT FALSE,
        total_cost NUMERIC(12,2),
        created_at TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS vitals (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        patient_id UUID NOT NULL REFERENCES patients(id),
        encounter_id UUID REFERENCES encounters(id),
        recorded_at TIMESTAMPTZ NOT NULL,
        systolic_bp SMALLINT,
        diastolic_bp SMALLINT,
        heart_rate SMALLINT,
        respiratory_rate SMALLINT,
        temperature_f NUMERIC(5,2),
        oxygen_sat NUMERIC(5,2),
        weight_kg NUMERIC(6,2),
        height_cm NUMERIC(5,1),
        bmi NUMERIC(5,2),
        pain_score SMALLINT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS diagnoses (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        patient_id UUID NOT NULL REFERENCES patients(id),
        encounter_id UUID REFERENCES encounters(id),
        icd10_code VARCHAR(10) NOT NULL,
        description TEXT,
        chronic_flag BOOLEAN DEFAULT FALSE,
        onset_date DATE,
        recorded_at TIMESTAMPTZ DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lab_results (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        patient_id UUID NOT NULL REFERENCES patients(id),
        encounter_id UUID REFERENCES encounters(id),
        test_name VARCHAR(200) NOT NULL,
        loinc_code VARCHAR(20),
        result_value NUMERIC(12,4),
        unit VARCHAR(50),
        reference_low NUMERIC(12,4),
        reference_high NUMERIC(12,4),
        abnormal_flag VARCHAR(5),
        collected_at TIMESTAMPTZ NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS medications (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        patient_id UUID NOT NULL REFERENCES patients(id),
        encounter_id UUID REFERENCES encounters(id),
        drug_name VARCHAR(200) NOT NULL,
        rxnorm_code VARCHAR(20),
        dose VARCHAR(50),
        route VARCHAR(50),
        frequency VARCHAR(50),
        start_date DATE,
        end_date DATE,
        status VARCHAR(20) DEFAULT 'active'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS patient_features (
        patient_id TEXT,
        age_years INTEGER,
        gender VARCHAR(10),
        insurance_medicaid INTEGER,
        insurance_uninsured INTEGER,
        insurance_type VARCHAR(50),
        num_admissions_12m INTEGER,
        num_ed_visits_6m INTEGER,
        avg_los_12m NUMERIC,
        max_los NUMERIC,
        total_inpatient INTEGER,
        readmission_30d INTEGER,
        days_since_last_visit INTEGER,
        num_diagnoses INTEGER,
        num_chronic_dx INTEGER,
        has_diabetes INTEGER,
        has_hypertension INTEGER,
        has_copd INTEGER,
        last_systolic_bp NUMERIC,
        last_bmi NUMERIC,
        last_spo2 NUMERIC,
        num_medications INTEGER
    )
    """
]

with engine.connect() as conn:
    for sql in tables_sql:
        conn.execute(text(sql))
    conn.commit()

print("All tables created on Railway!")