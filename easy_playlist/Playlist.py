#  coding: utf-8
from random import choice, shuffle
from mutagen.mp3 import MP3
from threading import Thread
import time
import json
import sys

from easy_events import Events, Parameters


def shorter(file, before: int = 0, after: int = 0, output: str = None):
    music_len = MP3(file).info.length

    with open(file, "rb", encoding="utf8") as f:
        music = f.readlines()

    nb_lines = len(music)
    cut_before = int(before * nb_lines / music_len)
    cut_after = int(after * nb_lines / music_len)

    if not output:
        output = file.replace(".mp3", "CUT.mp3")

    with open(output, "wb", encoding="utf8") as f:
        for lig in music[cut_before:cut_after]:
            f.write(lig)


class Music:
    def __init__(self, path_to_file: str):
        self.file = path_to_file
        self.name = self.file.replace("\\", "/").rsplit("/", 1)[-1]
        self.length = MP3(self.file).info.length
        self.timer = 0
        self.playing = False
        self.over = False

    def add_timer(self, val=1):
        self.timer += val

        if self.timer > self.length:
            self.stop()
            return False

        return True

    def play(self):
        self.reset_timer()
        self.over = False
        self.playing = True

    def stop(self):
        self.over = True
        self.playing = False
        self.reset_timer()

    def pause(self):
        self.playing = False

    def resume(self):
        self.over = False
        self.playing = True

    def reset_timer(self):
        self.timer = 0

    def is_over(self):
        return self.over

    def is_playing(self):
        return self.playing

    def build_str(self):
        res = ""
        for key, value in self.__dict__.items():
            res += f"{key} : {value}\n"

        return res

    def __str__(self):
        return self.build_str()


class Playlist:
    def __init__(self,
                 name: str = "playlist",
                 playlist: list = [],
                 loop: bool = False,
                 auto: bool = False
                 ):

        self.name = name
        self.current = None
        self.index = 0

        self.loop = loop
        self.auto = auto

        self.playlist = []
        self.lock = True

        if playlist:
            self.add_music(playlist)

        self.init()

    def get_name(self):
        return self.name

    def get_playlist(self):
        return self.playlist

    def get_current(self):
        return self.current

    def get_index(self):
        return self.index

    def is_auto(self):
        return self.auto

    def is_over(self):
        return not self.check_index(1, check_end=True)

    def set_name(self, name: str):
        self.name = name

    def set_playlist(self, playlist: list):
        self.playlist = playlist

    def set_current(self, music: Music):
        self.current = music

    def set_index(self, index: int):
        self.index = index
        self.check_index()
        self.update()

    def insert_music(self, index: int, music: Music):
        if isinstance(music, str):
            self.playlist.insert(index, Music(music))

        elif isinstance(music, Music):
            self.playlist.insert(index, music)

        self.update(False)

    def add_music(self, music: Music):
        if isinstance(music, str):
            self.playlist.append(Music(music))

        elif isinstance(music, Music):
            self.playlist.append(music)

        elif isinstance(music, list):
            for m in music:
                if isinstance(m, str):
                    m = Music(m)
                self.playlist.append(m)

        self.update(False)

    def get_names(self):
        return [m.name for m in self.playlist]

    def get_files(self):
        return [m.file for m in self.playlist]

    def get_music(self, val):
        if isinstance(val, int) and (0 <= val < len(self.playlist)):
            return self.playlist[val]

        elif isinstance(val, str):
            for m in self.playlist:
                if val == m.name:
                    return m
                elif val == m.file:
                    return m

        elif isinstance(val, Music):
            for m in self.playlist:
                if m == val:
                    return m

    def remove_music(self, music: Music):
        if isinstance(music, Music) and music in self.playlist:
            self.playlist.remove(music)

        elif isinstance(music, list):
            for m in music:
                if isinstance(m, str):
                    m = self.get_music(m)
                if m:
                    self.playlist.remove(m)

        self.check_index()
        self.update(False)

    def remove_index(self, index: int):
        if 0 <= index < len(self.playlist):
            self.playlist.pop(index)
            self.check_index()
            self.update(False)

    def shuffle_playlist(self):
        shuffle(self.playlist)

    def get_random(self):
        return choice(self.playlist)

    def check_index(self, i: int = 0, index: int = None, check_end: bool = False):
        if not index:
            index = self.index

        index += i

        if index >= len(self.playlist):
            if self.loop and check_end:
                return True

            elif check_end:
                return False

            self.index = 0

        elif index < 0:
            if self.loop and check_end:
                return True

            elif check_end:
                return False

            self.index = len(self.playlist) - 1

        elif i and not check_end:
            self.index += i

        return True

    def next(self, play: bool = True):
        if not self.playlist:
            return False

        self.stop()

        if not self.check_index(1, check_end=True):
            return False

        self.check_index(1)
        self.update(play)
        return True

    def previous(self, play: bool = True):
        if not self.playlist:
            return False

        self.stop()

        if not self.check_index(-1, check_end=True):
            return False

        self.check_index(-1)
        self.update(play)
        return True

    def clear(self):
        self.playlist = []
        self.stop()
        self.index = 0

    def init(self):
        self.set_current(None)
        self.index = -1

        if self.playlist:
            self.set_current(self.playlist[0])

    def update(self, play: bool = True):
        self.set_current(self.get_music(self.index))
        if play:
            self.play()

    def play(self, val: int = None):

        if self.index < 0:
            self.index = 0

        if not val:
            val = self.index
            self.check_index()

        music = self.get_music(val)

        if not music:
            self.add_music(val)
            music = self.get_music(val)

        self.stop()

        if isinstance(val, str):
            index = self.playlist.index(music)
            self.set_index(index)

        self.set_current(music)

        try:
            self.current.play()
        except AttributeError:
            pass

    def stop(self):
        try:
            self.current.stop()
        except AttributeError:
            pass

        self.set_current(None)

    def pause(self):
        try:
            self.current.pause()
        except AttributeError:
            pass

    def resume(self):
        try:
            self.current.resume()
        except AttributeError:
            pass

    def save(self):
        with open(f"{self.name}.json", "w", encoding="utf8") as f:
            f.write(json.dumps(self.get_files()))

    def load(self):
        with open(f"{self.name}.json", "r", encoding="utf8") as f:
            val = json.loads(f.read())
        self.add_music(val)

    def build_str(self):
        res = ""
        for key, value in self.__dict__.items():
            if key == "current":
                res += f"{key} : \n-----MUSIC-----\n{value}---------------\n"
            elif key == "playlist":
                res += f"{key} : {self.get_names()}\n"
            else:
                res += f"{key} : {value}\n"
        return res

    def __str__(self):
        return self.build_str()


