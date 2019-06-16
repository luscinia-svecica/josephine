#!/usr/bin/env python3

import random
import discord

FAVORITE='Yas'
CRITICAL=False
HUNGER_ONE=False
HUNGER_TEN=False
HUNGRY=False
ROLL_AS=""
REPLY_STRING=""
RESULTS = []
HUNRESULTS = []
NO_SUCCESSES=False
CREW_EMOJI = {
    'Yas' : ':mag:',
    'Meredith' : ':wolf:',
    'Joseph' : ':performing_arts:',
    'Gale' : ':tophat:',
    'Diana' : ':crown:'
}
REGISTERED_USERS = {

}

def process_diceroll(dicestring):
    global HUNGER_ONE
    global HUNGER_TEN
    global ROLL_AS
    global RESULTS
    global HUNRESULTS
    global REPLY_STRING
    global HUNGRY
    HUNGER_ONE=False
    HUNGER_TEN=False
    HUNGRY=False
    ROLL_AS=""
    RESULTS = []
    HUNRESULTS = []

    if dicestring.find('h') != -1:
        HUNGRY=True
        print("hunger dice detected")
        numdice = int(dicestring.partition('d')[0])
        print(numdice," regular dice")
        numhun = int(dicestring.partition('d')[2].partition('h')[0])
        print(numhun," hunger dice")
        if (numdice-numhun) < 1:
            numhun = numdice
            
        RESULTS=roll_dice(numdice-numhun)
        HUNRESULTS=roll_dice(numhun)

        for i in HUNRESULTS:
            if i < 2:
                HUNGER_ONE=True
                print("1 on a hunger die!")
            elif i > 9:
                HUNGER_TEN=True
                print("10 on a hunger die!")

        REPLY_STRING += str(RESULTS)
        REPLY_STRING += str(HUNRESULTS)
    else:
        print("no hunger dice, sweet")
        RESULTS=roll_dice(dicestring.partition('d')[0])
        REPLY_STRING += str(RESULTS)

def roll_dice(num):
    rolls = []
    for i in range(0,int(num)):
        rolls.append(random.randrange(1,11))

    return rolls
        

def check_successes(rolls):
    global CRITICAL
    global REPLY_STRING
    global NO_SUCCESSES
    NO_SUCCESSES=False
    CRITICAL=False

    successes = 0
    tens = 0
    if HUNGRY == True:
        for i in rolls:
            if i > 5:
                if i > 9:
                    tens += 1
                    if tens > 0 and tens % 2 == 0:
                        successes += 3
                        CRITICAL=True
                        #print("Critical: ",CRITICAL)
                        #print(successes,tens)
                    else:
                        successes += 1
                        #print(successes,tens)
                else:
                    successes += 1
                    #print(successes)
    else:
        for i in rolls:
            if i > 5:
                if i > 9:
                    tens += 1
                    if tens > 0 and tens % 2 == 0:
                        successes += 3
                        #print("Critical: ",CRITICAL)
                        CRITICAL=True
                        #print(successes,tens)
                    else:
                        successes += 1
                        #print(successes,tens)
                else:
                    successes += 1
                    #print(successes)

    if successes < 1:
        NO_SUCCESSES=True
        
    REPLY_STRING += ". Successes: " + str(successes)

def roll_as(name):
    print("rolling as" + name)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global CRITICAL
    global HUNGER_ONE
    global HUNGER_TEN
    global ROLL_AS
    global REPLY_STRING
    global RESULTS
    global HUNRESULTS
    global FAVORITE

    if message.author == client.user:
        return

    if message.channel.name.find('vtm-under-the-bridge') != -1:
        if message.content.find('log off, Josephine') != -1:
            await message.channel.send("Hmmph! :triumph: Bye, then.")
            await client.logout()
        if message.content.startswith('_roll'):
            REPLY_STRING=""
            dicestring = message.content.partition('_roll ')[2]
            if dicestring.find(' as ') != -1:
                name = dicestring.partition(' as ')[2]
                if name in CREW_EMOJI.keys():
                   ROLL_AS += CREW_EMOJI[name]+" "
                ROLL_AS += name
                if ROLL_AS.find(FAVORITE) != -1 and random.randrange(1,4) == 2:
                    ROLL_AS += " :heart_eyes:"
                REPLY_STRING=ROLL_AS + " rolls "
                process_diceroll(dicestring.partition(' as ')[0])
                RESULTS += HUNRESULTS
                check_successes(RESULTS)

            else:
                process_diceroll(dicestring)
                RESULTS += HUNRESULTS
                check_successes(RESULTS)

            if HUNGER_TEN==True and CRITICAL==True:
                REPLY_STRING += " :smiling_imp: **MESSY CRITICAL** "

            elif NO_SUCCESSES==True and HUNGER_ONE==True: 
                REPLY_STRING += " :skull: ***bEsTIal fAiLuRe***"

            await message.channel.send(REPLY_STRING)

        if message.content.startswith('_register'):

            char_name = message.content.partition('_register ')[2]

            if message.author.nick is not None:
                if str(message.author.nick) in REGISTERED_USERS.keys():
                    del REGISTERED_USERS[message.author.nick]
                REGISTERED_USERS[message.author.nick] = str(char_name)
                await message.channel.send("Registered " + str(message.author.nick) + " as " + char_name)
            else:
                if str(message.author.name) in REGISTERED_USERS.keys():
                    del REGISTERED_USERS[message.author.name]
                del REGISTERED_USERS[message.author.name]
                REGISTERED_USERS[message.author.name] = char_name
                await message.channel.send("Registered " + str(message.author.name) + " as " + char_name)
            print(REGISTERED_USERS)

        if message.content.startswith('_unregister'):
            if message.author.nick is not None:
                del REGISTERED_USERS[message.author.nick]
                await message.channel.send("un-registered " + str(message.author.nick))
            else:
                del REGISTERED_USERS[message.author.name]
                await message.channel.send("un-registered " + str(message.author.name))
            print(REGISTERED_USERS)
        

client.run('NTg5MjEwODYwMjI4OTY4NDQ4.XQQZNA.M7yQT1DXIwpZTehqF5fPFfiOloI')
