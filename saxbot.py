import discord
import os
import requests
import json
import config
import random

client = discord.Client()
TOKEN = config.TOKEN
awaiting_players = False
playing_fakin_it = False
fakin_mid_round = False
player_list = []
player_wait_list = []
faker = 0

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global awaiting_players
    global player_list
    global player_wait_list
    global playing_fakin_it
    global fakin_mid_round
    global faker
    if message.author == client.user:
        return
    
    if (awaiting_players):
        if message.content.startswith('!start'):
            playing_fakin_it = True
            await message.channel.send('Sounds good! We\'ll begin now\n\nType !hands for Hands of Truth\nType !number for Number Pressure\nType !point for You Gotta Point')

        if message.content.startswith('!players'):
            player_string = ""
            for player in player_list:
                if player.nick != None:
                    player_string += player.nick + ", "
                else:
                    player_string += player.name + ", "
            await message.channel.send(player_string[:-2])

        elif client.user.mentioned_in(message):
            if message.author not in player_list:
                player_list.append(message.author)
                await message.add_reaction('\U0001F44D')

    if (playing_fakin_it):
        if message.content.startswith('!end'):
            awaiting_players = False
            playing_fakin_it = False
            fakin_mid_round = False
            await message.channel.send("Thanks for playing!")
        if message.content.startswith('!number'):
            if(fakin_mid_round):
                await message.channel.send("<@" + str(message.author.id) + "> Please wait for the current round to end")
            else:
                fakin_mid_round = True
                faker = random.randint(0, len(player_list)-1)
                await message.channel.send("Now playing a round of number pressure")
                f = open("numberpressure.txt", "r")
                prompts = f.readlines()
                for line in enumerate(f):
                    prompts.append(line)
                prompt = random.randint(0, len(prompts)-1)
                for player in player_list:
                    channel = await player.create_dm()
                    await channel.send(prompts[prompt])
                prompts.append(prompts.pop(prompt))
                f = open("numberpressure.txt", "w")
                f.writelines(prompts)


    if message.content.startswith('!fakin it') or (client.user.mentioned_in(message) and 'fakin it' in message.content):
        awaiting_players = True
        await message.channel.send('Who wants to play?\n\nMention me if you want to play\nType !start to start')
        #await msg.add_reaction('\U0001F64B')

client.run(TOKEN)