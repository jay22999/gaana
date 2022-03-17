import json
import requests
from hashlib import md5
from urllib.parse import urlparse
import re
from concurrent.futures import ThreadPoolExecutor
import os
from os import path, mkdir
from os.path import join
import subprocess
import shutil
from mutagen.mp4 import MP4, MP4Cover
import ffmpeg

# Firstinput
song = input('Enter Song / Artist Name : ')
# song = "https://gaana.com/album/pal-pal-dil-ke-paas"

# Urls
url = 'https://apiv2.gaana.com/track/stream'
login_url = 'https://gaanajsso.indiatimes.com/sso/crossapp/identity/web/verifyLoginOtpPassword'
auto_suggest_temp = f"https://gaana.com/apiv2?country=IN&keyword=pal&type=search"

# sassion
s = requests.session()
s.headers = {
    'origin': 'https://gaana.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
}

login_header = {
    'Origin': 'https://gaana.com',
    'Referer': 'https://gaana.com',
    'isjssocrosswalk': 'true',
    'platform': 'WAP',
    'channel': 'gaana.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
}


class Gaana:
    def __init__(self):
        self.data = {
            "ps": "Acebf39db-5f2e-4729-bfec-65ea862add60",
            "track_id": '',
            "request_type": "web",
            "quality": "high",
            "st": "hls",
            "ssl": "true",
        }
        self.title_of_playlist = ''

    def playlist_download(self, song_url):

        base = urlparse(song_url).path
        base_name = path.basename(base)
        play = re.search(r'\/(.*)\/', base)
        typo = play.group(1)

        auto_suggest_2 = f"https://gaana.com/apiv2?seokey={base_name}&type={typo}Detail"
        album_track_list = s.post(url=auto_suggest_2)
        album_track_list = (album_track_list.json())

        # for album
        if album_track_list.get("album"):
            self.title_of_playlist = album_track_list.get("album")["title"]

        # for playlist
        elif album_track_list.get('playlist'):
            self.title_of_playlist = album_track_list.get("playlist")[
                "meta_h1_tag"]

        new_album_track_list = []

        for i in album_track_list.get("tracks"):
            new_album_track_list.append((i.get("track_id"), i.get("track_title"), i.get(
                'language'), i.get('artwork_large'), i.get('release_date'), i.get('artist')[0]['name']))

        return new_album_track_list

    def check(self, res1):
        if res1.isdigit():
            res1 = int(res1)
            if res1 in range(0, inde+1):
                return True
        else:
            return False

    def ht(self, download_track):
        self.data['track_id'] = download_track[0]
        ht1 = self.data['track_id'] + "|" + \
            self.data["ps"] + "|03:40:31 sec"
        self.ht1 = md5(ht1.encode("utf-8")).hexdigest() + \
            self.data['ps'][3:9] + "="
        self.download_track = download_track

    def playlist(self):

        self.data['ht'] = self.ht1
        a = s.post(url, data=self.data)
        a = a.json()
        stream = (a['stream_path'])

        try:
            m3u8_ = requests.get(stream)
        except:
            return
        playlist = re.search(
            r'\/.*\.m3u8.*', m3u8_.text)

        stream_url = urlparse(stream)
        playlist_url = urlparse(playlist.group(0))
        self.stream_url = stream_url._replace(
            path=playlist_url.path, query=playlist_url.query)

    def stream_(self):
        x = requests.get(self.stream_url.geturl())
        self.ts_urls = []
        base = path.basename(self.stream_url.path)
        for ts in re.finditer(r'.*\.ts.*', x.text):
            ts_url = urlparse(ts.group())
            final_ts_url_path = self.stream_url.path.replace(
                base, ts_url.path)
            ts_url = self.stream_url._replace(
                path=final_ts_url_path, query=ts_url.query)
            self.ts_urls.append(ts_url)

    def get_song(self, x):

        base = path.basename(x.path)
        track_id = x.path.split("/")[-3]

        track_path = join(self.temp_path, track_id)
        if not path.isdir(track_path):
            mkdir(track_path)

        r = requests.get(x.geturl())

        track_base = join(track_path, base)

        with open(track_base, "wb+") as f:
            f.write(r.content)

    def mutagen(self):
        audio = MP4(self.output)
        audio['covr'] = [MP4Cover(self.thumbnil.content)]

        try:
            audio.add_tags()
        except Exception:
            pass

        audio.save()

        audio["\xa9nam"] = self.download_track[1]
        audio["\xa9ART"] = self.download_track[5]

        audio.save()

    def thread(self):

        if len(self.title_of_playlist) != 0:
            if not path.isdir(self.title_of_playlist):
                mkdir(self.title_of_playlist)
            self.temp_path = join(os.getcwd(), self.title_of_playlist)

        else:
            if not path.isdir(self.download_track[1]):
                mkdir(self.download_track[1])
            self.temp_path = join(os.getcwd(), self.download_track[1])

        with ThreadPoolExecutor() as t:
            t.map(self.get_song, self.ts_urls)

        if path.isdir(join(self.temp_path, self.download_track[0])):
            if '?' in self.download_track[1]:
                new_song_name = str(self.download_track[1]).replace('?', '')
                file_name = join(self.temp_path, f"{new_song_name}.ts")
                self.output = os.path.join(
                    self.temp_path, f'{new_song_name}.m4a')
            else:
                file_name = join(
                    self.temp_path, f"{self.download_track[1]}.ts")
                self.output = os.path.join(
                    self.temp_path, f'{self.download_track[1]}.m4a')

            with open(file_name, 'wb+') as f:
                for ts_url in self.ts_urls:
                    base = path.basename(ts_url.path)

                    t2_path = join(
                        self.temp_path, self.download_track[0], base)

                    if path.exists(t2_path):
                        with open(t2_path, "rb") as rf:
                            f.write(rf.read())

            self.thumbnil = requests.get(self.download_track[3])

            ffmpeg.input(file_name).output(self.output).run()

            # subprocess.run(
            #     f'''ffmpeg -y  -i "{file_name}" -c copy "{self.output}"''', capture_output=False)

            self.mutagen()

            os.remove(file_name)
            shutil.rmtree(os.path.join(self.temp_path, self.download_track[0]))
            return False
        else:
            return False


