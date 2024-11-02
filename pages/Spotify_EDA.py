import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import io
import requests
import tempfile

st.set_page_config(page_title='Spotify EDA', page_icon=':musical_note:')

@st.cache_data
def loading_data():

    try:
        url_spotify_data = "https://raw.githubusercontent.com/KeyingWU23/Spotify-Dashboard/main/spotify_sql_db/spotify_data.sqlite"
        response_spotify_data = requests.get(url_spotify_data)

        url_spotify_top_tracks_by_artist = "https://raw.githubusercontent.com/KeyingWU23/Spotify-Dashboard/main/spotify_sql_db/spotify_top_tracks_by_artist.sqlite"
        response_spotify_top_tracks_by_artist = requests.get(url_spotify_top_tracks_by_artist)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file1:
            temp_file1.write(response_spotify_data.content)
            temp_file_path1 = temp_file1.name

        with tempfile.NamedTemporaryFile(delete=False) as temp_file2:
            temp_file2.write(response_spotify_top_tracks_by_artist.content)
            temp_file_path2 = temp_file2.name

        def sql_db_to_df(db_name, temp_file_path):
            import sqlite3
            cnx = sqlite3.connect(temp_file_path)
            df = pd.read_sql('select * from {}'.format(db_name), cnx)
            cnx.close()
            return df

        spotify_2023 = sql_db_to_df('spotify_data', temp_file_path1)
        spotify_2023['release_date'] = pd.to_datetime(spotify_2023['release_date']).dt.strftime('%Y-%m-%d')

        spotify_top_tracks = sql_db_to_df('spotify_top_tracks_by_artist', temp_file_path2)

        import os
        os.remove(temp_file_path1)
        os.remove(temp_file_path2)

        return spotify_2023, spotify_top_tracks
    except:
        st.error('Please Restart This Web App', icon="🚨")

spotify_2023,spotify_top_tracks = loading_data()

while spotify_2023.empty or spotify_top_tracks.empty:
    spotify_2023,spotify_top_tracks = loading_data()

st.title('Spotify Exploratory Data Analysis')
st.sidebar.success('Select a page above')

selected = option_menu(
    menu_title=None,
    options=['Datasets','Statistics','Distributions'],
    icons=['database','clipboard-data','graph-up-arrow'],
    orientation='horizontal')

if selected == 'Datasets':
    st.write('## Quick View of All Datasets')

    column_descriptions = {
        'track_name': 'Name of the song',
        'artist(s)_name': 'Name of the artist(s) of the song',
        'artist_count': 'Number of artists contributing to the song',
        'in_spotify_playlists': 'Number of Spotify playlists the song is included in',
        'in_spotify_charts': 'Presence and rank of the song on Spotify charts',
        'streams': 'Total number of streams on Spotify',
        'in_apple_playlists': 'Number of Apple Music playlists the song is included in',
        'in_apple_charts': 'Presence and rank of the song on Apple Music charts',
        'in_deezer_playlists': 'Number of Deezer playlists the song is included in',
        'in_deezer_charts': 'Presence and rank of the song on Deezer charts',
        'danceability_%': 'Percentage indicating how suitable the song is for dancing',
        'valence_%': 'Positivity of the song\'s musical content',
        'energy_%': 'Perceived energy level of the song',
        'acousticness_%': 'Amount of acoustic sound in the song',
        'instrumentalness_%': 'Amount of instrumental content in the song',
        'liveness_%': 'Presence of live performance elements',
        'speechiness_%': 'Amount of spoken words in the song',
        'released_date': 'Exact date when the song was released'
    }

    st.write("### Spotify Data for 2023")
    st.dataframe(spotify_2023,hide_index=True)

    st.write("### Information about Spotify Data for 2023")
    buffer = io.StringIO()
    spotify_2023.info(buf=buffer)
    info_str = buffer.getvalue()
    st.text(info_str)

    st.write("### Column Descriptions")
    for column, description in column_descriptions.items():
        st.write(f"**{column}**: {description}")
    st.write("### Top Tracks of Top 10 Artists Having Most Hits In 2023")
    artist_list = spotify_top_tracks['Artist Name'].unique().tolist()
    selected_artist = st.multiselect("Artist Name: ", artist_list, default=artist_list)
    filtered_top_tracks_by_artist = spotify_top_tracks[spotify_top_tracks['Artist Name'].isin(selected_artist)]
    st.dataframe(filtered_top_tracks_by_artist,hide_index=True,use_container_width=True)

if selected == 'Statistics':
    st.write('## Some Basic Statistics')

    st.write("### Numeric Variable Summary")
    numeric_columns = spotify_2023.select_dtypes(include=['number']).columns.to_list()
    numeric_summary = spotify_2023[numeric_columns].describe()
    st.dataframe(numeric_summary)

    st.write("### Non-Numeric Variable Summary")
    non_numeric_columns = spotify_2023.select_dtypes(exclude=['number']).columns.to_list()
    non_numeric_summary = spotify_2023[non_numeric_columns].describe()
    non_numeric_summary = non_numeric_summary.astype(str)
    st.dataframe(non_numeric_summary)

if selected == 'Distributions':
    st.write('## Distribution of Percentage Features')
    percentage_features_to_visualize = ['danceability_%', 'energy_%', 'valence_%', 'acousticness_%',
                                        'instrumentalness_%', 'liveness_%', 'speechiness_%']
    fig, axes = plt.subplots(nrows=len(percentage_features_to_visualize), figsize=(12, 15))
    for i, feature in enumerate(percentage_features_to_visualize):
        sns.histplot(spotify_2023[feature], ax=axes[i], bins=30, kde=True)
        axes[i].set_title(f'Distribution of {feature}', fontsize=14)
        axes[i].set_xlabel(feature)
        axes[i].set_ylabel('Frequency')
    plt.tight_layout()
    st.pyplot(fig)
