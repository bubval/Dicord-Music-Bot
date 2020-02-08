import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
from os import system
import shutil


# Generated on Discord Dev
TOKEN = open("token.txt").readline()
# What comes before the command
BOT_PREFIX = '/'

# Initializing bot to predefined prefix
bot = commands.Bot(command_prefix=BOT_PREFIX)


# Whenever bot is logged in with specified token, it will print this.
@bot.event
async def on_ready():
    print(bot.user.name + " is active!\n")


# Join command
# Aliases are short-hand for people who don't want to type "Join"
@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    # if we are in a voice channel, and it is connected to a voice channel already
    if voice and voice.is_connected():
        await voice.move_to(channel)
    # If we are in a voice channel, but it is not connected
    else:
        voice = await channel.connect()

    # Bug: Whenever I use join and then play, it wouldn't play audio until disconnect and rejoin
    # What I've done it have the bot leave and then rejoin automatically to solve it
    # Join -> Leave -> Join
    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Joined {channel}")


# Leave command
# Aliases are short-hand for people who don't want to type "Leave"
@bot.command(pass_context=True, aliases=['l', 'lea'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")


# Play command
# Aliases are short-hand for people who don't want to type "Play"
@bot.command(pass_context=True, aliases=['p', 'pla'])
async def play(ctx, url: str):

    def check_queue():
        # Check if Queue folder exists
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            # Queue length after current song is over
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next\n")
                print(f"Songs still in queue: {still_q}")

                # Check if song we just played is still there
                song_there = os.path.isfile("song.mp3")
                if song_there is True:
                    # Delete the file of the song that just ended playing
                    os.remove("song.mp3")

                # Move the next song in queue to the main directory
                shutil.move(song_path, main_location)

                # Check if there is an mp3 file, then rename it to song.mp3
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "song.mp3")

                # Play audio
                # After checks if the song is done playing
                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e:check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.value = 0.07
            else:
                queues.clear()
                return
        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")

    # check if file exists in directory
    song_there = os.path.isfile("song.mp3")

    # Check if it is being played
    try:
        # Remove song if file exists
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but is being played")
        await ctx.send("ERROR: Music currently playing")
        return

    # Check for old Queue folder
    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        # Remove old Queue folder
        if Queue_infile is True:
            print("Remove old Queue Folder")
            # Removes folder and all sub-files/sub-folder
            # OS cannot remove folder w/ files
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder found")

    await ctx.send("Getting everything ready")
    # Current voice channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    # Set download options to high quality
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        # Pass options to youtube downloader
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            # Download song
            ydl.download([url])
    except:
        print("FALLBACK: youtube_dl does not support this URL. Check if URL is from Spotify")
        # Get current working directory
        c_path = os.path.dirname(os.path.realpath(__file__))
        # Send this to terminal
        # Downloads song to current directory
        system("spotdl -f " + '"' + c_path + '"' + " -s " + url)

    # Current working directory
    for file in os.listdir("./"):
        # Find the downloaded file
        if file.endswith(".mp3"):
            name = file
            print(f"File name: {file}\n")
            # Rename file
            os.rename(file, "song.mp3")

    # Play audio
    # After checks if the song is done playing
    # Queues next song
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.value = 0.07
    try:
        nname = name.rsplit("-", 2)
        await ctx.send(f"Playing: {nname}")
    except:
        await ctx.send(f"Playing Song")

    print("Playing")


# Pause command
# Aliases are short-hand for people who don't want to type "Pause"
@bot.command(pass_context=True, aliases=['pa', 'pau'])
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    # Check if bot is in voice channel
    if voice and voice.is_playing():
        print("Music Paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music failed pause")
        await ctx.send("Music not playing")


# Resume command
# Aliases are short-hand for people who don't want to type "Resume"
@bot.command(pass_context=True, aliases=['r', 'res'])
async def resume(ctx):

    voice = get(bot.voice_clients,  guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")


# Stop command
# Aliases are short-hand for people who don't want to type "Stop"
@bot.command(pass_context=True, aliases=['s', 'sto'])
async def stop(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    # Remove all files in queue
    queues.clear()
    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_paused():
        print("Stopped music")
        voice.stop()
        await ctx.send("Stopped music")
    elif voice and voice.is_playing():
        print("Stopped music")
        voice.stop()
        await ctx.send("Stopped music")
    else:
        print("No music playing, failed to stop")
        await ctx.send("No music playing, failed to stop")


queues = {}


# Queue command
# Aliases are short-hand for people who don't want to type "Queue"
@bot.command(pass_context=True, aliases=['q', 'que'])
async def queue(ctx, url):
    # Check if Queue is in working directory
    Queue_infile = os.path.isdir("./Queue")

    if Queue_infile is False:
        os.mkdir("Queue")

    # Get absolute path of the queue
    DIR = os.path.abspath(os.path.realpath("Queue"))

    # Get the number of files in Queue
    q_num = len(os.listdir(DIR))
    # Song number of next song
    q_num += 1
    add_queue = True
    while add_queue:
        # Check if number is in dictionary
        if q_num in queues:
            q_num += 1
        else:
            # Adds to queue and get out of loop
            add_queue = False
            queues[q_num] = q_num

    # Make sure the song has that number attached to it.
    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    # Set download options to high quality
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        # Pass options to youtube downloader
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            # Download song
            ydl.download([url])
    except:
        print("FALLBACK: youtube_dl does not support this URL. Check if URL is from Spotify")
        # Get path to Queue folder
        q_path = os.path.abspath(os.path.realpath("Queue"))
        # Downloads song to Queue directory with specified name
        system(f"spotdl -ff song{q_num} -f " + '"' + q_path + '"' + " -s " + url)

    await ctx.send("Adding song " + str(q_num) + " to the queue")

    print("Song added to queue\n")


# Next command
# Aliases are short-hand for people who don't want to type "Next"
@bot.command(pass_context=True, aliases=['n', 'nex'])
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing next song")
        voice.stop()
        await ctx.send("Next Song")
    else:
        print("No music playing, failed to play next song")
        await ctx.send("No music playing, failed to play next song")


bot.run(TOKEN)
