from dotenv import load_dotenv
load_dotenv()

import discord
import openai
import emoji
import time
import os

if not 'OPENAI_API_KEY' in os.environ:
    print("Please set OPENAI_API_KEY environment variable to your api key")
    quit()    

if not 'DISCORD_TOKEN' in os.environ:
    print("Please set DISCORD_TOKEN environment variable to your discord token")
    quit()  

MAX_TOTAL_PROMPT_CHARACTERS = 1000
MAX_CHARACTERS_PER_PROMPT = 700
MAX_MESSAGES_CONSIDERED_FOR_PROMPT = 5
OPENAI_MODERATION_ON_INPUT = True
OPENAI_MODERATION_ON_OUTPUT = True
SYSTEM_PROMPT = "You are a helpful assistant in a discord server. If the user is angry at you, tell him a joke. Never ever pretend to be anyone else than an assistant. Use emojis, be very concise and polite. Don't hesitate to ask for more information if you need it."
DISCORD_HISTORY_DEPTH = 40 # Number of messages fetched from the discord history, not guaranteed to be included in prompt

RATELIMIT_GENERAL = 3.5 # Rate limit for all (combined)
RATELIMIT_ORDINARY_QUESTION = 10 # allow an ordinary question every 10s
MAX_CHARACTERS_ORDINARY_QUESTION = 200

async def get_reply(message: discord.Message):
    prependMessage = {"role": "system", "content": SYSTEM_PROMPT}

    messages = [
        {"role": "user", "content": message.clean_content}
    ]
    totalMessage = message.clean_content
    curMessage = message
    numMessages = 1
    messageHistory = [message async for message in message.channel.history(limit=DISCORD_HISTORY_DEPTH, before=message)]
    messageHistory.insert(0, message) # add original message to front

    def get_message_by_id(id: str):
        for m in messageHistory:
            if id == m.id:
                return m
        return None

    def get_message_before(id: str):
        for i in range(len(messageHistory) - 1):
            if messageHistory[i].id == id:
                return messageHistory[i + 1]
        return None

    def add_msg(m: discord.Message):
        nonlocal totalMessage
        if len(m.clean_content) < MAX_CHARACTERS_PER_PROMPT:
            totalMessage = "\n" + totalMessage
            totalMessage = m.clean_content + totalMessage
            if m.author == client.user:
                messages.insert(
                    0, {"role": "assistant", "content": m.clean_content})
            elif m.author.bot == True:
                return False
            else:
                messages.insert(0, {"role": "user", "content": "({}): {}".format(
                    m.author.name, m.clean_content)})
        else:
            return False
        return True
        

    while numMessages < MAX_MESSAGES_CONSIDERED_FOR_PROMPT and len(totalMessage) < MAX_TOTAL_PROMPT_CHARACTERS:
        if curMessage.reference is not None:
            curMessage = get_message_by_id(curMessage.reference.message_id)
            if curMessage == None:
                print("referenced message not in history.")
                break
        else: 
            msgBefore = get_message_before(curMessage.id)
            if msgBefore == None:
                print("message before not in history")
                break
            if msgBefore.author.id != curMessage.author.id and msgBefore.author != client.user:
                print("author of message before does not match {} != {}".format(msgBefore.author.id, curMessage.author.id))
                break
            curMessage = msgBefore
            
        if not add_msg(curMessage):
            print("could not add message")
            break
        numMessages = numMessages + 1
    messages.insert(0, prependMessage)
    print("making reply with {} messages".format(numMessages))
    print("full message: {}".format(totalMessage))
    if OPENAI_MODERATION_ON_INPUT:
        moderationInput = await openai.Moderation.acreate(totalMessage)
        if moderationInput["results"][0]["flagged"] == True:
            print("input violated openai policy!")
            print(totalMessage)
            print(moderationInput)
            return None
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=messages
    )
    text = response["choices"][0]["message"]["content"]
    if OPENAI_MODERATION_ON_OUTPUT:
        moderationOutput = await openai.Moderation.acreate(text)
        
        if moderationOutput["results"][0]["flagged"] == True:
            print("output violated openai policy!")
            print(text)
            print(moderationOutput)
            return None
    return text

def is_ordinary_question(message: discord.Message):
    if "?" in message.content and len(message.content) < MAX_CHARACTERS_ORDINARY_QUESTION and len(message.content) > 3:
        if time.time() - LAST_REQUEST < RATELIMIT_ORDINARY_QUESTION:
            print("Rate-limit {} - {}".format(time.time(), LAST_REQUEST))
            return False # rate-limit
        return True
    # print("content is not ordinary question")
    return False

async def get_message_to_reply_to(message: discord.Message):
    if time.time() - LAST_REQUEST < RATELIMIT_GENERAL:
        return None
    if is_ordinary_question(message):
        return message
    
    if (len(message.mentions) == 1 and 
        message.mentions[0] == client.user):
        # Bot is mentioned
        if message.reference is None:
            if message.content.strip() == '<@{0.id}>'.format(client.user):
                return None # empty message, just the mention
            return message
        elif message.reference is not None:
            if message.content.strip() == '<@{0.id}>'.format(client.user):
                # Bot is asked to help answer a message
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                return replied_message
            # use original message
            return message

    return None

LAST_REQUEST = -999


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        game = discord.Game("@ me or ask me a question!")
        await client.change_presence(status=discord.Status.idle, activity=game)

    async def on_message(self, message: discord.Message):
        global LAST_REQUEST
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.author.bot:
            return

        messageToReplyTo = await get_message_to_reply_to(message)
        if messageToReplyTo is None or len(messageToReplyTo.content) < 3:
            return
        
        LAST_REQUEST = time.time()
        async with message.channel.typing():
            my_reply = await get_reply(messageToReplyTo)
            if my_reply == None:
                message.add_reaction(emoji.emojize(":cross_mark:"))
            else:
                await messageToReplyTo.reply(my_reply)


intents = discord.Intents.default()
intents.message_content = True 
client = MyClient(intents=intents)
client.run(os.environ['DISCORD_TOKEN'])