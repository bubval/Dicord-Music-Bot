import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os

# Generated on Discord Dev
TOKEN = 'Njc0OTgzNDA3MzYwNjcxNzQ1.Xj1ptA.f2OkTecoHyLh_52zvkjh1f18QNo'
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
    # check if file exists in directory
    song_there = os.path.isfile("song.mp3")

    # Check if it is being played
    try:
        # Remove song if file exists
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but is being played")
        await ctx.send("ERROR: Music currently playing")
        return

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

    # Pass options to youtube downloader
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        # Download song
        ydl.download([url])

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
    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: print(f"{name} has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.value = 0.07

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname}")
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


bot.run(TOKEN)
