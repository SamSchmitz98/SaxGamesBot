import discord
import os
import requests
import json
import config

client = discord.Client()
TOKEN = config.TOKEN
awaiting_players = False
playing_fakin_it = False
player_list = []

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global awaiting_players
    global player_list
    global playing_fakin_it
    if message.author == client.user:
        return
    
    if (awaiting_players):
        if message.content.startswith('-begin'):
            playing_fakin_it = True
            await message.channel.send('Sounds good! We\'ll begin now')

        if message.content.startswith('-players'):
            player_string = ""
            for player in player_list:
                player_string += player.name + ", "
            await message.channel.send(player_string[:-2])

        elif client.user.mentioned_in(message):
            if message.author not in player_list:
                player_list.append(message.author)

    if (playing_fakin_it):
        if message.content.startswith('-end')
            awaiting_players = False
            playing_fakin_it = False

    if message.content.startswith('-fakin it') or (client.user.mentioned_in(message) and 'fakin it' in message.content):
        awaiting_players = True
        await message.channel.send('Who wants to play?')

client.run(TOKEN)