download_song = Gaana()

if song.startswith("https") and 'artist' not in song:
    track_id_list = download_song.playlist_download(song)
    for i in track_id_list:

        download_song.ht(i)
        download_song.playlist()
        download_song.stream_()
        download_song.thread()
    exit()

else:
    parse = urlparse(song)
    if song.startswith("https") and 'artist' in song:
        song = os.path.basename(parse.path)
    auto_suggest = f"https://gaana.com/apiv2?country=IN&keyword={song}&type=search"
    suggetion = s.post(url=auto_suggest)
    suggetion = suggetion.json()
    f = True


f = True
while f == True:
    for gr_inde, i in enumerate(suggetion.get('gr')):
        inde = 1
        track_name = []
        for x in i['gd']:
            if x.get('sti') == 'Artist':
                if x.get('innerGdList'):
                    for a in x.get('innerGdList'):
                        track_name.append((a['iid'], a['ti']))
                        print(
                            f"\n{inde} Song Name :- {a.get('ti')}\nSong Details:- {a.get('sti')}\nLanguage:- {a.get('language')}\n")
                        inde += 1

            else:
                print(
                    f"\n{inde} Song Name :- {x.get('ti')}\nSong Details:- {x.get('sti')}\nLanguage:- {x.get('language')}\n")

                # for i in album_track_list.get("tracks"):
                #     new_album_track_list.append((i.get("track_id"), i.get("track_title"), i.get(
                #             'language'), i.get('artwork_large'), i.get('release_date'), i.get('artist')[0]['name']))

                track_name.append(
                    (x['iid'], x['ti'], x['language'], x['aw'], x['sti'], x['language']))
                inde += 1

        if len(suggetion['gr']) <= gr_inde+1:
            f = False
        else:
            print("Press 0 For More Results")
            close = False
            while close == False:
                res1 = input('\nwhich one you want to download:- ')
                close = download_song.check(res1)
            if res1 != '0':
                download_track = track_name[int(res1)-1]
                download_song.ht(download_track)
                download_song.playlist()
                try:
                    download_song.stream_()
                except:
                    print('Sorry please choose another one')
                    continue
                # download_song.playlist_download(download_track[1])
                f = download_song.thread()
                break
            else:
                continue