class Playlists(Events):
    def __init__(self, run: bool = True):
        Events.__init__(self)
        self.playlists = []
        self.run = run
        self.launched = False

        if run:
            self.start()

    def _check_music(self):
        while self.run:
            for playlist in self.playlists:
                music = playlist.get_current()

                if not music:
                    playlist.lock = True
                    continue

                if not music.is_over() and music.is_playing():
                    playlist.lock = False
                    music.add_timer(.2)

                elif music.is_over() and playlist.is_auto() and not playlist.lock:
                    playlist.lock = True
                    self.call_event("music_over", playlist)
                    playlist.next()

                elif music.is_over() and not playlist.lock:
                    playlist.lock = True
                    self.call_event("music_over", playlist)

            time.sleep(.2)

        self.launched = False

    def call_event(self, name: str, playlist):
        data = Parameters(name)
        data.playlist = playlist
        data.music = playlist.get_current()
        self.process_data(data)

    def put_playlist(self, playlist):
        self.playlists.append(playlist)

    def remove_playlist(self, playlist):
        if playlist in self.playlist:
            self.playlist.remove(playlist)

    def stop(self):
        self.run = False
        self.launched = False

    def start(self):
        if not self.launched:
            self.run = True
            Thread(target=self._check_music).start()

        self.launched = True

    def add_playlist(self,
                     name: str = "playlist",
                     playlist: list = [],
                     loop: bool = False,
                     auto: bool = False
                    ):

        self.playlists.append(Playlist(name, playlist, loop, auto))

    def add_music(self, playlist: str, music: str):
        if isinstance(playlist, str):
            temp = self.get_playlist(playlist)

            if not temp:
                self.add_playlist(playlist, music)
                playlist = self.get_playlist(playlist)
            else:
                playlist = temp

        playlist.add_music(music)

    def get_playlist(self, name: str):
        for play in self.playlists:
            if name == play.get_name():
                return play

    def exit(self):
        self.stop()


if __name__ == "__main__":
    pl = Playlists()
    pl.add_playlist(name="test1", playlist=["music/bip1.mp3", "music/bip2.mp3"])
    pl.add_playlist(name="test2", playlist=["music/bip1.mp3", "music/bip2.mp3"])
    pl.add_music("test1", "music/bip3.mp3")

    pl1 = pl.get_playlist("test1")
    pl1.play()

    pl2 = pl.get_playlist("test2")
    pl2.play()

    print("starting...")


    @pl.event("music_over")
    def music_over(data):
        print(f"[{data.playlist.name}] {data.music.name} is over, next song now!")

        if data.playlist.is_over():
            print(f"Playlist {data.playlist.name} is over")
            data.playlist.clear()
            return

        data.playlist.next()
