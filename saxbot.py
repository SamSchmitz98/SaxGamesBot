import discord
from discord.ext import commands
import os
import requests
import json
import config
import roledoc
import random

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!')
TOKEN = config.TOKEN
awaiting_players = False
playing_fakin_it = False
fakin_mid_round = False
player_list = []
player_wait_list = []
hand_response_list = []
number_response_list = []
point_response_list = []
voting_list = []
player_dm_channel_list = []
game_channel = None
prompt = ""
mode = "number"
faker = 0
msgid = roledoc.MSGID
emojis = roledoc.EMOJIS
roles = roledoc.ROLES

def IsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

async def send_prompts(mode):
    global player_dm_channel_list
    player_dm_channel_list = []
    if mode == "hands":
        file = "handsoftruth.txt"
        lst = hand_response_list
        faker_string = "Yes or No"
    if mode == "number":
        file = "numberpressure.txt"
        lst = number_response_list
        faker_string = "a number between 0-10"
    if mode == "point":
        file = "yougottapoint.txt"
        lst = point_response_list
        faker_string = "the name of someone playing (including yourself)"
    global prompt
    f = open(file, "r")
    prompts = f.readlines()
    for line in enumerate(f):
        prompts.append(line)
    promptnum = -1
    while promptnum == -1:
        for i in range(len(prompts)):
            if random.randint(0, 2) == 0:
                promptnum = i
                break
    prompt = prompts[promptnum]
    for player in player_list:
        channel = await player.create_dm()
        player_dm_channel_list.append(channel)
        lst.append(None)
        if player_list.index(player) == faker:
            await channel.send("You are the faker! Send me " + faker_string + " and try to blend in")
        else:
            await channel.send(prompt)
    prompts.append(prompts.pop(promptnum))
    f = open(file, "w")
    f.writelines(prompts)
    return

@client.event
async def on_ready():
    global msgid
    global emojis
    global roles
    print('We have logged in as {0.user}'.format(client))
    # f = open("roledoc.txt", "r")
    # for line in f.readlines():
    #     if line.startswith("MSGID"):
    #         msgid = int(line.split(":")[1])
    #         print(msgid)
    #     if line.startswith("EMOJIS"):
    #         for emoji in line.split(":")[1].split(","):
    #             emojis.append(emoji)
    #             print(emoji)
    #     if line.startswith("ROLES"):
    #         for role in line.split(":")[1].split(","):
    #             roles.append(role)
    #             print(role)

