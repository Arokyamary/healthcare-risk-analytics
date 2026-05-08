import psycopg2
for pwd in ['postgres','admin123','1234','password','root']:
    try:
        conn = psycopg2.connect(host='127.0.0.1',port=5432,user='postgres',password=pwd,dbname='healthcare_db')
        print('PASSWORD IS:', pwd)
        conn.close()
        break
    except:
        print('Wrong:', pwd)
