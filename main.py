import json
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import asyncio
import os
import random

channel_id = 1082305144143740958
MUSIC_DIR = 'pisnyary'
FILATOV_DIR = 'filatov'

with open('config.json', 'r') as file:
    config = json.load(file)

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Создаем плейлист
def create_playlist(directory):
    playlist = []
    for file in os.listdir(directory):
        if file.endswith('.mp3'):
            playlist.append(os.path.join(directory, file))
    return playlist


@bot.command(name='pisnyari')
async def play(ctx):
    if ctx.channel.id != channel_id:
        return
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("Вы не находитесь в голосовом канале!")
        return

    # Создаем плейлист
    playlist = create_playlist(MUSIC_DIR)
    random.shuffle(playlist)

    try:
        voice = await voice_channel.connect()
    except discord.errors.ClientException:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    if not playlist:
        await ctx.send("Плейлист пуст!")
        return
    for song in playlist:
        track_name = os.path.splitext(os.path.basename(song))[0]
        audio = discord.FFmpegPCMAudio(song)
        audio = discord.PCMVolumeTransformer( audio, volume=0.5)
        voice.play(audio)
        await ctx.send(f"Играет {track_name}")
        while voice.is_playing():
            await asyncio.sleep(1)

@bot.command(name='filatov')
async def play_filatov(ctx):
    if ctx.channel.id != channel_id:
        return
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("Вы не находитесь в голосовом канале!")
        return

    # Создаем плейлист
    playlist = create_playlist(FILATOV_DIR)
    random.shuffle(playlist)

    try:
        voice = await voice_channel.connect()
    except discord.errors.ClientException:
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    random_citata = random.choice(playlist)
    track_name = os.path.splitext(os.path.basename(random_citata))[0]
    voice.play(discord.FFmpegPCMAudio(random_citata))
    while voice.is_playing():
        await asyncio.sleep(1)
    await voice.disconnect()

@bot.command(name='stop')
async def stop(ctx):
    if ctx.channel.id != channel_id:
        return
    voice_client = ctx.guild.voice_client
    if voice_client:
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Музыка остановлена")
            await voice_client.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу!")

@bot.command(name='skip')
async def skip(ctx):
    if ctx.channel.id != channel_id:
        return
    voice_client = ctx.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Трек пропущен")

@bot.command(name='clean')
async def clean(ctx, limit: int = 10):
    if ctx.channel.id != channel_id:
        return
    """Удаляет сообщения из канала"""
    messages = []
    async for message in ctx.channel.history(limit=limit):
        if message.author == bot.user:
            messages.append(message)
    await ctx.channel.delete_messages(messages)
    await ctx.send(f"Удалено {len(messages)} сообщений.", delete_after=5)

@bot.event
async def on_message(message):
    """Удаляет сообщения, начинающиеся с префикса ! после 10 секунд"""
    if message.content.startswith('!'):
        #await asyncio.sleep(2)
        await message.delete()

    await bot.process_commands(message)

@bot.command(name='play')
async def play_audio(ctx, filename):
    if ctx.channel.id != channel_id:
        return
    # Подключаемся к голосовому каналу пользователя
    voice_channel = ctx.author.voice.channel
    vc = await voice_channel.connect()

    # Определяем путь к файлу
    filepath = f"frazki/{filename}.mp3"

    # Проверяем, существует ли файл
    try:
        with open(filepath):
            pass
    except FileNotFoundError:
        await ctx.send(f"Файл {filename}.mp3 не найден.")
        await vc.disconnect()
        return

    # Воспроизводим аудиофайл
    vc.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=filepath)))

    # Ожидаем, пока трек закончится
    while vc.is_playing():
        await asyncio.sleep(1)

    # Отключаемся от голосового канала
    await vc.disconnect()


bot.run(config['token'], reconnect=True)
