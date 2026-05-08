import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:postgres@127.0.0.1:5432/healthcare_db')

# Pull encounter data with patient age
df = pd.read_sql(text("""
    SELECT e.id, e.patient_id,
           EXTRACT(YEAR FROM AGE(p.date_of_birth))::INTEGER AS age,
           e.los_days, e.encounter_type,
           p.insurance_type
    FROM encounters e
    JOIN patients p ON e.patient_id = p.id
    WHERE e.encounter_type = 'inpatient'
"""), engine)

print(f"Inpatient encounters: {len(df)}")

# Create realistic readmission probability based on risk factors
np.random.seed(42)
prob = 0.05  # base rate
prob = prob + (df['age'] > 65) * 0.10
prob = prob + (df['los_days'] > 5) * 0.10
prob = prob + (df['insurance_type'].isin(['Medicaid','Uninsured'])) * 0.08
prob = np.clip(prob, 0.02, 0.40)

df['readmission_flag'] = np.random.binomial(1, prob)
print(f"Readmission rate: {df.readmission_flag.mean()*100:.1f}%")

# Update database
with engine.begin() as conn:
    for _, row in df.iterrows():
        conn.execute(
            text("UPDATE encounters SET readmission_flag = :flag WHERE id = :id"),
            {'flag': bool(row['readmission_flag']), 'id': str(row['id'])}
        )

print("Done updating readmission flags.")