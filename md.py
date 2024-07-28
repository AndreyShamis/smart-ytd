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


def search_youtube(query):
    videos_search = VideosSearch(query, limit=10)
    results = videos_search.result()['result']
    return [(video['title'], video['link']) for video in results]


def calculate_similarity(query, title):
    ratio = fuzz.partial_ratio(query.lower(), title.lower())

    bonus = 0
    if "official" in title.lower():
        bonus += 10
    if "music video" in title.lower():
        bonus += 5
    if "lyric" in title.lower():
        bonus += 3

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
    return choose_best_result(results, query)


def get_top_10_songs():
    surl = "https://www.billboard.com/charts/hot-100/"
    url = "https://www.billboard.com/charts/billboard-global-200/"
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
        'outtmpl': output_path + '%(title)s.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except Exception as e:
            print(f"Произошла ошибка при скачивании: {str(e)}")
            return False


# Main execution
if __name__ == "__main__":
    top_10_songs = get_top_10_songs()

    if top_10_songs:
        print("Top 10 Songs on Billboard Hot 100:")
        for song in top_10_songs:
            print(f"{song['rank']}. {song['title']} by {song['artist']}")
            query = f"{song['artist']} {song['title']}"
            best_url = find_best_youtube_match(query)
            if best_url:
                print(f"Наилучшее совпадение: {best_url}")
                download_audio(best_url)
            print("-------------------------")

        # # Example usage of the new function
        # track_to_search = top_10_songs[0]['title'] + ' ' + top_10_songs[0]['artist']
        # youtube_url = get_youtube_search_url(track_to_search)
        # print(f"Search URL for '{track_to_search}' on YouTube: {youtube_url}")
    else:
        print("Failed to retrieve top songs.")