@client.event
async def on_message(message):
    global awaiting_players
    global player_list
    global player_wait_list
    global hand_response_list
    global number_response_list
    global point_response_list
    global voting_list
    global playing_fakin_it
    global fakin_mid_round
    global faker
    global prompt
    global mode
    global game_channel
    global player_dm_channel_list
    global msgid
    if message.author == client.user:
        return
    
    if (awaiting_players):
        if message.content.startswith('!start'):
            playing_fakin_it = True
            await message.channel.send('Sounds good! We\'ll begin now\n\nType !hands for Hands of Truth\nType !number for Number Pressure\nType !point for You Gotta Point')
            return
        if message.content.startswith('!end') and not playing_fakin_it:
            awaiting_players = False
            playing_fakin_it = False
            fakin_mid_round = False
            player_list = []
            player_dm_channel_list = []
            await message.channel.send("Game cancelled")
            return

        if message.content.startswith('!players'):
            if not player_list:
                await message.channel.send("No one has joined yet")
                return
            player_string = ""
            for player in player_list:
                if player.nick != None:
                    player_string += player.nick + ", "
                else:
                    player_string += player.name + ", "
            await message.channel.send(player_string[:-2])
            return

        elif client.user.mentioned_in(message) and message.channel == game_channel:
            if message.author not in player_list:
                player_list.append(message.author)
                await message.add_reaction('\U0001F44D')
            return

    if (playing_fakin_it):
        if message.content.startswith('!end'):
            awaiting_players = False
            playing_fakin_it = False
            fakin_mid_round = False
            player_list = []
            player_dm_channel_list = []
            await message.channel.send("Thanks for playing!")
            return
        if len(hand_response_list) != 0:
            if message.author in player_list and message.channel in player_dm_channel_list:
                if message.content.lower() == "yes" or message.content.lower() == "no":
                    hand_response_list[player_list.index(message.author)] = message.content
                    await message.add_reaction('\U0001F44D')
            if None not in hand_response_list:
                prompt_responses_string = "The prompt was:\n" + prompt + "\nAnd the responses were:\n"
                for i in range(0,len(player_list)):
                    prompt_responses_string += str(i+1) + ". " + player_list[i].name + ": " + hand_response_list[i] + "\n"
                prompt_responses_string += "\nNow Vote!"
                hand_response_list = []
                for player in player_list:
                    voting_list.append(None)
                for dm_channel in player_dm_channel_list:
                    await dm_channel.send(prompt_responses_string)
                await game_channel.send(prompt_responses_string)
            return
        if len(number_response_list) != 0:
            if message.author in player_list and message.channel in player_dm_channel_list:
                if IsInt(message.content) and int(message.content) >= 0 and int(message.content) <= 10:
                    number_response_list[player_list.index(message.author)] = message.content
                    await message.add_reaction('\U0001F44D')
            if None not in number_response_list:
                prompt_responses_string = "The prompt was:\n" + prompt + "\nAnd the responses were:\n"
                for i in range(0,len(player_list)):
                    prompt_responses_string += str(i+1) + ". " + player_list[i].name + ": " + number_response_list[i] + "\n"
                prompt_responses_string += "\nNow Vote!"
                number_response_list = []
                for player in player_list:
                    voting_list.append(None)
                for dm_channel in player_dm_channel_list:
                    await dm_channel.send(prompt_responses_string)
                await game_channel.send(prompt_responses_string)
            return
        if len(point_response_list) != 0:
            if message.author in player_list and message.channel in player_dm_channel_list:
                    point_response_list[player_list.index(message.author)] = message.content
                    await message.add_reaction('\U0001F44D')
            if None not in number_response_list:
                prompt_responses_string = "The prompt was:\n" + prompt + "\nAnd the responses were:\n"
                for i in range(0,len(player_list)):
                    prompt_responses_string += str(i+1) + ". " + player_list[i].name + ": " + point_response_list[i] + "\n"
                prompt_responses_string += "\nNow Vote!"
                point_response_list = []
                for player in player_list:
                    voting_list.append(None)
                for dm_channel in player_dm_channel_list:
                    await dm_channel.send(prompt_responses_string)
                await game_channel.send(prompt_responses_string)
            return
        
        if len(voting_list) != 0:
            if message.author in player_list and message.channel in player_dm_channel_list:
                if IsInt(message.content) and int(message.content) > 0 and int(message.content) <= len(player_list):
                    voting_list[player_list.index(message.author)] = int(message.content)-1
            if None not in voting_list:
                vote_results = [0 for i in range(len(voting_list))]
                for vote in voting_list:
                    vote_results[vote] += 1
                voted_for = -1
                tie = False
                vote_results_string = "Voting results:\n\n"
                for i in range(len(vote_results)):
                    vote_results_string += player_list[i].name + ": " + str(vote_results[i]) + "\n"
                    if voted_for == -1 or vote_results[i] > vote_results[voted_for]:
                        voted_for = i
                        tie = False
                    elif vote_results[i] == vote_results[voted_for]:
                        tie = True
                vote_results_string += "\n"
                if tie:
                    vote_results_string += "There was a tie. No one is outed"
                    for dm_channel in player_dm_channel_list:
                        await dm_channel.send(vote_results_string)
                    await game_channel.send(vote_results_string)
                    await send_prompts(mode)
                else:
                    if voted_for == faker:
                        vote_results_string += player_list[voted_for].name + " was the faker!\n\nSelect the next round"
                        fakin_mid_round = False
                        for dm_channel in player_dm_channel_list:
                            await dm_channel.send(vote_results_string)
                        await game_channel.send(vote_results_string)
                    else:
                        vote_results_string += player_list[voted_for].name + " was not the faker!"
                        for dm_channel in player_dm_channel_list:
                            await dm_channel.send(vote_results_string)
                        await game_channel.send(vote_results_string)
                        await send_prompts(mode)
                voting_list = []
                        


        #Hands of Truth
        if message.content.startswith('!hands'):
            if(fakin_mid_round):
                await message.channel.send("<@" + str(message.author.id) + "> Please wait for the current round to end")
            else:
                fakin_mid_round = True
                mode = "hands"
                faker = random.randint(0, len(player_list)-1)
                await message.channel.send("Now playing a round of Hands of Truth")
                await send_prompts("hands")
            return
        #Number Pressure
        if message.content.startswith('!number'):
            if(fakin_mid_round):
                await message.channel.send("<@" + str(message.author.id) + "> Please wait for the current round to end")
            else:
                fakin_mid_round = True
                mode = "number"
                faker = random.randint(0, len(player_list)-1)
                await message.channel.send("Now playing a round of Number Pressure")
                await send_prompts("number")
            return
        #You Gotta Point
        if message.content.startswith('!point'):
            if(fakin_mid_round):
                await message.channel.send("<@" + str(message.author.id) + "> Please wait for the current round to end")
            else:
                fakin_mid_round = True
                mode = "point"
                faker = random.randint(0, len(player_list)-1)
                await message.channel.send("Now playing a round of You Gotta Point")
                await send_prompts("point")
            return

    if message.content.startswith('!fakin it') or (client.user.mentioned_in(message) and 'fakin it' in message.content):
        awaiting_players = True
        game_channel = message.channel
        await message.channel.send('Who wants to play?\n\nMention me if you want to play\nType !start to start')
        #await msg.add_reaction('\U0001F64B')
        return

    if message.content.startswith('!add '):
        message_list = message.content.split()
        if message_list[1] == "hands":
            f = "handsoftruth.txt"
        elif message_list[1] == "number":
            f = "numberpressure.txt"
        elif message_list[1] == "point":
            f = "yougottapoint.txt"
        else:
            await message.channel.send("Unknown gamemode. Please try '!add hands', '!add number', or '!add point'")
            return
        new_prompt = ""
        for i in range(2, len(message_list)):
            new_prompt += message_list[i] + " "
        new_prompt += "\n"
        writer = open(f, "r+")
        content = writer.read()
        writer.seek(0, 0)
        writer.write(new_prompt+content)
        return

    if message.content.startswith('!confession'):
        print(message.channel.id)
        await client.get_channel(940308822231220274).send(message.content[12:])

    if message.content.startswith('!dndrecap'):
        writer = open("dndrecap.txt", "r")
        await message.channel.send("Last time on DnD...\n\n")
        msg = writer.read(2000).strip()
        while len(msg) > 0:
            await message.channel.send(msg)
            msg = writer.read(2000).strip()
        await message.channel.send("\n\nWhat's going to happen next? Tune in tonight!")

    if message.content.startswith('!dndupdate'):
        writer = open("dndrecap.txt", "r+")
        content = writer.read()
        writer.write(message.content[10:])

    if message.content.startswith('!dndclear'):
        writer = open("dndrecap.txt", "r+")
        await message.channel.send("Cleared\n\n")
        msg = writer.read(2000).strip()
        while len(msg) > 0:
            await message.channel.send(msg)
            msg = writer.read(2000).strip()
        writer.truncate(0)

    if message.content.startswith('!dndhelp'):
        await message.channel.send("!recapdnd for the current recap\n!updatednd to append text to the end of the recap\n!cleardnd to erase the current recap, but outputting it first\n!heropointhelp for hero points information")

    if message.content == '!heropoints':
        f = open("heropoints.txt", "r")
        lines = f.readlines()
        result = ""
        for x in range(1, len(lines)):
            user = await client.fetch_user(lines[x].split()[0])
            result += user.name + " has " + lines[x].split()[1] + " hero points\n"
        await message.channel.send(result)

    if message.content.startswith('!heropointset'):
        f = open("heropoints.txt", "r")
        lines = f.readlines()
        if (str(message.author.id) != lines[0].split()[1]):
            await message.channel.send("Nope! You aren't the DM")
            return
        player = message.mentions[0].id
        found = False
        for x in range(len(lines)):
            if (lines[x].split()[0] == str(player)):
                lines[x] = str(player) + " " + message.content.split()[2] + "\n"
                found = True
                break
        if not found:
            lines.append(str(player) + " " + message.content.split()[2] + "\n")
        f.close()
        f = open("heropoints.txt", "w")
        f.writelines(lines)
        await message.add_reaction('\U0001F44D')

    if message.content.startswith('!heropointuse'):
        f = open("heropoints.txt", "r")
        lines = f.readlines()
        player = message.author.id
        points = 1
        if len(message.content.split()) == 2:
            points = int(message.content.split()[1])
        if points < 0:
            await message.channel.send("<@" + str(player) + "> quit trying to cheat or the DM will be angry")
            return
        for x in range(len(lines)):
            if (lines[x].split()[0] == str(player)):
                if (lines[x].split()[1] == "0"):
                    await message.channel.send("<@" + str(player) + "> You are out of Hero points silly")
                    return   
                lines[x] = str(player) + " " + str(int(lines[x].split()[1])-points) + "\n"
                break
        f.close()
        f = open("heropoints.txt", "w")
        f.writelines(lines)
        await message.add_reaction('\U0001F60E')

    if message.content.startswith('!heropointall'):
        if len(message.content.split()) != 2:
            await message.channel.send("Wrong number of arguments. Sorry")
            return
        addednum = message.content.split()[1]
        f = open("heropoints.txt", "r")
        lines = f.readlines()
        if (str(message.author.id) != lines[0].split()[1]):
            await message.channel.send("Nope! You aren't the DM")
            return
        for x in range(1, len(lines)): 
            lines[x] = lines[x].split()[0] + " " + str(int(lines[x].split()[1])+int(addednum)) + "\n"
        f.close()
        f = open("heropoints.txt", "w")
        f.writelines(lines)
        await message.add_reaction('\U0001F60E')

    if message.content.startswith('!heropointadd'):
        if len(message.content.split()) != 2:
            await message.channel.send("Wrong number of arguments. Sorry")
            return
        addedplayer = message.mentions[0].id
        f = open("heropoints.txt", "r")
        lines = f.readlines()
        if (str(message.author.id) != lines[0].split()[1]):
            await message.channel.send("Nope! You aren't the DM")
            return
        for x in range(1, len(lines)):
            if (lines[x].split()[0] == "addedplayer"):
                lines[x] = lines[x].split()[0] + " " + str(int(lines[x].split()[1])+1) + "\n"
        f.close()
        f = open("heropoints.txt", "w")
        f.writelines(lines)
        await message.add_reaction('\U0001F60E')


    if message.content.startswith('!heropointdm'):
        admin = message.mentions[0].id
        f = open("heropoints.txt", "r")
        lines = f.readlines()
        if (str(message.author.id) != lines[0].split()[1] and str(message.author.id) != "265569176884609024" ):
            await message.channel.send("Nope! You aren't the DM")
            return
        lines[0] = "DM: " + str(admin) + "\n"
        f.close()
        f = open("heropoints.txt", "w")
        f.writelines(lines)
        await message.add_reaction('\U0001F44D')

    if message.content.startswith('!heropointhelp'):
        await message.channel.send("!heropoints to view current heropoint levels\n!heropointdm followed by the user to set the current DM\n!heropointuse to use a hero point\n!heropointset followed by the user and a number to set the users current hero point level\n!heropointall followed by a number to add that many points to every user")

    if message.content.startswith('!lmgtfy'):
        googlemessage = "https://letmegooglethat.com/?q="
        for x in message.content.split()[1:]:
            googlemessage += x + "+"
        googlemessage = str[:-1]
        await message.channel.send(str)

    if ':0' in message.content:
        await message.channel.send(':0')

    if ':O' in message.content:
        await message.channel.send(':0')

    if '😮' in message.content:
        await message.channel.send(':0')

    if '!createrolemessage' in message.content:
        newmessage = "Add the reactions for the corresponding role:\n"
        for x in range(len(emojis)):
            newmessage += str(emojis[x]) + ": " + roles[x] + "\n"
        msg = await message.channel.send(newmessage)
        msgid = msg.id
        print(msgid)
        f = open("roledoc.py", "r")
        lines = f.readlines()
        lines[0] = "MSGID = " + str(msgid) + "\n"
        f.close()
        f = open("roledoc.py", "w")
        f.writelines(lines)

        for emoji in emojis:
            await msg.add_reaction(emoji)
    
    if '!addrole' in message.content:
        if len(message.content.split()) < 3:
            await message.channel.send("Not enough arguments. Try '!addrole <<emoji>> <<role name>>")
            return
        emoji = message.content.split()[1]
        role = " ".join(message.content.split()[2:])
        if emoji in emojis:
            await message.channel.send("Emoji already in use. Please remove it or use another one")
            return
        if role in roles:
            await message.channel.send("Role already in use. Please remove it or use another one")
            return
        emojis.append(emoji)
        roles.append(role)
        f = open("roledoc.py", "r")
        lines = f.readlines()
        lines[1] = "EMOJIS = ['"
        for emj in emojis:
            lines[1] += str(emj) + "', '"
        lines[1] = lines[1][:-4]
        lines[1] += "']\n"
        lines[2] = "ROLES = ['" + "', '".join(roles) + "']\n"
        f.close()
        f = open("roledoc.py", "w", encoding='utf-8')
        f.writelines(lines)
        msg = await client.get_channel(800154991456157758).fetch_message(msgid)
        await msg.add_reaction(emoji)
        newmessage = "Add the reactions for the corresponding role:\n"
        for x in range(len(emojis)):
            newmessage += str(emojis[x]) + ": " + roles[x] + "\n"
        await msg.edit(content = newmessage)

    if '!removerole' in message.content:
        if len(message.content.split()) != 2:
            await message.channel.send("Wrong number of arguments. Try '!removerole <<emoji>>")
            return
        emoji = message.content.split()[1]
        if emoji not in emojis:
            await message.channel.send("Could not find emoji. Please identify by emoji")
            return
        roles.pop(emojis.index(emoji))
        emojis.remove(emoji)
        f = open("roledoc.py", "r")
        lines = f.readlines()
        lines[1] = "EMOJIS = ['"
        for emj in emojis:
            lines[1] += str(emj) + "', '"
        lines[1] = lines[1][:-4]
        lines[1] += "']\n"
        lines[2] = "ROLES = ['" + "', '".join(roles) + "']\n"
        f.close()
        f = open("roledoc.py", "w", encoding='utf-8')
        f.writelines(lines)
        msg = await client.get_channel(800154991456157758).fetch_message(msgid)
        await msg.clear_reaction(emoji)
        newmessage = "Add the reactions for the corresponding role:\n"
        for x in range(len(emojis)):
            newmessage += str(emojis[x]) + ": " + roles[x] + "\n"
        await msg.edit(content = newmessage)
         


        
            
@client.event
async def on_raw_reaction_add(payload):
    #role permission channel '839326133311766548'
    #await reaction.message.channel.send("Emoji")
    if payload.member.bot:
        return
    if payload.message_id != msgid:
        return
    if payload.emoji.name in emojis:
        Role = discord.utils.get(payload.member.guild.roles, name=roles[emojis.index(payload.emoji.name)])
        await payload.member.add_roles(Role)

@client.event
async def on_raw_reaction_remove(payload):
    #role permission channel '839326133311766548'
    #Channel = client.get_channel('800154991456157758')
    if payload.message_id != msgid:
        return
    member = await client.get_guild(payload.guild_id).fetch_member(payload.user_id)
    if payload.emoji.name in emojis:
        Role = discord.utils.get(member.roles, name=roles[emojis.index(payload.emoji.name)])
        await member.remove_roles(Role)
        #await client.remove_roles(user, Role)

client.run(TOKEN)
