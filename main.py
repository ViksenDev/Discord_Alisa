import discord
import random
import asyncio
import requests
import json
from discord.ext import commands, tasks
import config
from conditions import condition_translations
from datetime import datetime
import logging

intents = discord.Intents.default()
intents.typing = True
intents.presences = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

is_paused = False
    
@bot.command(name='start')
async def start_command(ctx):
    global is_paused
    is_paused = False  # сбрасываем флаг паузы
    await ctx.send("Привет! Я - Алиса! И я снова тут!")
    await bot.change_presence(status=discord.Status.online, activity = discord.Activity(type=discord.ActivityType.listening, name="Вас"))

@bot.command(name='pause')
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

@bot.event
async def on_message(message):
    if message.content.endswith('?'):
        channel = message.channel
        guild = message.guild
        author = message.author
        messages = []

        async for msg in channel.history(limit=10, before=message):
            if msg.author != author:
                messages.append({
                    'question': message.content,
                    'answer': msg.content
                })

        with open('new_qa.json', 'a') as file:
            json.dump(messages, file)    

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
