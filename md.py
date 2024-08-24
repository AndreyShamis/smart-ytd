#/bin/python

#!pip install fuzzywuzzy
#!pip install youtube-search-python
#!pip install yt-dlp
import requests
from bs4 import BeautifulSoup
import urllib.parse
from fuzzywuzzy import fuzz
from youtubesearchpython import VideosSearch
import yt_dlp
import librosa
import time, os
from music_file import MusicFile


def search_youtube(query):
    videos_search = VideosSearch(query, limit=10)
    results = videos_search.result()['result']
    
    # Extracting relevant information including the view count
    video_info = [
        {
            'title': video['title'],
            'link': video['link'],
            'viewCount': int(video['viewCount'].get('text', '0').replace(' views', '').replace(',', '').replace('No', '0'))
        }
        for video in results
    ]
    
    # Sorting the videos by view count in descending order
    sorted_videos = sorted(video_info, key=lambda x: x['viewCount'], reverse=True)
    
    # Returning the title and link of the sorted videos
    return [(video['title'], video['link'], video['viewCount']) for video in sorted_videos]



def calculate_similarity(query, title):
    ratio = fuzz.partial_ratio(query.lower(), title.lower())

    bonus = 0
    if "official" in title.lower():
        bonus += 10
    if "music video" in title.lower():
        bonus += 5
    if "lyric" in title.lower():
        bonus += 3
    if "1hour" in title.lower():
        bonus -= 20
    if "1 hour" in title.lower():
        bonus -= 20
    return ratio + bonus


def choose_best_result(results, query):
    if not results:
        return None

    sorted_results = sorted(results, key=lambda x: calculate_similarity(query, x[0]), reverse=True)
    best_score = calculate_similarity(query, sorted_results[0][0])

    if best_score >= 60:  # Приемлемое соответствие
        return sorted_results[0][1]
    else:
        return None  # Ничего подходящего не найдено

def find_best_youtube_match(query):
    results = search_youtube(query)
    print(f"Results for '{query}': {results}")
    return [results, choose_best_result(results, query)]


def get_top_10_songs():
    url = "https://www.billboard.com/charts/hot-100/"
    #url = "https://www.billboard.com/charts/billboard-global-200/"
    # Send a GET request to the URL
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all song items
    song_items = soup.select('ul.o-chart-results-list-row')

    top_songs = []
    for item in song_items:  # Limit to top 10
        rank = item.select_one('span.c-label.a-font-primary-bold-l').text.strip()
        title = item.select_one('h3#title-of-a-story').text.strip()
        artist = item.select_one('span.c-label.a-no-trucate').text.strip()

        top_songs.append({
            "rank": rank,
            "title": title,
            "artist": artist
        })

    return top_songs


def get_top_songs_youtube(country:str = 'us'):
    url = f"https://charts.youtube.com/charts/TrendingVideos/{country}/RightNow"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Assuming the structure of the site to find the necessary elements
    video_items = soup.find_all('div', class_='chart-table-container', limit=10)
    
    top_songs = []
    for item in video_items:
        title_element = item.find('yt-formatted-string', {'id': 'video-title'})
        artist_element = item.find('yt-formatted-string', {'id': 'byline'})
        link_element = item.find('a', {'id': 'thumbnail'})
        
        title = title_element.text.strip() if title_element else "No title found"
        artist = artist_element.text.strip() if artist_element else "No artist found"
        link = f"https://www.youtube.com{link_element['href']}" if link_element else "No link found"

        top_songs.append({
            "title": title,
            "artist": artist,
            "link": link
        })

    return top_songs

def get_youtube_search_url(track):
    base_url = "https://www.youtube.com/results"
    params = {"search_query": track}
    response = requests.get(base_url, params=params)
    return response.url


def download_audio(url, output_path='./downloads/'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(result).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return os.path.abspath(file_path)
        except Exception as e:
            print(f"Произошла ошибка при скачивании: {str(e)}")
            return None

def get_bpm(file_path):
    # Load the audio file
    y, sr = librosa.load(file_path)

    # Use the tempo function from librosa
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    return tempo


# Main execution
if __name__ == "__main__":
    top_10_songs = get_top_songs_youtube() 
    #get_top_10_songs()

    if top_10_songs:
        print("Top 10 Songs on Billboard Hot 100:")
        for song in top_10_songs:
            print(f"{song['rank']}. {song['title']} by {song['artist']}")
            query = f"{song['artist']} {song['title']}"
            urls , best_url = find_best_youtube_match(query)
            # if urls[0][1] != best_url:
            #     print(f"!!!!!!!!!!Best match: {best_url} != {urls[0]}")
            #     print(f"Start dowerloading: {urls[0][1]}")
            #     file_path  = download_audio(urls[0][1])
            #     time.sleep(0.1)
            #     mf = MusicFile(file_path)
            #     mf.set_bpm(get_bpm(file_path))
            #     mf.set_artist(song['artist'])
            #     mf.set_title(song['title'])
            #     # mf.set_album

            #     print(f"-------------------------\nBPM={mf.bpm} \n {mf}")
            best_url = urls[0][1]
            if best_url:
                print(f"Start dowerloading: {best_url}")
                file_path  = download_audio(best_url)
                time.sleep(0.1)
                mf = MusicFile(file_path)
                mf.set_bpm(get_bpm(file_path))
                mf.set_artist(song['artist'])
                mf.set_title(song['title'])
                # mf.set_album

                print(f"-------------------------\nBPM={mf.bpm} \n {mf}")
                # print(f"BPM (aubio): {bpm_aubio}")
            print("-------------------------")

        # # Example usage of the new function
        # track_to_search = top_10_songs[0]['title'] + ' ' + top_10_songs[0]['artist']
        # youtube_url = get_youtube_search_url(track_to_search)
        # print(f"Search URL for '{track_to_search}' on YouTube: {youtube_url}")
    else:
        print("Failed to retrieve top songs.")


