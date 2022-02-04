from nextcord.ext import commands
import requests, json, random, datetime, asyncio
from PIL import Image, ImageFont, ImageDraw
import textwrap
from nextcord import File, ButtonStyle
from nextcord.ui import Button, View

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


async def schedule_daily_message(h, m, s, msg, channelid):
	while True:
		now = datetime.datetime.now()
		# then = now+datetime.timedelta(days=1)
		then = now.replace(hour=h, minute=m, second=s)
		if then < now:
			then += datetime.timedelta(days=1)
		wait_time = (then-now).total_seconds()
		await asyncio.sleep(wait_time)

		channel = bot.get_channel(channelid)

		await channel.send(msg)
		await channel.send(random.choice(links["play"]))
		await asyncio.sleep(1)

# dog daily "good morning" 8 30

@bot.command(name="daily")
async def daily(ctx, mystr:str, hour:int, minute:int, second:int):
	print(mystr, hour, minute, second)

	if not (0 < hour < 24 and 0 <= minute <= 60 and 0 <= second < 60):
		raise commands.BadArgument()

	time = datetime.time(hour, minute, second)
	timestr = time.strftime("%I:%M:%S %p")
	await ctx.send(f"A daily message will be sent at {timestr} everyday in this channel.\nDaily message:\"{mystr}\"\nConfirm by simply saying: `yes`")

@daily.error
async def daily_error(ctx, error):
	if isinstance(error, commands.BadArgument):
		await ctx.send("""Incorrect format. Use the command this way: `dog daily "message" hour minute second`.
For example: `dog daily "good morning" 22 30 0` for a message to be sent at 10:30 everyday""")

# dog speak hello world!!

@bot.command(name='speak')
async def speak(ctx, *args):
	msg = " ".join(args)
	font = ImageFont.truetype("PatrickHand-Regular.ttf", 50)
	img = Image.open("dog.jpg")
	cx, cy = (350, 230)
	
	lines = textwrap.wrap(msg, width=20)
	print(lines)
	w, h = font.getsize(msg)
	y_offset = (len(lines)*h)/2
	y_text = cy-(h/2) - y_offset

	for line in lines:
		draw = ImageDraw.Draw(img)
		w, h = font.getsize(line)
		draw.text((cx-(w/2), y_text), line, (0, 0, 0), font=font)
		img.save("dog-edited.jpg")
		y_text += h
	
	with open("dog-edited.jpg", "rb") as f:
		img = File(f)
		await ctx.channel.send(file=img)
	

@bot.command(name='support')
async def support(ctx):
	hi = Button(label="click me", style=ButtonStyle.blurple)
	subscribe = Button(label="subscribe", url="https://www.youtube.com/channel/UCqRLiT8Kv5RVmoNtnshKZwA?sub_confirmation=1")

	async def hi_callback(interaction):
		await interaction.response.send_message("Hello!")

	hi.callback = hi_callback

	myview = View(timeout=180)
	myview.add_item(hi)
	myview.add_item(subscribe)
	
	await ctx.send("hi", view=myview)

@bot.event
async def on_ready():
	print(f"Loggined in as: {bot.user.name}")
	# await schedule_daily_message()

if __name__ == '__main__':
	bot.run("PASTE YOUR TOKEN HERE")