from faker import Faker
import random
import json 
from dotenv import load_dotenv
import os
import psycopg2
load_dotenv()
from datetime import datetime, timedelta

POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB=os.getenv("POSTGRES_DB")
host=os.getenv("host")
port=os.getenv("port")

def connect():
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    conn.autocommit = True
    return conn


rows= [("NGN_USD", "NGN", "USD", "Nigeria to USA", True), ("NGN_GBP", "NGN", "GBP", "Nigeria to UK", True), ("NGN_EUR", "NGN", "EUR", "Nigeria to Europe", True), ("NGN_CAD", "NGN", "CAD", "Nigeria to Canada", True)]
BASE_RATES = {"USD": 1400, "GBP": 1800, "EUR": 1600, "CAD": 1100}

def seed_corridors(conn):
    with conn.cursor() as cursor:
        sql = "INSERT INTO corridors (corridor_code, source_currency, target_currency, corridor_name, is_active) VALUES (%s, %s, %s, %s, %s)"
        for row in rows:
            cursor.execute(sql, row)
    conn.commit()

def seed_users(conn, n):
    fake = Faker()
    with conn.cursor() as cursor:
        for i in range(n):
            tier = random.choices(["standard", "premium"], weights=[0.8, 0.2])[0]
            country = fake.country()
            signup_date = fake.date_between(start_date='-18m', end_date='today')
            sql = "INSERT INTO users (tier, country, signup_date) VALUES (%s, %s, %s)"
            cursor.execute(sql, (tier, country, signup_date))
    conn.commit()

def seed_transactions(conn, n=100):
    transactions = []
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()
        users = [user[0] for user in users]
        cursor.execute("SELECT corridor_code, target_currency FROM corridors")
        corridors = cursor.fetchall()
        for i in range(n):
            user_id = random.choice(users)
            corridor_code, target_currency = random.choice(corridors)
            amount_ngn = round(random.uniform(50000, 5000000), 2)
            fx_rate_applied = round(BASE_RATES[target_currency] * random.uniform(0.98, 1.02), 6)
            amount_target_currency = round (amount_ngn / fx_rate_applied, 2)
            fee_amount_ngn = round(amount_ngn * 0.01, 2)
            status = random.choices(["initiated", "processing", "completed", "failed"], weights=[0.03, 0.04, 0.9, 0.03])[0]
            created_at = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            if status in ("completed", "failed"):
                updated_at = created_at + timedelta(minutes=random.randint(1, 30))
            else:
                updated_at = created_at
            transactions.append((user_id, corridor_code, amount_ngn, amount_target_currency, fx_rate_applied, fee_amount_ngn, status, created_at, updated_at))
        sql = "INSERT INTO transactions (user_id, corridor_code, amount_ngn, amount_target_currency, fx_rate_applied, fee_amount_ngn, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(sql, transactions)

def main():
    conn = connect()
    truncate = "TRUNCATE TABLE corridors, users RESTART IDENTITY CASCADE" 
    with conn.cursor() as cursor:
        cursor.execute(truncate)
    seed_corridors(conn)
    seed_users(conn, 1000)
    seed_transactions(conn, 100)
    conn.close()    

def check_tables():
    conn = connect()
    with conn.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM corridors")
        corridors = cursor.fetchall()
        print("Corridors:")
        for corridor in corridors:
            print(corridor)
        
        cursor.execute("SELECT count(*) FROM users")
        users = cursor.fetchall()
        print("\nUsers:")
        for user in users:
            print(user)
    conn.close()

if __name__ == "__main__":
    main()
    check_tables()