from nextcord.ext import commands
import requests, json, random, datetime, asyncio

links = json.load(open("gifs.json"))

bot = commands.Bot(command_prefix="dog ")

@bot.command(name="hi")
async def SendMessage(ctx):
	await ctx.send('Hello!')

@bot.command(name="pic")
async def Dog(ctx):
	response = requests.get("https://dog.ceo/api/breeds/image/random")
	image_link = response.json()["message"]
	await ctx.send(image_link)

@bot.command(name="gif", aliases=["feed", "play", "sleep"])
async def Gif(ctx):
	await ctx.send(random.choice(links[ctx.invoked_with]))

async def schedule_daily_message():
	while True:
		now = datetime.datetime.now()
		then = now+datetime.timedelta(days=1)
		# then = now.replace(hour=22, minute=31)
		wait_time = (then-now).total_seconds()
		await asyncio.sleep(wait_time)

		channel = bot.get_channel(919372924538986576)

		await channel.send("Good morning!!")
		await channel.send(random.choice(links["play"]))

@bot.event
async def on_ready():
	print(f"Loggined in as: {bot.user.name}")
	await schedule_daily_message()

if __name__ == '__main__':
	bot.run("PASTE YOUR TOKEN HERE")