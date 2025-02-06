import requests
import sqlite3
import streamlit as st
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

#-----------------------------------------------------------------------------------------------------
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS post
               (user_id INTEGER,
               post_id INTEGER,
               title TEXT,
               body TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS khabar
               (title TEXT,
               body TEXT)''')
conn.commit()

#-----------------------------------------------------------------------------------------------------

def json_api():
    
    temp_conn = sqlite3.connect('example.db')
    temp_cursor = temp_conn.cursor()

    for user_id in range(1, 11):
        response = requests.get(f"https://jsonplaceholder.typicode.com/posts?userId={user_id}")
        if response.status_code == 200:

            data = response.json()
            for post in data:
                post_id = post['id']
                title = post['title']
                body = post['body']
                temp_cursor.execute('''INSERT INTO post
                                    (user_id, post_id, title, body) VALUES (?, ?, ?, ?)''', 
                                    (user_id, post_id, title, body))
    temp_conn.commit()
    temp_conn.close()

#-----------------------------------------------------------------------------------------------------

def digiato():
    response = requests.get("https://digiato.com/")
    soup = BeautifulSoup(response.text, 'html.parser')
    news_items = soup.find_all("div", class_="rowCard homeTodayItem")

    temp_conn = sqlite3.connect('example.db')
    temp_cursor = temp_conn.cursor()

    for item in news_items:
        title = item.find("a", class_="rowCard__title").text.strip()
        body = item.find("p", class_="rowCard__description").text.strip()
        temp_cursor.execute('''INSERT INTO khabar
                            (title, body) VALUES (?, ?)''', (title, body))

    temp_conn.commit()
    temp_conn.close()

#-----------------------------------------------------------------------------------------------------

executor = ThreadPoolExecutor(max_workers=2)
executor.submit(json_api)
executor.submit(digiato)


st.title("EXAM FINAL RESULT")

st.header("-------------------Khabar-------------------")
cursor.execute("SELECT * FROM khabar")
news_data = cursor.fetchall()
for row in news_data:
    title, body = row
    st.subheader(title)
    st.write(body)

st.header("-------------------Posts-------------------")
conn = sqlite3.connect('example.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM post")
posts_data = cursor.fetchall()
for row in posts_data:
    user_id, post_id, title, body = row
    st.write(f"user-Id: {user_id}")
    st.write(f"Post-Id: {post_id}")
    st.write(f"Title: {title}")
    st.write(f"Body: {body}")

conn.close()