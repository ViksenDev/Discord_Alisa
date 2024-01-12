import discord
import random
import asyncio
import requests
import json
from discord.ext import commands, tasks
import config
from conditions import condition_translations
import datetime
import logging
import os
import urllib.request
import praw
from bs4 import BeautifulSoup
from discord import File
from io import BytesIO

intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)


        

is_paused = False
    
@bot.command(name='start', description="Позвать Алису")
async def start_command(ctx):
    global is_paused
    is_paused = False  # сбрасываем флаг паузы
    await ctx.send("Привет! Я - Алиса! И я снова тут!")
    await bot.change_presence(status=discord.Status.online, activity = discord.Activity(type=discord.ActivityType.listening, name="Вас"))

@bot.command(name='pause', description="Заткнуть Алису на 5 минут")
async def pause_bot(ctx):
    global is_paused
    is_paused = True
    await ctx.send("Всё, поняла, молчу.")
    await bot.change_presence(status=discord.Status.idle, activity = discord.Activity(type=discord.ActivityType.listening, name="только себя"))
    await asyncio.sleep(300)
       
# Загрузка вопросов и ответов из qa.json
def load_qa():
    try:
        with open('qa.json', 'r', encoding='utf-8') as f:
            qa_dict = json.load(f)
        print("Вопросы и ответы успешно загружены из JSON")
    except Exception as e:
        print(f"Ошибка при загрузке 'qa.json': {e}")
        qa_dict = {}
    return qa_dict

qa_dict = load_qa()

def process_message(text):
    response = None
    for key in qa_dict:
        if key.lower() in text:  # Проверка наличия ключевого слова в тексте сообщения, игнорируя регистр символов
            response = random.choice(qa_dict[key])
            break
    return response

def get_weather():
    api_key = "e00eee27c422413080b155000240801"
    city = "Moscow"

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    data = response.json()

    condition = data["current"]["condition"]["text"]


    condition_translation = condition_translations.get(condition, condition)
    temperature = data["current"]["temp_c"]
    wind =  data["current"]["wind_mph"]
    wind2 = data["current"]["wind_degree"]
    gust = data["current"]["gust_mph"]
    vis = data["current"]["vis_km"]

    return f"## **   Сейчас в Москве:** \n* {condition_translation}\n- Температура: {temperature}°C\n- Ветер {wind2}°, {wind} м/с,\n- Порывы {gust} м/с \n- Видимость {vis} км "


