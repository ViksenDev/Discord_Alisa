﻿import discord
import random
import asyncio
import requests

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = discord.Client(intents=intents)

# Словарь сообщений
messages_dict = {
    "greeting": [
        "Привет! Я Алиса, готова помочь. Как твои дела?",
        "Доброго времени суток! Чем я могу быть полезной?",
        "Здравствуй! Что нового у тебя?",
        "Приветствую! Как прошел твой день?",
        "Рада тебя видеть! Что нового в твоей жизни?",
        "Доброе утро! Как ты сегодня?",
        "Привет! Что у тебя запланировано на сегодня?",
        "Здравствуй! Как проходит твой день?",
        "Привет! Какие у тебя новости?",
        "Рада снова тебя слышать! Как твои дела?",
        "Привет! Что нового в мире?",
    ],
    "question": [
        "Какой твой любимый цвет?",
        "Расскажи о своем любимом фильме.",
        "Какое твое хобби?",
        "Если бы ты могла выбрать любую страну для путешествия, куда бы ты поехала?",
        "Какое твое любимое время года?",
        "Что тебе нравится делать в свободное время?",
        "Какая книга тебе больше всего запомнилась?",
        "Какую музыку ты предпочитаешь слушать?",
        "Какой твой любимый вид спорта?",
        "Какой твой самый любимый видеоигры?",
        "Какой твой любимый вид транспорта?",
    ],
    "farewell": [
        "До свидания! Желаю удачного дня!",
        "Пока! Возвращайся еще!",
        "До скорого! Буду ждать твоего возвращения!",
        "Желаю тебе отличного времени! До встречи!",
        "До свидания! Пусть у тебя будет замечательный день!",
        "Прощай! Надеюсь, скоро увидимся снова!",
        "Удачи! Пусть все твои планы сбудутся!",
        "До встречи! Помни, что всегда можешь обратиться ко мне!",
        "До свидания! Пусть тебя сопровождают только хорошие вещи!",
        "Прощай! Желаю тебе только приятных моментов в жизни!",
        "До свидания! Надеюсь, скоро снова услышать твой голос!",
    ],
    "periodic": [
        "Привет! Я хотела просто поздороваться.",
        "Как дела? Что нового у тебя?",
        "Привет! Я здесь, чтобы поддержать беседу.",
        "Как проходит твой день? Расскажи мне о своих планах.",
        "Я надеюсь, у тебя все идет хорошо. Если нужна помощь, обращайся!",
        "Привет! Как твои дела? Что нового происходит в твоей жизни?",
        "Как проходит твой день? У меня есть несколько интересных фактов, которыми могу поделиться.",
        "Привет! Что нового в мире? Есть ли что-то, что тебя заинтересовало?",
        "Как твои дела? Если нужна поддержка или просто поговорить, я здесь для тебя.",
        "Привет! Что нового в твоей жизни? Есть ли у тебя какие-то планы на ближайшее время?",
        "Как ты? Я надеюсь, у тебя все отлично. Если есть что-то, о чем хочешь поговорить, я готова выслушать.",
    ]
}

# Функция обработки входящих сообщений
def process_message(message):
    if any(word in message for word in ["привет", "здравствуй", "добр", "Алиса", "Alisa"]):
        response = random.choice(messages_dict["greeting"])
    elif any(word in message for word in ["погода", "температура", "прогноз"]):
        weather = get_weather()
        response = f"Прогноз погоды: {weather}"
    elif any(word in message for word in ["пока", "до свидания"]):
        response = random.choice(messages_dict["farewell"])
    elif "?" in message:
        response = random.choice(messages_dict["question"])
    else:
        response = None

    print(f"Сообщение: {message}")
    print(f"Ответ: {response}")

    if response:
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")

    return response

def get_weather():
    api_key = "e00eee27c422413080b155000240801"
    city = "Moscow"

    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    data = response.json()

    condition = data["current"]["condition"]["text"]
    temperature = data["current"]["temp_c"]

    return f"Сейчас в {city} {condition}, температура: {temperature}°C"

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user or not message.content:
        return

    response = process_message(message.content)

    if response is not None:
        await message.channel.send(response)

async def send_periodic_messages():
    await bot.wait_until_ready()
    
    channel1 = bot.get_channel(515483857126948864)
    channel2 = bot.get_channel(515483542361341954)

    if channel1 is None or channel2 is None:
        print("Не удалось найти каналы. Проверьте правильность указанных ID каналов.")
        return

    channels = [channel1, channel2]

    while not bot.is_closed():
        channel = random.choice(channels)
        response = random.choice(messages_dict["periodic"])

        try:
            await channel.send(response)
        except discord.errors.Forbidden:
            print(f"Невозможно отправить сообщение в канал {channel.name}. Продолжение выполнения...")
            continue
        else:
            print(f"Сообщение успешно отправлено в канал {channel.name}.")

        interval = random.randint(2400, 7200)
        await asyncio.sleep(interval)

async def main():
    await bot.start('MTE5MzgxODI1MDM3NTYxMDM5OA.GrJ4xL.rvceXus2bgh17eAhlMxcsP0I4WfmnwUHp564BU')

asyncio.run(main())