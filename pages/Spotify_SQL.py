import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import requests
import tempfile

st.set_page_config(page_title='Spotify SQL', page_icon=':musical_note:')

@st.cache_data
def get_df_using_sql_query(sql_query):

    try:
        url_spotify_data = "https://raw.githubusercontent.com/KeyingWU23/Spotify-Dashboard/main/spotify_sql_db/spotify_data.sqlite"
        response_spotify_data = requests.get(url_spotify_data)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response_spotify_data.content)
            temp_file_path = temp_file.name

        import sqlite3
        cnx = sqlite3.connect(temp_file_path)
        df = pd.read_sql(sql_query,cnx)
        cnx.close()

        import os
        os.remove(temp_file_path)

        return df
    except:
        st.error('Please Restart This Web App', icon="🚨")

st.title('SQL Project: Spotify Songs 2023')
st.sidebar.success('Select a page above')

question = option_menu(
    menu_title=None,
    options=['Question1','Question2','Question3'],
    icons=['filetype-sql']*3,
    orientation='horizontal')

if question == 'Question1':
    st.write('###### What are all the top 5 songs with multiple artists?')
    sql_query_1 = '''
        SELECT track_name, "artist(s)_name", artist_count, streams
        FROM spotify_data
        WHERE artist_count > 1
        ORDER BY streams DESC
        LIMIT 5;
        '''
    st.code(sql_query_1,language='SQL')
    df1 = get_df_using_sql_query(sql_query=sql_query_1)
    while df1.empty:
        df1 = get_df_using_sql_query(sql_query=sql_query_1)
    df1.index = df1.index + 1
    st.write('Answer: ')
    st.dataframe(df1,use_container_width=True)

if question == 'Question2':
    st.write('###### What are the top 5 songs that have the word "Love" in the track name?')
    sql_query_2 = '''
        SELECT track_name, "artist(s)_name"
        FROM spotify_data
        WHERE track_name LIKE '%love%'
        ORDER BY streams DESC
        LIMIT 5;
        '''
    st.code(sql_query_2,language='SQL')
    df2 = get_df_using_sql_query(sql_query=sql_query_2)
    while df2.empty:
        df2 = get_df_using_sql_query(sql_query=sql_query_2)
    df2.index = df2.index + 1
    st.write('Answer: ')
    st.dataframe(df2)

if question == 'Question3':
    st.write('###### Which artist has the most songs released in 2023 that are in the top spotify charts?')
    sql_query_3 = ''' 
        SELECT "artist(s)_name", COUNT(*) AS song_count
        FROM spotify_data
        WHERE release_date BETWEEN '2023-01-01' AND '2024-01-01'
        GROUP BY "artist(s)_name"
        ORDER BY song_count DESC
        LIMIT 3;
        '''
    st.code(sql_query_3,language='SQL')
    df3 = get_df_using_sql_query(sql_query=sql_query_3)
    while df3.empty:
        df3 = get_df_using_sql_query(sql_query=sql_query_3)
    df3.index = df3.index + 1
    answer = df3.loc[1,'artist(s)_name']
    st.dataframe(df3)
    st.write(f'Answer:{answer}')
    st.write('''Despite Taylor Swift's tour generating enough revenue to boost the American economy, 
        it was not enough to take the top spot from Morgan Wallen for most top songs released in 2023 (8 total songs!)
    ''')
