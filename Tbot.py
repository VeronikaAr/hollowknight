import discord
import requests
from discord.ext import tasks

intents = intents = discord.Intents.all()
client = discord.Client(intents = intents)
orders = 0


@tasks.loop(seconds=60) # Повторяется каждые 2 секунды
async def my_loop(channel):
    global orders
    data = requests.get('http://localhost:5000/api/orders').json()
    if len(data) > orders:
        orders ++
        await channel.send(str(data))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Мы передаем в функцию myLoop канал, чтобы иметь возможность отправлять сообщения
    if message.content == '$start':
        my_loop.start(message.channel)
    

client.run('MTA1NTc1NjU1OTcyNjE2NjA1Ng.G9_yAJ.7cEh73HSCis2W7RVQkUnwhKKHJHkSdq5H1ynbE')