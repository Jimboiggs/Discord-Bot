import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]

starter_encouragements = [
    "Cheer up!",
    "Hang in there!",
    "You are a great person / bot!"
]

if "responding" not in db.keys():
    db["responding"] = True

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return quote

def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        if not isinstance(encouragements, list):
            encouragements = list(encouragements)
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]

def delete_encouragement(index):
    if "encouragements" in db.keys():
        encouragements = db["encouragements"]
        if not isinstance(encouragements, list):
            encouragements = list(encouragements)
        if len(encouragements) > index:
            del encouragements[index]
            db["encouragements"] = encouragements

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("$hello"):
        await message.channel.send("Hello!")

    elif msg.startswith("$inspire"):
        quote = get_quote()
        await message.channel.send(quote)

    if db.get("responding", True):  # Default to True if "responding" key does not exist
        options = starter_encouragements.copy()
        if "encouragements" in db.keys():
            encouragements = list(db["encouragements"])
            options.extend(encouragements)

        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encouraging message added.")

    if msg.startswith("$del"):
        if "encouragements" in db.keys():
            try:
                index = int(msg.split("$del ", 1)[1])
                delete_encouragement(index)
                await message.channel.send("Encouraging message deleted.")
            except (IndexError, ValueError):
                await message.channel.send("Invalid index or format. Please use $del <index>.")
        else:
            await message.channel.send("No encouragements to delete.")

    if msg.startswith("$list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = list(db["encouragements"])
        await message.channel.send(encouragements)

    if msg.startswith("$responding"):
        value = msg.split("$responding ", 1)[1]

        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on.")
        else:
            db["responding"] = False
            await message.channel.send("Responding is off.")

keep_alive()
client.run(os.getenv("TOKEN"))
