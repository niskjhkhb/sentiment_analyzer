import streamlit as st
from transformers import pipeline
import sqlite3



#App title 
st.title("AI-powered Sentiment Analyzer")

#load model (it only loads once cause its cached)
model_name="distilbert-base-uncased-finetuned-sst-2-english"
model_task="sentiment-analysis"
@st.cache_resource
def load_model():
    return pipeline(model_task, model=model_name)

model= load_model()

#connect to the database

conn = sqlite3.connect('sentiment.db')
c = conn.cursor()

# Create a table to store the results 
 
c.execute('''CREATE TABLE IF NOT EXISTS sentiments
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             text TEXT,
             sentiment TEXT,
             score REAL)
           ''')

conn.commit()

#text input 
user_input= st.text_area("Enter your text here:")

#analyze button

if st.button("Analyze"):
    if user_input:
        result = model(user_input)[0]
        label = result['label']
        score = round(result['score'],3)

        #display result
        st.markdown(f"### Sentiment: **{label}**")
        st.markdown(f"### Score: **{score}**")

        c.execute("INSERT INTO sentiments (text, sentiment, score) VALUES (?, ?, ?)",
                  (user_input, label, score))
        conn.commit()

    else:
        st.warning("Please enter some text to analyze.")
    

if st.button("Show History"):
    c.execute("SELECT * FROM sentiments")
    data = c.fetchall()
    if data:
        st.write("### Analysis History")
        for row in data:
            st.write(f"**Text:** {row[1]}")
            st.write(f"**Sentiment:** {row[2]}")
            st.write(f"**Score:** {row[3]}")
            st.write("---")
    else:
        st.warning("No analysis history found.")

if st.button("Clear History"):
    c.execute("DELETE FROM sentiments")
    conn.commit()
    st.success("History cleared.")


#close connection 
conn.close()


