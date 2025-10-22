import streamlit as st
import pdfplumber
import spacy
import random
import re

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

# --- Extract text from uploaded PDF ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# --- Generate simple AI questions using spaCy ---
def generate_questions(text, num_questions=5):
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents if len(sent.text.split()) > 6]

    if not sentences:
        return ["No valid sentences found for question generation."]

    questions = []
    for _ in range(num_questions):
        sentence = random.choice(sentences)
        sent_doc = nlp(sentence)
        keywords = [token.text for token in sent_doc if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2]

        if keywords:
            keyword = random.choice(keywords)
            # Make a fill-in-the-blank type question
            question = sentence.replace(keyword, "_____")
            questions.append(f"Q: {question}\nA: {keyword}")
        else:
            # Wh-type question fallback
            questions.append(f"Q: What is the main idea of the following?\nA: {sentence}")

    return questions

# --- Streamlit App Layout ---
st.set_page_config(page_title="AI Question Generator", layout="centered")
st.title("🧠 AI Question Generator")
st.write("Upload a PDF file to automatically generate questions from its content.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)

    if text:
        st.success("Text successfully extracted!")
        st.subheader("📘 Extracted Text Preview:")
        st.text_area("Extracted Text", text[:1000] + "..." if len(text) > 1000 else text, height=200)

        num_questions = st.slider("Number of Questions", 3, 15, 5)

        if st.button("Generate Questions"):
            with st.spinner("Generating questions..."):
                questions = generate_questions(text, num_questions)
            st.success("Questions Generated Successfully!")
            for i, q in enumerate(questions, 1):
                st.markdown(f"**{i}.** {q}")
    else:
        st.error("Could not extract text from the uploaded PDF.")
else:
    st.info("Please upload a PDF file to begin.")
