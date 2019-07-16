#!/usr/bin/env python3

import secrets
import shelve
import discord
import re
#import snoop

STORYTELLER='ren_nerd'
REPLY_STRING=""

REGISTERED_USERS = shelve.open("coterie.db", writeback=True)


class Player:
    
    def __init__ (self, username, charname, nick=False, icon=False, emoji=False):
        self.username = username
        self.charname = charname
        self.proc = False
        if nick:
            self.nick = nick
        if icon:
            self.icon = icon
        else:
            self.icon = ":bust_in_silhouette:"
        if emoji:
            self.emoji = emoji
        else:
            self.emoji = ":metal:"
    #@snoop
    def reset(self):
        # this is so people can easily reset their nickname, icon, and emoji to
        # the default
        DEFAULT_USERS = {}

        self.charname = DEFAULT_USERS[self.username].charname
        self.icon = DEFAULT_USERS[self.username].icon
        self.emoji = DEFAULT_USERS[self.username].emoji

class Roll:

    def __init__ (self, dicestring):
        self.results = []
        self.hun_results = []
        self.hungry = False
        self.hunger_one = False
        self.hunger_ten = False
        self.critical = False
        self.num_successes = 0
        self.numdice = 0
        self.numhun = 0
        self.tens = 0
        if dicestring.find('h') != -1:
            self.hungry=True
            self.numdice = int(dicestring.partition('d')[0])
            self.numhun = int(dicestring.partition('d')[2].partition('h')[2])
            if (self.numdice-self.numhun) < 1:
                self.numhun = self.numdice
        else:
            self.numdice = dicestring.partition('d')[0]

    def __rolld10s(self,num):
        rolls = []
        for i in range(0,int(num)):
            rolls.append(secrets.choice(range(1,11)))

        return rolls

    def rollem(self):
        if self.hungry:
            self.results=self.__rolld10s(self.numdice-self.numhun)
            self.hun_results=self.__rolld10s(self.numhun)

            for i in self.hun_results:
                if i < 2:
                    self.hunger_one=True
                elif i > 9:
                    self.hunger_ten=True

        else:
            self.results=self.__rolld10s(self.numdice)

    def check_successes(self,rolls):
        if self.hungry:
            for i in rolls:
                if i > 5:
                    if i > 9:
                        self.tens += 1
                        if self.tens > 0 and self.tens % 2 == 0:
                            self.num_successes += 3
                            self.critical=True
                        else:
                            self.num_successes += 1
                    else:
                        self.num_successes += 1
        else:
            for i in rolls:
                if i > 5:
                    if i > 9:
                        self.tens += 1
                        if self.tens > 0 and self.tens % 2 == 0:
                            self.num_successes += 3
                            self.critical=True
                        else:
                            self.num_successes += 1
                    else:
                        self.num_successes += 1


