from sqlalchemy import create_engine, text

DB = "postgresql://postgres:uykweXXcynlmeYaXItiNbmbGcWxDlLMg@turntable.proxy.rlwy.net:19990/railway"
engine = create_engine(DB)

with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"
    ))
    tables = [row[0] for row in result]
    print("Tables on Railway:")
    for t in tables:
        print(f"  - {t}")