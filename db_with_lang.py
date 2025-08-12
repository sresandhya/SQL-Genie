import os
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

st.set_page_config(page_title="SQL Genie", page_icon="🧞‍♂️")

# Load environment variables
load_dotenv()

# ---------------------- STYLING ----------------------
st.markdown(
    """
    <style>
    /* App background plain */
    [data-testid="stAppViewContainer"] {
        background-color: #1e1e1e;
    }

    /* Header with fixed height so image is not full-page */
    .header-section {
        background: 
            linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)),
            url('https://blog.nextideatech.com/wp-content/uploads/2023/09/LangSQL-1.png');
        background-size: cover;
        background-position: center;
        padding: 20px;
        height: 180px; /* Fixed height */
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-bottom: 2px solid rgba(255,255,255,0.2);
        margin-bottom: 40px; /* ✅ Added more space below image */
    }

    /* Title without white box */
    .title-text {
        font-size: 2rem;
        font-weight: bold;
        color: #ff4d88;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    /* Subtitle in black bold */
    .subtitle {
        text-align: center;
        font-size: 1.4rem;
        font-weight: bold;
        color: black;
        margin-top: 5px;
    }

    /* Input label styling - remove gap between label & box */
    .input-label {
        font-size: 1.2rem;
        font-weight: bold;
        color: white;
        margin-bottom: 0px; /* ✅ No space between label and textbox */
        display: block;
    }

    /* Section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: white;
    }

    /* Execute Query Button */
    div.stButton > button {
        background: linear-gradient(45deg, #ff3c78, #0078ff);
        color: white;
        font-weight: 700;
        padding: 12px 25px;
        font-size: 1.1rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 0 15px #ff3c78, 0 0 25px #0078ff;
        transition: background 0.4s ease;
        cursor: pointer;
        width: 100%;
        max-width: 220px;
        margin: 15px auto;
        display: block;
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #0078ff, #ff3c78);
        box-shadow: 0 0 30px #ff3c78, 0 0 40px #0078ff;
    }

    /* Query/Result box */
    .custom-box {
        background: rgba(0, 0, 50, 0.7);
        padding: 15px;
        border-radius: 12px;
        margin-top: 10px;
        font-family: monospace;
        font-size: 1rem;
        color: white;
        white-space: pre-wrap;
        border: 1px solid rgba(255,255,255,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------- DATABASE CONNECTION ----------------------
db_user = "root"
db_password = "1234"
db_host = "localhost"
db_name = "retails"

engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
db = SQLDatabase(engine, sample_rows_in_table_info=3)
llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.environ["GOOGLE_API_KEY"])
chain = create_sql_query_chain(llm, db)

# ---------------------- QUERY EXECUTION FUNCTION ----------------------
def execute_query(question):
    try:
        response = chain.invoke({"question": question})
        cleaned = response.strip().removeprefix("```sql").removesuffix("```").strip()
        result = db.run(cleaned)
        return cleaned, result
    except ProgrammingError as e:
        st.error(f"An error occurred: {e}")
        return None, None

# ---------------------- STREAMLIT UI ----------------------
st.markdown(
    "<div class='header-section'>"
    "<div class='title-text'>💡 AI SQL Assistant</div>"
    "<div class='subtitle'>Ask your database anything in plain English</div>"
    "</div>", 
    unsafe_allow_html=True
)

st.markdown("<label class='input-label'>Enter your question here:</label>", unsafe_allow_html=True)
question = st.text_input("", key="user_question")

if st.button("🚀 Execute Query"):
    if question:
        cleaned_query, query_result = execute_query(question)
        
        if cleaned_query and query_result is not None:
            st.markdown('<div class="section-header">📄 Generated SQL Query</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="custom-box">{cleaned_query}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header">📊 Query Results</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="custom-box">{query_result}</div>', unsafe_allow_html=True)
        else:
            st.write("No result returned due to an error.")
    else:
        st.write("Please enter a question.")
