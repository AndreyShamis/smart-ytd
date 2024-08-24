

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class MusicFile(object):

    def __init__(self, path=None) -> None:
        self.path = path
        self.bpm = None
        self.title = None
        self.artist = None
        self.album = None
        self.year = None
        self.genre = None
        self.duration = None
        self.track_number = None
        self.rank = None

        if path:
            self.load_metadata()

    def load_metadata(self):
        try:
            audio = MP3(self.path, ID3=EasyID3)
            self.title = audio.get('title', [None])[0]
            self.artist = audio.get('artist', [None])[0]
            self.album = audio.get('album', [None])[0]
            self.year = audio.get('date', [None])[0]
            self.genre = audio.get('genre', [None])[0]
            self.track_number = audio.get('tracknumber', [None])[0]
            self.duration = int(audio.info.length)
            # BPM is not usually included in standard tags, but if available:
            self.bpm = audio.get('bpm', [None])[0]
        except Exception as e:
            print(f"Error loading metadata for {self.path}: {e}")

    def __str__(self):
        return (f"{self.title} - {self.artist}:"
                # f"Album: {self.album}\n"
                # f"Year: {self.year}\n"
                # f"Genre: {self.genre}\n"
                # f"Track Number: {self.track_number}\n"
                f"Duration: {self.duration} s. BPM: {self.bpm} Path: {self.path} Rank: {self.rank}")

    def __repr__(self):
        return (f"MusicFile(path={self.path!r}, bpm={self.bpm!r}, title={self.title!r}, artist={self.artist!r}, "
                f"album={self.album!r}, year={self.year!r}, genre={self.genre!r}, duration={self.duration!r}, "
                f"track_number={self.track_number!r}, rank={self.rank!r})")
    
    def set_bpm(self, bpm):
        try:
            audio = MP3(self.path, ID3=EasyID3)
            audio['bpm'] = str(bpm)
            audio.save()
            self.bpm = bpm
            print(f"BPM set to {bpm} for {self.path}")
        except Exception as e:
            print(f"Error setting BPM for {self.path}: {e}")

    def set_artist(self, artist):
        try:
            audio = MP3(self.path, ID3=EasyID3)
            audio['artist'] = artist
            audio.save()
            self.artist = artist
            print(f"Artist set to {artist} for {self.path}")
        except Exception as e:
            print(f"Error setting artist for {self.path}: {e}")
    
    def set_title(self, title):
        try:
            audio = MP3(self.path, ID3=EasyID3)
            audio['title'] = title
            audio.save()
            self.title = title
            print(f"Title set to {title} for {self.path}")
        except Exception as e:
            print(f"Error setting title for {self.path}: {e}")

    def set_album(self, album):
        try:
            audio = MP3(self.path, ID3=EasyID3)
            audio['album'] = album
            audio.save()
            self.album = album
            print(f"Album set to {album} for {self.path}")
        except Exception as e:
            print(f"Error setting album for {self.path}: {e}")

    def set_rank(self, rank):
        self.rank = rank
        print(f"Rank set to {rank} for {self.path}")
