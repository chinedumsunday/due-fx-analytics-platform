from faker import Faker
import random
import json 
from dotenv import load_dotenv
import os
import psycopg2
load_dotenv()

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


rows= [("NGN_USD", "NGN", "USD", "Nigeria to USA", True), ("NGN_GBP", "NGN", "GBP", "Nigeria to UK", True), ("NGN_EUR", "NGN", "EUR", "Nigeria to Europe", True), ("NGN_JPY", "NGN", "JPY", "Nigeria to Japan", True)]

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

def main():
    conn = connect()
    truncate = "TRUNCATE TABLE corridors, users RESTART IDENTITY CASCADE" 
    with conn.cursor() as cursor:
        cursor.execute(truncate)
    seed_corridors(conn)
    seed_users(conn, 1000)
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