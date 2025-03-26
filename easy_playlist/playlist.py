#  coding: utf-8

from random import choice, shuffle
from threading import Thread
import asyncio
import ffmpeg
import time
import json



def get_duration(file_path: str):
    try:
        probe: dict = ffmpeg.probe(file_path, v='error', select_streams='a', show_entries='format=duration')
        return float(probe['format']['duration'])
    except Exception:
        return None


def shorter(file: str, from_start: int = 0, from_end: int = 0, output: str = None):
    music_len: float = get_duration(file)

    with open(file, "rb") as f:
        music: list = f.readlines()

    nb_lines: int = len(music)
    cut_before: int = int(from_start * nb_lines / music_len)
    cut_after: int = int(from_end * nb_lines / music_len)

    if not output:
        output: str = file.replace(".mp3", "CUT.mp3")

    with open(output, "wb") as f:
        for lig in music[cut_before:cut_after]:
            f.write(lig)


class Music:
    def __init__(self, path_to_file: str):
        self.file: str = path_to_file
        self.name: str = path_to_file

        if "\\" in path_to_file or "/" in path_to_file:
            self.name: str = path_to_file.replace("\\", "/").rsplit("/", 1)[-1]

        self.length: float = get_duration(self.file)
        self.timer: float = 0
        self.playing: bool = False
        self.over: bool = False
        self.duration: float = self.convert_time(self.length)

    def add_timer(self, value: int = 1):
        self.timer += value

        if self.timer > self.length:
            self.stop()
            return False

        return True

    def convert_time(self, value: int):
        val2, val = int(value//60), int(value % 60)
        message: str = f"{val2}:{val}"

        if val2 > 60:
            val3, val2 = int(val2//60), int(val2 % 60)
            message: str = f"{val3}:{val2}:{val}"

        return message

    def str_timer(self):
        timer: str = self.convert_time(value=self.timer)
        return f"{timer}/{self.duration}"

    def play(self):
        self.over: bool = False
        self.playing: bool = True
        self.reset_timer()

    def stop(self):
        self.over: bool = True
        self.playing: bool = False
        self.reset_timer()

    def pause(self):
        self.playing: bool = False

    def resume(self):
        self.over: bool = False
        self.playing: bool = True

    def reset_timer(self):
        self.timer: float = 0

    def is_over(self):
        return self.over

    def is_playing(self):
        return self.playing

    def build_str(self):
        res: str = ""

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

        self.name: str = name
        self.current: Music = None
        self.index: int = 0

        self.loop: bool = loop
        self.auto: bool = auto

        self.playlist: list = []
        self.lock: bool = True

        if playlist:
            self.add_music(music=playlist)

        self.init()

    def get_name(self):
        return self.name

    def get_playlist(self):
        return self.playlist

    def get_current(self):
        return self.current

    def get_index(self):
        return self.index

    def get_current_timer(self):
        return self.current.duration

    def str_timer(self):
        return self.current.str_timer()

    def is_auto(self):
        return self.auto

    def is_over(self):
        return not self.check_index(i=1, check_end=True)

    def set_name(self, name: str):
        self.name: str = name

    def set_playlist(self, playlist: list):
        self.playlist: list = playlist

    def set_current(self, music: Music):
        self.current: Music = music

    def set_index(self, index: int):
        self.index: int = index
        self.check_index()
        self.update()

    def insert_music(self, index: int, music: Music):
        if isinstance(music, str):
            self.playlist.insert(index, Music(music))

        elif isinstance(music, Music):
            self.playlist.insert(index, music)

        self.update(play=False)

    def add_music(self, music: Music):
        if isinstance(music, str):
            self.playlist.append(Music(music))

        elif isinstance(music, Music):
            self.playlist.append(music)

        elif str(type(music)) == "<class 'easy_playlist.playlist.Music'>":
            self.playlist.append(music)

        elif isinstance(music, list):
            for m in music:
                if isinstance(m, str):
                    m: Music = Music(m)

                self.playlist.append(m)

        self.update(play=False)

    def get_names(self):
        return [m.name for m in self.playlist]

    def get_files(self):
        return [m.file for m in self.playlist]

    def get_music(self, val: any):
        if isinstance(val, int) and self.is_index_in_range(index=val):
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
                    m = self.get_music(val=m)

                if m:
                    self.playlist.remove(m)

        self.check_index()
        self.update(play=False)

    def remove_index(self, index: int):
        if 0 <= index < len(self.playlist):
            self.playlist.pop(index)
            self.check_index()
            self.update(play=False)

    def shuffle_playlist(self):
        shuffle(self.playlist)

    def get_random(self):
        return choice(self.playlist)

    def get_next_music(self):
        if self.is_index_in_range(index=self.index+1):
            return self.get_music(val=self.index+1)

    def get_previous_music(self):
        if self.is_index_in_range(index=self.index-1):
            return self.get_music(val=self.index-1)

    def add_index(self, i: int = 1):
        self.index += i

    def is_index_in_range(self, index: int):
        return 0 <= index < len(self.playlist)

    def check_index(self, i: int = 0, index: int = None, check_end: bool = False):
        if not index:
            index: int = self.index

        index += i

        if index >= len(self.playlist):
            if self.loop and check_end:
                return True

            elif check_end:
                return False

            self.index: int = 0

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

        if not self.check_index(i=1, check_end=True):
            return False

        self.check_index(i=1)
        self.update(play=play)

        return True

    def previous(self, play: bool = True):
        if not self.playlist:
            return False

        self.stop()

        if not self.check_index(i=-1, check_end=True):
            return False

        self.check_index(i=-1)
        self.update(play=play)
        return True

    def clear(self):
        self.stop()
        self.playlist: list = []
        self.index: int = 0

    def init(self):
        self.set_current(music=None)
        self.index: int = -1

        if self.playlist:
            self.set_current(music=self.playlist[0])

    def update(self, play: bool = True):
        self.set_current(music=self.get_music(val=self.index))

        if play:
            self.play()

    def play(self, val: int = None):
        if self.index < 0:
            self.index: int = 0

        if not val:
            val: int = self.index
            self.check_index()

        music = self.get_music(val=val)

        if not music:
            self.add_music(music=val)
            music = self.get_music(val=val)

        self.stop()

        if isinstance(val, str):
            index = self.playlist.index(music)
            self.set_index(index=index)

        self.set_current(music=music)

        try:
            self.current.play()
        except AttributeError:
            pass

    def stop(self):
        try:
            self.current.stop()
        except AttributeError:
            pass

        self.set_current(music=None)

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
            val: dict = json.loads(f.read())

        self.add_music(music=val)

    def build_str(self):
        res: str = ""

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


class PlaylistObj:
    def __init__(self, playlist: Playlist, music: Music):
        self.playlist: Playlist = playlist
        self.music: Music = music


class Playlists:
    def __init__(self, run: bool = True):
        self.playlists: list = []
        self.run: bool = False
        self.callback: callable = None
        self._delay: float = .1

        if run:
            self.start()

    def _check_music(self):
        while self.run:
            for playlist in self.playlists:
                music: Music = playlist.get_current()

                if not music:
                    playlist.lock: bool = True
                    continue

                if not music.is_over() and music.is_playing():
                    playlist.lock: bool = False
                    music.add_timer(value=self._delay)

                elif music.is_over() and playlist.is_auto() and not playlist.lock:
                    playlist.lock: bool = True

                    if callable(self.callback):
                        self.call_event(playlist=playlist)

                    playlist.next()

                elif music.is_over() and not playlist.lock:
                    playlist.lock: bool = True

                    if callable(self.callback):
                        self.call_event(playlist=playlist)

            time.sleep(self._delay)

    async def _check_music_async(self):
        while self.run:
            for playlist in self.playlists:
                music: Music = playlist.get_current()

                if not music:
                    playlist.lock: bool = True
                    continue

                if not music.is_over() and music.is_playing():
                    playlist.lock: bool = False
                    music.add_timer(value=self._delay)

                elif music.is_over() and playlist.is_auto() and not playlist.lock:
                    playlist.lock: bool = True

                    if callable(self.callback):
                        await self.call_event(playlist=playlist)

                    playlist.next()

                elif music.is_over() and not playlist.lock:
                    playlist.lock: bool = True

                    if callable(self.callback):
                        await self.call_event(playlist=playlist)

            await asyncio.sleep(self._delay)

    def call_event(self, playlist: Playlist):
        data = PlaylistObj(playlist=playlist, music=playlist.get_current())
        self.callback(data)

    def remove_playlist(self, playlist: Playlist):
        if playlist in self.playlist:
            self.playlist.remove(playlist)

    def add_playlist(self,
                     playlist: str = "playlist",
                     musics: list = [],
                     loop: bool = False,
                     auto: bool = False
                    ):

        if isinstance(playlist, Playlist):
            pl: Playlist = playlist

        elif str(type(playlist)) == "<class 'easy_playlist.playlist.Playlist'>":
            pl: Playlist = playlist

        else:
            pl: Playlist = Playlist(name=playlist, playlist=musics, loop=loop, auto=auto)

        self.playlists.append(pl)

        return pl

    def add_music(self, playlist: str, music: list):
        """
        Add a music to the playlist, if there is no playlist it's created

        Args:
            playlist (Playlist | str): The target playlist
            music (Music | list |str): The list of music to add
        """
        if isinstance(playlist, str):
            temp: Playlist = self.get_playlist(name=playlist)

            if not temp:
                self.add_playlist(playlist=playlist, music=music)
                playlist: Playlist = self.get_playlist(name=playlist)

            else:
                playlist: Playlist = temp

        playlist.add_music(music=music)

    def get_playlist(self, name: str):
        for play in self.playlists:
            if name == play.get_name():
                return play

    def start(self):
        if not self.run:
            self.run: bool = True
            Thread(target=self._check_music).start()

    def stop(self):
        self.run: bool = False

    def exit(self):
        self.stop()

    def _start(self, run_async: bool = True):
        if not run_async and self.run:
            return

        if self.run:
            self.run: bool = False
            time.sleep(self._delay + .01)

        if not self.run:
            self.run: bool = True

            if run_async:
                self.start_async_thread(self._check_music_async())

            else:
                Thread(target=self._check_music).start()

    def start_async_thread(self, awaitable):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        Thread(target=loop.run_forever).start()
        asyncio.run_coroutine_threadsafe(awaitable, loop)
        return loop

    def stop_async_thread(self, loop):
        loop.call_soon_threadsafe(loop.stop)

    def on_music_over(self, callback: callable = None):
        def add_debug(func: callable):
            self._start(asyncio.iscoroutinefunction(func))
            self.callback: callable = func
            return func

        if callback:
            return add_debug(func=callback)

        return add_debug
