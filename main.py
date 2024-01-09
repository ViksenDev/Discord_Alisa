import discord
import random
import asyncio
import requests
import json
from discord.ext import commands
import config
import conditions

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

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
    await ctx.send("Всё, поняла, затыкаюсь.")
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
    if 'погода' in text:
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
