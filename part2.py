from nextcord.ext import commands
import requests, json, random

links = json.load(open("gifs.json"))

bot = commands.Bot(command_prefix="dog ")

@bot.command(name="hi")
async def SendMessage(ctx):
	await ctx.send('Hello!')

@bot.command(name="pic")
async def Dog(ctx):
	response = requests.get("https://dog.ceo/api/breeds/image")
	image_link = response.json()["message"]
	await ctx.send(image_link)

@bot.command(name="gif", aliases=["feed", "play", "sleep"])
async def Gif(ctx):
	await ctx.send(random.choice(links[ctx.invoked_with]))

@bot.event
async def on_ready():
	print(f"Loggined in as: {bot.user.name}")

if __name__ == '__main__':
	bot.run("PASTE YOUR TOKEN HERE")