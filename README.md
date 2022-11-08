# PyPlaylist

**A library to easily manage yours playlists in python**

## Getting started

1. [**Installation**](#installation)
2. [**Usages**](#usages)
3. [**Code example**](#code-example)
4. [**Documentation**](#documentation)


## Installation

**This library will work with python 3.6+**

PyPi : `pip install PyPlaylist`

GitHub : [Github](https://github.com/ThePhoenix78/Playlist)


## Usages

This library will work with any .mp3 files
It's was desinged to work with bots in general


## Code example

### Simple tasks

```py
from PyPlaylist import Playlist

pl = Playlist()

# add music to your playlist
pl.add_music("path_to_music.mp3")
pl.add_music(["path_to_music.mp3", "path_to_other_music.mp3"])

# trigger the timer
# this will take the first song of the playlist
pl.play()

# pause the timer
pl.pause()

# resume the timer
pl.resume()

# stop the current music and trigger the timer for the next one
pl.next()

# stop the current music and trigger the timer for the previous one
pl.previous()

# stop the timer and the music
pl.stop()

# IMPORTANT
# when you don't need to use the playlist anymore do this
# this library use a thread to calculate the time
pl.exit()
```

### To make it work with a bot

```py
from PyPlaylist import Playlist

# any bot library
bot = Bot()
pl = Playlist()


# code example


@bot.command()
def add_music(music):
	pl.add_music(music)


@bot.command()
def pause():
	pl.pause()
	bot.pause_music()


@bot.command()
def resume():
	pl.resume()
	bot.resume_music()


@bot.command()
def play(music):
	pl.play(music)
	bot.play_music(music)


@pl.event("music_over")
def music_over(data):
	print(f"{data.playlist.name} {data.music.name} is over, playing next now")
	pl.next()
	bot.play_music(pl.get_current().file)

```
