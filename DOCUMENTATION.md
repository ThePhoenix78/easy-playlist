# Introduction

This code is a simple implementation of a music playlist and an MP3 cutter. The playlist class uses the `Music` class to represent individual tracks in the playlist, and provides functions to add, delete, and manage the tracks. The `shorter` function cuts a specified portion of an MP3 file and saves the result to a new file.
Contents

    Music
        Class Properties
        Class Methods

    Playlist
        Class Properties
        Class Methods

    Playlists
        Class Properties
        Class Methods

## Music

The Music class represents a single track in a playlist.

### Class Properties

- file: a string representing the file path of the MP3 file

- name: the name of the MP3 file
- length: the length of the MP3 file in seconds
- timer: the current timer of the music (starts at 0)
- playing: a boolean value indicating whether the music is currently playing
- over: a boolean value indicating whether the music has finished playing
- duration: a string representation of the music length in minutes and seconds

### Class Methods

    add_timer(val: float): increments the timer by a specified value

    convert_time(): converts a value in seconds to a string representation in minutes and seconds

    str_timer(): returns a string representation of the current timer and the music length

    play(): starts playing the music and resets the timer

    stop(): stops playing the music and resets the timer

    pause(): pauses the music

    resume(): resumes playing the music

    reset_timer(): resets the timer to 0

    is_over(): returns a boolean value indicating whether the music has
    finished playing

    is_playing(): returns a boolean value indicating whether the music
    is currently playing

    build_str(): returns a string representation of the class properties

    __str__: returns the result of build_str


## Class Playlist

A class that manages a list of music tracks and implements basic functionalities such as playing, pausing, and stopping music.

### Properties

- name: A string that represents the name of the playlist.

- current: The current music track that is being played.
- index: An integer that represents the current music track's index in the playlist.
- loop: A boolean that indicates whether the playlist should loop back to the first track after all tracks have been played.
- auto: A boolean that indicates whether the playlist should automatically start playing the next track after the current track has finished.
- playlist: A list of Music objects that represent the music tracks in the playlist.
- lock: A boolean that is used to control concurrent access to the playlist.

### Methods

        __init__(self, name: str = "playlist", playlist: list = [], loop: bool = False, auto: bool = False): The constructor of the class that initializes the class properties. The name, loop, and auto parameters are optional and have default values. The playlist parameter is a list of strings or Music objects.

        get_name(): returns the name of the playlist.

        get_playlist(): returns the playlist.

        get_current(): returns the current music track.

        get_index(): returns the current music track's index in the playlist.

        get_current_timer(): returns the current music track's duration.

        str_timer(): returns the current time in the format minutes:seconds or hours:minutes:seconds depending on the length of the track.

        is_auto(): returns whether the playlist is set to play tracks automatically.

        is_over(): returns whether the playlist has reached the end of all tracks and there is no more music to play.

        set_name(name: str): sets the name of the playlist to the specified string.

        set_playlist(playlist: list): sets the playlist to the specified list.

        set_current(music: Music): sets the current music track to the specified Music object.

        set_index(index: int): sets the index of the current music track to the specified integer.

        insert_music(index: int, music: Music): inserts a Music object at the specified index in the playlist.

        add_music(music: Music): appends a Music object to the end of the playlist.

        next(): plays the next music track in the playlist.

        previous(): plays the previous music track in the playlist.

        clear(): clear the playlist from all songs

        init(): initializes the playlist and starts playing the first music track.

        play(): play the current track

        stop(): stop the current track

        pause(): pause the current track

        resume(): resume the current track

        save(): save the playlist in a json file

        load(): will load the playlist

        build_str(): returns a string representation of the class properties

        __str__: returns the result of build_str
        
