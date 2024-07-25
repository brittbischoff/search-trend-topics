import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
from pytrends.exceptions import TooManyRequestsError, ResponseError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize pytrends request
pytrends = TrendReq(hl='en-US', tz=360)

# Candidate names and their respective topic IDs
candidates = {
    "Kamala Harris": "/m/08sry2",
    "Robert F Kennedy Jr": "/m/02l5km",
    "Robert F. Kennedy Jr. 2024 presidential campaign": "/g/11ssfhnzyz",
    "Donald Trump": "/m/0cqt90",
    "Donald Trump 2024 presidential campaign": "/g/11sbx7l5r8",
    "J. D. Vance": "/g/11c6v_wj1r",
    "Joe Biden": "/m/012gx2",
    "Joe Biden presidential campaign, 2024": "/g/11t6vtlz6y",
    "Presidency of Joe Biden": "/g/11qnb9gr97"
}

# List of US states
us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", 
             "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
             "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

# Function to fetch Google Trends data and related queries with rate limiting
def get_trends_data(topic_ids, geo='US', timeframe='today 12-m', gprop=''):
    pytrends.build_payload(topic_ids, cat=0, timeframe=timeframe, geo=geo, gprop=gprop)
    
    # Retry logic for handling TooManyRequestsError
    attempts = 0
    while attempts < 5:
        try:
            data = pytrends.interest_over_time()
            related_queries = pytrends.related_queries()
            if not data.empty:
                data = data.drop(labels=['isPartial'], axis='columns')
            return data, related_queries
        except TooManyRequestsError:
            attempts += 1
            st.warning("Rate limit reached, retrying...")
            time.sleep(60)  # Wait for 60 seconds before retrying
        except ResponseError as e:
            logger.error(f"ResponseError: {e}")
            st.error("Failed to fetch data due to a response error.")
            return pd.DataFrame(), {}
    st.error("Failed to fetch data after several attempts due to rate limiting.")
    return pd.DataFrame(), {}

# Function to create a word cloud from query data
def create_wordcloud(query_data):
    if query_data is not None and not query_data.empty:
        query_text = ' '.join(query_data['query'].tolist())
        wordcloud = WordCloud(width=800, height=400, max_words=25, background_color='white').generate(query_text)
        return wordcloud
    return None

# Function to display rising queries
def display_rising_queries(rising_queries, timeframe):
    if rising_queries is not None and not rising_queries.empty:
        rising_queries.reset_index(inplace=True)
        st.subheader(f"Rising Queries - Last 7 Days ({timeframe})")
        st.write("Queries with the biggest increase in search frequency since the last time period. Results marked 'Breakout' had a tremendous increase, probably because these queries are new and had few (if any) prior searches.")
        st.dataframe(rising_queries)

# Streamlit app layout
st.title("Search Trend Report Automation - 2024 Presidential Candidates")

# Candidate selection
selected_candidates = st.multiselect("Select the candidates to analyze", list(candidates.keys()))

# User inputs for trend analysis
region = st.selectbox("Select the region", ["US"] + us_states, index=0)
timeframe = st.selectbox("Select the timeframe", ["now 7-d", "today 1-m", "today 3-m", "today 12-m", "all"])
gprop = st.selectbox("Select the property", ["", "news", "images", "youtube", "froogle"])

if st.button("Fetch Trends"):
    if selected_candidates:
        topic_ids = [candidates[candidate] for candidate in selected_candidates]
        with st.spinner("Fetching data..."):
            data, related_queries = get_trends_data(topic_ids, region, timeframe, gprop)
            if not data.empty:
                st.success("Data fetched successfully!")
                
                # Plot the trend data
                st.line_chart(data)
                
                # Display the data in a table
                st.dataframe(data)
                
                # Display rising queries for each topic
                for topic_id in topic_ids:
                    rising_queries = related_queries[topic_id]['rising']
                    display_rising_queries(rising_queries, timeframe)
                    
                    # Create and display word cloud for rising queries
                    wordcloud = create_wordcloud(rising_queries)
                    if wordcloud:
                        st.image(wordcloud.to_array(), use_column_width=True)
            else:
                st.error("No data found for the given parameters.")
    else:
        st.error("No candidates selected.")

# Additional functionalities (Placeholders for further development)
