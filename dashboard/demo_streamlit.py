import streamlit as st
import pandas as pd
import plotly.express as px

# Source : https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148/4
# run with : streamlit run Dashboard/demo_streamlit.py

def load_data():
    return pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv")

# Load data
df = load_data()

# Display some information
st.title("Air Travel Time Series Plot")
st.write("This chart shows the number of air passenger traveled in each month from 1949 to 1960")

# Plotly figure
fig = px.line(df, x="Month", y=df.columns[1:], title="Air Passenger Travel")
st.plotly_chart(fig)