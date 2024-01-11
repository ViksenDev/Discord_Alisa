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

intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Список URL-адресов потоков музыки
music_streams = [
    'https://nashe2.hostingradio.ru/ultra-128.mp3',
    'http://nashe2.hostingradio.ru/rock-128.mp3',
    'http://ep128.streamr.ru'
    'http://listen1.myradio24.com:9000/5967'
]

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

@bot.command()
async def ym(ctx):
    # Проверяем, что автор команды находится в голосовом канале
    if ctx.author.voice is None:
        await ctx.send('Вы должны находиться в голосовом канале, чтобы использовать эту команду.')
        return
    
    # Выбираем случайный поток музыки
    stream_url = random.choice(music_streams)
    
    # Присоединяемся к голосовому каналу автора команды
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()
    
    # Воспроизводим поток музыки
    voice_client.play(discord.FFmpegPCMAudio(stream_url))
    
    # Ожидаем окончания потока музыки
    while voice_client.is_playing():
        await asyncio.sleep(1)
    
    # Отключаемся от голосового канала
    await voice_client.disconnect()
    
@bot.command()
async def ym_off(ctx):
    # Проверяем, что автор команды находится в голосовом канале
    if ctx.author.voice is None:
        await ctx.send('Вы должны находиться в голосовом канале, чтобы использовать эту команду.')
        return
    
    # Проверяем, что бот находится в голосовом канале
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        await ctx.send('Бот не находится в голосовом канале.')
        return
    
    # Останавливаем воспроизведение музыки
    voice_client.stop()
    
    # Отключаемся от голосового канала
    await voice_client.disconnect()

    
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
            message = f'{member_mention}, выфармим нового фрейма в {after_activity}?'
            print(message)  # Дублирование сообщения в консоль
            #if channel_without_category:
                #await channel_without_category.send(message)
            #if channel_in_category:
               # await channel_in_category.send(message)
        elif after_activity == 'Skyforge':
            message = f'{member_mention}, выфармим нового фрейма в {after_activity}?'
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

reddit = praw.Reddit(client_id='lIwhm8aNKKH4BQ',
                     client_secret='VrI0rAVzIeOuZVV_SYiR0jXZiA4',
                     user_agent='bot-o-meme by TheWizzy1547')


used_memes = []

def get_memes_urls(limit=100):
    req_subreddits = ["memes", "dankmemes", "HistoryMemes", "Pikabu", "rusAskReddit"]  # subreddits
    meme_list = []
    for req_subreddit in req_subreddits:
        subreddit = reddit.subreddit(req_subreddit)
        for submission in subreddit.new(limit=(limit//len(req_subreddits)) + 1):
            if submission.url in used_memes:
                continue
            meme_list.append(
                ["https://reddit.com" + submission.permalink, submission.title, submission.url])
            used_memes.append(submission.url)

    random.shuffle(meme_list)  # to shuffle obtained posts
    return meme_list

# meme command
@bot.command(name="meme", description="Посмотреть мемас")
async def meme(message):
    meme_list = get_memes_urls(1)
    for meme_set in meme_list[:1]:
        response_permalink = meme_set[0]
        response_title = meme_set[1]
        response_url = meme_set[2]
        colors = [0xff0000, 0x00ff00, 0x0000ff, 0x000000,
                  0xffffff, 0xffff00, 0x00ffff, 0xff00ff]
        random.shuffle(colors)
        emb = discord.Embed(title=response_title,
                            url=response_permalink, color=colors[0])
        emb.set_image(url=response_url)
        await message.send(embed=emb)

        

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

    await bot.process_commands(message)
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
    
    # Проверяем, содержится ли в сообщении слово 'мем'
    if 'мем' in text:
        command_ctx = await bot.get_context(message)
        await command_ctx.invoke(bot.get_command('meme'))
        return
    
    # Проверяем, содержится ли в сообщении слово 'музык'
    if 'музык' in text:
        command_ctx = await bot.get_context(message)
        await command_ctx.invoke(bot.get_command('ym'))
        return
    
    # Проверяем, содержится ли в сообщении слово 'выключ'
    if 'выключ' in text:
        command_ctx = await bot.get_context(message)
        await command_ctx.invoke(bot.get_command('ym_off'))
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




  