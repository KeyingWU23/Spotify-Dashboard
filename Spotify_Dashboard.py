import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import requests
import tempfile

st.set_page_config(page_title='Spotify Dashboard', page_icon=':musical_note:')

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

        def sql_db_to_df(db_name,temp_file_path):
            import sqlite3
            cnx = sqlite3.connect(temp_file_path)
            df = pd.read_sql('select * from {}'.format(db_name), cnx)
            cnx.close()
            return df

        spotify_2023 = sql_db_to_df('spotify_data',temp_file_path1)
        spotify_2023['release_date'] = pd.to_datetime(spotify_2023['release_date']).dt.strftime('%Y-%m-%d')

        spotify_top_tracks = sql_db_to_df('spotify_top_tracks_by_artist',temp_file_path2)

        import os
        os.remove(temp_file_path1)
        os.remove(temp_file_path2)

        return spotify_2023, spotify_top_tracks
    except:
        st.error('Please Restart This Web App', icon="🚨")

spotify_2023,spotify_top_tracks = loading_data()

while spotify_2023.empty or spotify_top_tracks.empty:
    spotify_2023,spotify_top_tracks = loading_data()

st.title('Spotify Data Visualization')
st.sidebar.success('Select a page above')

option = option_menu(
    menu_title=None,
    options=['Top 10 Artists','Top 10 Songs','Audio Features'],
    icons=['person-up','music-note-list','speaker'],
    orientation='horizontal')

if option == 'Top 10 Artists':
    st.write('### Top 10 Artists Having Most Hits In 2023')
    artist_counts = spotify_2023['artist(s)_name'].value_counts()
    top_artists = pd.DataFrame(artist_counts.head(10)).reset_index()
    fig = plt.figure(figsize=(12, 6))
    sns.barplot(top_artists, x='artist(s)_name', y='count',
                hue='count', palette='tab20')
    plt.title('Top 10 Artists Having Most Hits In 2023')
    plt.xlabel('Artist')
    plt.ylabel('Number of Hits')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

    st.write('### Top Tracks of Top 10 Artists Having Most Hits In 2023')
    artist_list = spotify_top_tracks['Artist Name'].unique().tolist()
    selected_artist = st.selectbox("Select an Artist: ", artist_list)
    filtered_top_tracks_by_artist = spotify_top_tracks[spotify_top_tracks['Artist Name'] == selected_artist]
    st.dataframe(filtered_top_tracks_by_artist,hide_index=True,use_container_width=True)

if option == 'Top 10 Songs':
    st.write('### Top 10 Streamed Songs in 2023')
    top_songs = spotify_2023.sort_values(by='streams',ascending=False).head(10)
    fig = plt.figure(figsize=(12, 6))
    sns.barplot(top_songs, x='streams', y='track_name', hue='streams', palette='tab20')
    plt.title('Top 10 Streamed Songs in 2023')
    plt.xlabel('Streams')
    plt.ylabel('Song')
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig)

    platform = option_menu(
    menu_title=None,
    options=['Spotify','Apple'],
    icons=['spotify','apple'],
    orientation='horizontal')

    if platform == 'Spotify':
        st.write('##### Top 10 Songs on Spotify Based on Presence in Playlists/Charts')

        top_songs_spotify = spotify_2023[['track_name','artist(s)_name',
                                        'in_spotify_playlists','in_spotify_charts']].copy()
        top_songs_spotify['spotify_total'] = (top_songs_spotify['in_spotify_playlists']
                                            + top_songs_spotify['in_spotify_charts'])
        top_songs_spotify = top_songs_spotify.sort_values(by='spotify_total', ascending=False).head(10)
        top_songs_spotify = top_songs_spotify.reset_index(drop=True)

        fig = plt.figure(figsize=(12, 6))
        sns.barplot(top_songs_spotify, x='spotify_total', y='track_name', hue='spotify_total', palette='tab20')
        plt.title('Top 10 Songs on Spotify Based on Presence in Playlists/Charts')
        plt.xlabel('Total Presence')
        plt.ylabel('Track')
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig)

    if platform == 'Apple':
        st.write('##### Top 10 Songs on Apple Music Based on Presence in Playlists/Charts')

        top_songs_apple = spotify_2023[['track_name', 'artist(s)_name', 'in_apple_playlists', 'in_apple_charts']].copy()
        top_songs_apple['apple_total'] = (top_songs_apple['in_apple_playlists']
                                        + top_songs_apple['in_apple_charts'])
        top_songs_apple = top_songs_apple.sort_values(by='apple_total', ascending=False).head(10)
        top_songs_apple = top_songs_apple.reset_index(drop=True)

        fig = plt.figure(figsize=(12, 6))
        sns.barplot(top_songs_apple, x='apple_total', y='track_name', hue='apple_total', palette='tab20')
        plt.title('Top 10 Songs on Apple Music Based on Presence in Playlists/Charts')
        plt.xlabel('Total Presence')
        plt.ylabel('Track')
        plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
        plt.tight_layout()
        st.pyplot(fig)

if option == 'Audio Features':
    st.write('### Relationship Between All Audio Features')
    def correlation_heatmap(df):
        corr_df = df.corr()
        fig = px.imshow(corr_df, text_auto=".2f", aspect="auto", template='plotly_dark',
                        color_continuous_scale='geyser', height=600, width=1200)
        return fig
    fig_correlation = correlation_heatmap(spotify_2023[['danceability_%','valence_%', 'energy_%', 'acousticness_%',
                                                    'instrumentalness_%','liveness_%', 'speechiness_%']])
    st.plotly_chart(fig_correlation)

    st.write('### Audio Feature Radar of Top 10 Streamed Songs in 2023')
    top_songs = spotify_2023.sort_values(by='streams',ascending=False).head(10)
    top_songs = top_songs[['track_name','artist(s)_name','release_date']].copy()
    track_list = top_songs['track_name'].unique().tolist()
    selected_track = st.selectbox("Select a Song: ", track_list)
    filtered_top_track = top_songs[top_songs['track_name'] == selected_track]
    st.dataframe(filtered_top_track,hide_index=True)

    selected_track_audio_feature = spotify_2023[spotify_2023['track_name'] == selected_track]
    selected_track_audio_feature = selected_track_audio_feature[['danceability_%','valence_%', 'energy_%',
                                    'acousticness_%','instrumentalness_%','liveness_%', 'speechiness_%']]
    selected_track_audio_feature = selected_track_audio_feature.T.reset_index()
    selected_track_audio_feature.columns = ['Audio Feature','%']

    fig_radar_chart = px.line_polar(selected_track_audio_feature, r='%',
                                    theta='Audio Feature', line_close=True, template='plotly_dark', height=600,
                                    width=1200, markers=True,
                                    title=f'Audio Feature Radar of {selected_track}')
    st.plotly_chart(fig_radar_chart)

# Terminal:
# streamlit run Spotify_Dashboard.py