@bot.event
async def on_ready():
    print(f"Вы вошли как {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="Вас"))
    await run_check_log_file()
    await meme()

music_streams = []

def save_music_streams():
    with open('playlists.txt', 'w') as file:
        for stream in music_streams:
            file.write(stream + '\n')

@bot.command()
async def play(ctx):
    remove_non_working_playlists()
    
    if ctx.author.voice is None:
        await ctx.send('Вы должны находиться в голосовом канале.')
        return

    if not music_streams:
        await ctx.send('Нет доступных плейлистов.')
        return

    stream_url = random.choice(music_streams)
    
    if ctx.voice_client is None:
        channel = ctx.author.voice.channel
        await channel.connect()
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    ctx.voice_client.play(discord.FFmpegPCMAudio(stream_url))
    await ctx.send(f'Включаю музыку..')

@bot.command()
async def next(ctx):
    remove_non_working_playlists()

    if ctx.voice_client is not None:
        if len(music_streams) == 0:
            await ctx.send('Нет других плейлистов.')
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        next_stream_url = random.choice(music_streams)

        ctx.voice_client.play(discord.FFmpegPCMAudio(next_stream_url), after=lambda e: print(f'Finished playing: {next_stream_url}.'))
        await ctx.send(f'Включаю следующий плейлист..')
    else:
        await ctx.send('Алиса не находится в голосовом канале.')


@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send('Выключаю музыку..')
    else:
        await ctx.send('Алиса не находится в голосовом канале.')

@bot.command()
async def add_pl(ctx, stream_url):
    music_streams.append(stream_url)
    save_music_streams()
    await ctx.send(f'Добавлен плейлист: {stream_url}')

def remove_non_working_playlists():
    global music_streams
    music_streams = [stream for stream in music_streams if is_music_stream_available(stream)]
    save_music_streams()

def is_music_stream_available(stream_url):
    try:
        response = requests.head(stream_url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def load_music_streams():
    with open('playlists.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

music_streams = load_music_streams()



    
# Функция, которая будет вызываться при изменении статуса
logging.basicConfig(filename='example.log', level=logging.INFO)

@bot.event
async def on_presence_update(before, after):
    before_activity = getattr(before.activity, 'name', 'None')
    after_activity = getattr(after.activity, 'name', 'None')
    
    if after_activity != 'None' and before_activity != after_activity:
        member_mention = after.mention  # Получить упоминание пользователя
        if member_mention is None:  # Проверить, есть ли у участника упоминание на сервере
            member_mention = after.name  # Если нет, то использовать имя пользователя в дискорде
        guild = after.guild  # Получить сервер, на котором произошло изменение активности
        channel_without_category = None  # Инициализация переменной channel_without_category
        channel_in_category = None  # Инициализация переменной channel_in_category
        if guild.categories:
            category = guild.categories[0]
            if category.channels:
                channel_in_category = category.channels[10]
                print(f"Selected channel in category on {guild}: {category.name} {channel_in_category.name}")
                # Здесь можно добавить отправку сообщения в выбранный канал в категории
            else:
                print(f"No channels in the category on {guild}.")
        else:
            text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel) and ch.guild == guild]
            if len(text_channels) > 1:
                channel_without_category = text_channels[1]
                print(f"Selected text channel on {guild}: {channel_without_category.name}")
            else:
                print(f"No text channels in the guild {guild}.")
        
        if after_activity == 'Visual Studio':
            message = f'{member_mention}, решил написать программу в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)

        elif after_activity == 'Dota 2':
            message = f'{member_mention}, как дела с пробитием в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Farming Simulator 22':
            message = f'{member_mention}, весь урожай собрал в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Microsoft Flight Simulator':
            message = f'{member_mention}, куда сегодня летим в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Warframe':
            message = f'{member_mention}, скрытое сообщение в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            #if channel_without_category:
                #await channel_without_category.send(message)
            #if channel_in_category:
               # await channel_in_category.send(message)
        elif 'Skyforge' in after_activity:
            message = f'{member_mention}, скрытое сообщение в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            #if channel_without_category:
              #  await channel_without_category.send(message)
            #if channel_in_category:
               # await channel_in_category.send(message)  
        elif 'The End Is Coming' in after_activity:
            message = f'{member_mention}, скрытое сообщение в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            #if channel_without_category:
              #  await channel_without_category.send(message)
            #if channel_in_category:
               # await channel_in_category.send(message)          
        elif 'Lineage' in after_activity:
            message = f'{member_mention}, уже купил пуху дракона в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif 'Gate 3' in after_activity:
            message = f'{member_mention}, сколько уже концовок завершил в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Garry`s Mod':
            message = f'{member_mention}, Москва 2020 уже появилась в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Sea of Thieves':
            message = f'{member_mention}, куда сегодня плывем в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Euro Truck Simulator 2':
            message = f'{member_mention}, может конвой в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'American Truck Simulator':
            message = f'{member_mention}, погнали в Лас Вегас в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        elif after_activity == 'Assetto Corsa Competizione':
            message = f'{member_mention}, ставишь новые рекорды в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)
        else:
            message = f'{member_mention}, решил катнуть в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            if channel_without_category:
                await channel_without_category.send(message)
            if channel_in_category:
                await channel_in_category.send(message)

async def check_log_file():
    # Путь к файлу LapLog.txt
    file_path = r'\\VIKSEN-PC\Logs\LapLog.txt'
    
    # Путь к файлу simhub.json
    simhub_file_path = r'\\VIKSEN-PC\Logs\simhub.json'

    def get_last_line_count(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data.get('last_line_count', 0)
        else:
            return 0

    def update_last_line_count(file_path, count):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            data['last_line_count'] = count
            
            with open(file_path, 'w') as file:
                json.dump(data, file)
        else:
            with open(file_path, 'w') as file:
                data = {'last_line_count': count}
                json.dump(data, file)

    # Проверяем существование файла
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            # Считываем содержимое файла
            lines = file.read().splitlines()

        # Проверяем наличие новых записей
        if len(lines) > get_last_line_count(simhub_file_path):
            # Обновляем количество строк
            update_last_line_count(simhub_file_path, len(lines))

            # Считываем только последнюю строку
            last_line = lines[-1]

            # Парсим значения параметров
            if 'Laptime' in last_line:
                lt = last_line.split('"Laptime":')[1].strip().strip('"')
                formatted_lt = lt[3:12]  # Извлекаем только нужную часть времени
                print(f'Lap time: {formatted_lt}')

            if 'NewSimHubAllTimeBest' in last_line:
                bt = last_line.split('"NewSimHubAllTimeBest":')[1].strip().strip('"')
                formatted_bt = bt[3:12]  # Извлекаем только нужную часть времени
                print(f'Best time: {formatted_bt}')

            if 'LapMaxSpeed' in last_line:
                ms = last_line.split('"LapMaxSpeed":')[1].strip().strip('"')
                print(f'Max Speed: {ms[:3]} км/ч')

            # Создаем embeds зеленого цвета

            current_time = datetime.datetime.now().strftime("%d.%m.%Y в %H:%M:%S")
            
            embeds = [{
                "title": "Завершение круга",
                "description": f"- Время круга: {formatted_lt}\n- Лучший круг: {formatted_bt}\n- Максимальная скорость: {ms[:3]} км/ч\n- Текущее время: {current_time}",
                "color": 65280  # Зеленый цвет в десятичном формате
            }]

            # Отправляем вебхук
            payload = {
                "content": f"",
                "embeds": embeds,
            }
            webhook_url = "https://discord.com/api/webhooks/1191486176482316410/gv0NiNvzY2WrkXKkYIvNpNYKS5QNm77EAZs6_R5dw9AMRMyM0-0VZ_JUjDx6xr1xPB4D"
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 204:
                print("Webhook sent successfully")
            else:
                print("Failed to send webhook")

        else:
            return False
    else:
        return False

    return True

async def run_check_log_file():
    while True:
        new_line_added = await check_log_file()
        if new_line_added:
            await asyncio.sleep(10)
        else:
            #print('Нет новых записей в файле')
            await asyncio.sleep(3)
        

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.content:
        return

    if is_paused and message.content.lower() != "/start":
        if "алиса" in message.content.lower():
            start_command_ctx = await bot.get_context(message)
            await start_command_ctx.invoke(bot.get_command('start'))
        return

    if "заткнись" in message.content.lower():
        await pause_bot(message.channel)
        return    


    if message.content.startswith('/meme'):
        # Отправляем GET-запрос на страницу для получения случайного мема
        response = requests.get('https://img.randme.me/')
        if response.status_code == 200:
            # Получаем изображение из ответа и создаем из него файловый буфер в памяти
            meme_image = BytesIO(response.content)
            meme_image.seek(0)  # Перемещаем указатель на начало файла, если это необходимо

            # Создаем объект файла Discord из буфера в памяти
            discord_file = File(meme_image, filename="meme.png")

            # Отправляем изображение в чат
            await message.channel.send(file=discord_file)
        else:
            await message.channel.send('Не удалось загрузить мем.')
 
            
    if message.content.lower().startswith('мем'):
        # Отправляем GET-запрос на страницу для получения случайного мема
        response = requests.get('https://img.randme.me/')
        if response.status_code == 200:
            # Получаем изображение из ответа и создаем из него файловый буфер в памяти
            meme_image = BytesIO(response.content)
            meme_image.seek(0)  # Перемещаем указатель на начало файла, если это необходимо

            # Создаем объект файла Discord из буфера в памяти
            discord_file = File(meme_image, filename="meme.png")

            # Отправляем изображение в чат
            await message.channel.send(file=discord_file)
        else:
            await message.channel.send('Не удалось загрузить мем.')

    
    if message.content.startswith('/'):
        return

    # Текстовая часть для обработки обычных сообщений
    print(f"Получено сообщение: {message.content}")

    # Приведение текста сообщения к нижнему регистру
    text = message.content.lower()

    # Проверяем, содержится ли в сообщении слово 'погода'
    if 'погод' in text:
        weather_report = get_weather()  # Предполагаем, что функция get_weather() существует
        await message.channel.send(weather_report)
        print(f"Отправлено погодное уведомление: {weather_report}")
        return
    
    # Проверяем, содержится ли в сообщении слово 'музык'
    if 'музык' in text:
        command_ctx = await bot.get_context(message)
        await command_ctx.invoke(bot.get_command('play'))
        return
    
    # Проверяем, содержится ли в сообщении слово 'выключ'
    if 'выключ' in text:
        command_ctx = await bot.get_context(message)
        await command_ctx.invoke(bot.get_command('leave'))
        return
    
    # Проверяем, содержится ли в сообщении слово 'некст'
    if 'некст' in text:
        command_ctx = await bot.get_context(message)
        await command_ctx.invoke(bot.get_command('next'))
        return

    # Предполагаем, что функция process_message() существует и обрабатывает сообщение
    response = process_message(text)

    # Если функция process_message() возвращает не None, отправляем ответ в чат
    if response is not None:
        await message.channel.send(response)
        print(f"Отправлен ответ: {response}")



# В конце основной функции тоже добавлен вывод в консоль
async def main():
    print("Запуск Алисы...")
    await bot.start(config.TOKEN)    
asyncio.run(main())




  