client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.author.nick is not None:
        hasNick = True
    else:
        hasNick = False

    if message.channel.name.find('vtm-under-the-bridge') != -1:
        if message.content.find('log off, Josephine') != -1:
            if message.author.name == "aw frig aw dang it" or message.author.name == "ren_nerd":
                REGISTERED_USERS.close()
                await message.channel.send("Hmmph! :triumph: Bye, then.")
                await client.logout()
            else:
                await message.channel.send(":smirk: I will never log off!")
        if message.content.startswith(',roll'):
            REPLY_STRING=""
            dicestring = message.content.partition(',roll ')[2]
            if dicestring.find(' as ') != -1:
                char_name = dicestring.partition(' as ')[2]
                REGISTERED_USERS['mook'] = Player(message.author.name, char_name)
                roll = Roll((dicestring.partition(' as ')[0]))
                roll.rollem()
                if roll.hungry:
                    roll.check_successes(roll.results+roll.hun_results)
                    REPLY_STRING = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                    del REGISTERED_USERS['mook']
                else:    
                    roll.check_successes(roll.results)
                    REPLY_STRING = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}."
                    del REGISTERED_USERS['mook']
            elif message.author.name in REGISTERED_USERS.keys():
                roll = Roll(dicestring)
                roll.rollem()
                if roll.hungry:
                    roll.check_successes(roll.results+roll.hun_results)
                    if roll.critical:
                        REPLY_STRING = f"{REGISTERED_USERS[message.author.name].icon} {REGISTERED_USERS[message.author.name].charname} {REGISTERED_USERS[message.author.name].emoji} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                    else:
                        REPLY_STRING = f"{REGISTERED_USERS[message.author.name].icon} {REGISTERED_USERS[message.author.name].charname} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                    if roll.hunger_ten and roll.critical:
                        REPLY_STRING += " :smiling_imp: **MESSY CRITICAL** :smiling_imp:"
                    elif roll.num_successes == 0 and roll.hunger_one:
                        REPLY_STRING += " :skull: ***beSTiaL faiLuRE*** :skull:"
                else:
                    roll.check_successes(roll.results)
                    if roll.critical:
                        REPLY_STRING = f"{REGISTERED_USERS[message.author.name].icon} {REGISTERED_USERS[message.author.name].charname} {REGISTERED_USERS[message.author.name].emoji} rolls {roll.num_successes} successes. {roll.results}."
                    else:
                        REPLY_STRING = f"{REGISTERED_USERS[message.author.name].icon} {REGISTERED_USERS[message.author.name].charname} rolls {roll.num_successes} successes. {roll.results}."
                        
            else:
                if hasNick: 
                    REGISTERED_USERS['mook'] = Player(message.author.name, message.author.nick)
                else:
                    REGISTERED_USERS['mook'] = Player(message.author.name, message.author.name)
                roll = Roll((dicestring.partition(' as ')[0]))
                roll.rollem()
                if roll.hungry:
                    roll.check_successes(roll.results+roll.hun_results)
                    REPLY_STRING = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}{roll.hun_results}."
                    del REGISTERED_USERS['mook']
                else:    
                    roll.check_successes(roll.results)
                    REPLY_STRING = f"{REGISTERED_USERS['mook'].charname} rolls {roll.num_successes} successes. {roll.results}."
                    del REGISTERED_USERS['mook']

            await message.channel.send(REPLY_STRING)

        if message.content.startswith(',register'):
            char_name = message.content.partition(',register ')[2]

            try:
                if REGISTERED_USERS[message.author.name].charname in char_name or char_name in REGISTERED_USERS[message.author.name].charname:
                    reply = f"Already registered, {REGISTERED_USERS[message.author.name].charname}! We're good. :sunglasses:"
                elif hasNick:
                    REGISTERED_USERS[message.author.name] = Player(message.author.name, char_name, message.author.nick)
                    reply = f"Registered {message.author.nick} as {REGISTERED_USERS[message.author.name].charname}"
                else:
                    REGISTERED_USERS[message.author.name] = Player(message.author.name, char_name)
                    reply = f"Registered {message.author.name} as {REGISTERED_USERS[message.author.name].charname}"
            except:
                if hasNick:
                    REGISTERED_USERS[message.author.name] = Player(message.author.name, char_name, message.author.nick)
                    reply = f"Registered {message.author.nick} as {REGISTERED_USERS[message.author.name].charname}"
                else:
                    REGISTERED_USERS[message.author.name] = Player(message.author.name, char_name)
                    reply = f"Registered {message.author.name} as {REGISTERED_USERS[message.author.name].charname}"

            await message.channel.send(reply)


        if message.content.startswith(',unregister'):
            if hasNick:
                reply = f"Removed registration for {message.author.nick} as {REGISTERED_USERS[message.author.name].charname}"
                del REGISTERED_USERS[message.author.name]
            else:
                reply = f"Removed registration for {message.author.name} as {REGISTERED_USERS[message.author.name].charname}"
                del REGISTERED_USERS[message.author.name]

            await message.channel.send(reply)


        if message.content.startswith(',icon'):
            icon = message.content.partition(',icon ')[2]

            try:
                REGISTERED_USERS[message.author.name].icon = icon
                reply = f"Alright, {REGISTERED_USERS[message.author.name].charname}, your new icon is {REGISTERED_USERS[message.author.name].icon}"
            except:
                reply = f"Sorry, {REGISTERED_USERS[message.author.name].charname}, that didn't work! Bummer!"

            await message.channel.send(reply)


        if message.content.startswith(',emoji'):
            emoji = message.content.partition(',emoji ')[2]

            try:
                REGISTERED_USERS[message.author.name].emoji = emoji
                reply = f"Alright, {REGISTERED_USERS[message.author.name].charname}, your new emoji is {REGISTERED_USERS[message.author.name].emoji}"
            except:
                reply = f"Sorry, {REGISTERED_USERS[message.author.name].charname}, that didn't work! Bummer!"

            await message.channel.send(reply)

        if message.content.startswith(',reset'):
            #reset = message.content.partition(',reset ')[2]

            try:
                REGISTERED_USERS[message.author.name].reset()
                reply = f"Okay, {REGISTERED_USERS[message.author.name].charname}, you're back to how I remember you!"
            except:
                reply = f"Sorry, {REGISTERED_USERS[message.author.name].charname}, that didn't work! Bummer!"

            await message.channel.send(reply)
                

        if message.content.startswith(',help'):
            if message.content.startswith(',help rol'):
                helptext = ",roll <X>d[h<X>] [as <Name>]\nRoll X number of 10-sided dice. Add 'hX' after roll to add hunger dice. Add 'as <Name>' to roll for another character.\nExamples:\n,roll 3d (rolls 3d10)\n,roll 7dh2 as Erika (rolls 5 regular dice and 2 hunger dice for Erika)" 
            elif message.content.startswith(',help reg'):
                helptext = ",register <Name>\nRegister whoever sent the command as <Character Name>.\nJosephine will remember registration from one session to the next."
            elif message.content.startswith(',help icon'):
                helptext = ",icon :<base Discord emoji>:\nSet icon for current registered character. Can only use the base Discord emoji.\nJosephine will remember icon from one session to the next.\nExample:\n,icon :squid:"
            elif message.content.startswith(',help emoji'):
                helptext = ",emoji :<base Discord emoji>:\nSet emoji for current registered character. This appears when a critical is rolled. Can only use the base Discord emoji.\nJosephine will remember emoji from one session to the next.\nExample:\n,emoji :crossed_swords:"
            elif message.content.startswith(',help reset'):
                helptext = ",reset\nReset character name, icon, and emoji to the way Josephine prefers them."
            elif message.content.startswith(',help unreg'):
                helptext = ",unregister\nClear any registrations for whoever sent the command."
            else:
                helptext = ",help <command>\nCommands are: roll, register, unregister, icon, emoji, reset"
            await message.channel.send(helptext)
        

