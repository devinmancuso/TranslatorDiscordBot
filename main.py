import os
import requests
import emoji
import csv
import discord
from keep_alive import keep_alive
from discord.ext import commands
from datetime import datetime, timedelta

# Set intents - see: https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(
	command_prefix="!",  # Change to desired prefix
	case_insensitive=True,  # Commands aren't case-sensitive
	intents=intents		# "Import" the intents
)

bot.author_id = 1027106760386949190

def log(user, server, channel, source_lang, target_lang, translateMe, result):
	with open('./log.csv', 'a', encoding='UTF8', newline='') as f:
		now = datetime.now() - timedelta(hours=5)
		now = now.strftime("%Y-%m-%d %H:%M:%S")
		row = [now, user, server, channel, source_lang, target_lang, translateMe, result]
		writer = csv.writer(f)
		writer.writerow(row)

@bot.event 
async def on_ready():  # When the bot is ready
    print("Bot connected!")
    print(bot.user)  # Prints the bot's username and ID

@bot.command(name="translate", aliases=["tl"])
async def translate(ctx,*args):
	'''Translates JP -> EN, and vice-versa.\n
	Reply to a message you wish to translate with: !translate\n
	Or, enter: !translate [Sentence to be translated]'''

	channel = ctx.channel.name
	server = ctx.guild.name
	user = ctx.author
	
	translateMe = ""
	for arg in args: translateMe += arg + " "

	#print('{} from {} server in {} channel sent {}'.format(user, server, channel, translateMe))
	
	print("Translation request: ", translateMe)
	if translateMe == "": # If no args, get the msg this command replied to
		translateMe = await ctx.channel.fetch_message(ctx.message.reference.message_id)
		translateMe = translateMe.content
	if(emoji.demojize(translateMe).isascii()): # Text is EN if all chars (excl emoji) are ascii
		source_lang = 'EN'
		target_lang = 'JA'
	else: # Else, text is JA
		source_lang = 'JA'
		target_lang = 'EN'
	url = "https://api-free.deepl.com/v2/translate?auth_key={}".format(os.getenv('DEEPL_API_KEY'))
	headers = {'text' : translateMe, 'source_lang' : source_lang, 'target_lang' : target_lang}
	response = requests.get(url, headers)
	responseJSON = response.json()
	try:
		print('response: 👉️', responseJSON)  # response: 👉️ <Response [204]>
		result = responseJSON['translations'][0]['text']
		print("Translated output: ", result)
		await ctx.reply(result)
		log(user, server, channel, source_lang, target_lang, translateMe, result)
	except:
		errMsg = "Translation failed. Error code: {}".format(response.status_code)
		print("Error: ", errMsg)
		await ctx.reply(errMsg)
		log(user, server, channel, source_lang, target_lang, translateMe, errMsg)

keep_alive()  # Starts a webserver to be pinged.
token = os.environ['DISCORD_BOT_SECRET']
try:
	print("attempting to run bot")
	bot.run(token)  # Starts the bot
except Exception as e:
	print("Bot unable to start")
	print(e.__class__)
	if bot.is_ws_ratelimited():
		print("Rate Limited, Unable to start")