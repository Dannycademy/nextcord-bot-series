from distutils.log import debug
from matplotlib.pyplot import text
from nextcord.ext import commands
from pathvalidate import validate_symbol
import requests, json, random, datetime, asyncio
from PIL import Image, ImageFont, ImageDraw
import textwrap
from nextcord import File, ButtonStyle, Embed, Color, SelectOption, Intents, Interaction, SlashOption
from nextcord.ui import Button, View, Select

# pip install nextcord --upgrade
# reinvite bot with bot AND application.commands perm
# https://docs.nextcord.dev/en/stable/interactions.html

links = json.load(open("gifs.json"))
helpGuide = json.load(open("help.json"))

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="dog ", intents=intents)
bot.remove_command("help")

# create help embed using page number and helpGuide
def createHelpEmbed(pageNum=0, inline=False):
	pageNum = (pageNum) % len(list(helpGuide))
	pageTitle = list(helpGuide)[pageNum]
	embed=Embed(color=0x0080ff, title=pageTitle)
	for key, val in helpGuide[pageTitle].items():
		embed.add_field(name=bot.command_prefix+key, value=val, inline=inline)
		embed.set_footer(text=f"Page {pageNum+1} of {len(list(helpGuide))}")
	return embed


@bot.command(name="help")
async def Help(ctx):
	currentPage = 0

	# functionality for buttons

	async def next_callback(interaction):
		nonlocal currentPage, sent_msg
		currentPage += 1
		await sent_msg.edit(embed=createHelpEmbed(pageNum=currentPage), view=myview)

	async def previous_callback(interaction):
		nonlocal currentPage, sent_msg
		currentPage -= 1
		await sent_msg.edit(embed=createHelpEmbed(pageNum=currentPage), view=myview)
	


	# add buttons to embed

	previousButton = Button(label="<", style=ButtonStyle.blurple)
	nextButton = Button(label=">", style=ButtonStyle.blurple)
	previousButton.callback = previous_callback
	nextButton.callback =  next_callback

	myview = View(timeout=180)
	myview.add_item(previousButton)
	myview.add_item(nextButton)

	sent_msg = await ctx.send(embed=createHelpEmbed(currentPage), view=myview)


# @bot.command(name="help")
# async def Help(ctx):
# 	embed=Embed(color=0x0080ff, title="Basic Commands")
# 	embed.add_field(name="dog pic", value="get a cute doggo pic :)", inline=False)
# 	embed.add_field(name="dog gif", value="get a cute doggo gif :)", inline=False)
# 	embed.add_field(name="dog play", value="get a cute playing doggo gif :)", inline=False)
# 	embed.add_field(name="dog sleep", value="get a cute sleepy doggo gif :)", inline=False)
# 	await ctx.send(embed=embed)




# https://nextcord.readthedocs.io/en/latest/ext/commands/api.html#nextcord.ext.commands.cooldown
@commands.cooldown(1, 2, commands.BucketType.user)
@bot.command(name="hi")
async def SendMessage(ctx):

	async def dropdown_callback(interaction):
		for value in dropdown.values:
			await ctx.send(random.choice(links[value]))
	
	option1 = SelectOption(label="chill", value="gif", description="doggo is lonely", emoji="😎")
	option2 = SelectOption(label="play", value="play", description="doggo is bored", emoji="🙂")
	option3 = SelectOption(label="feed", value="feed", description="doggo is hungry", emoji="😋")
	dropdown = Select(placeholder="What would you like to do with doggo?", options=[option1, option2, option3], max_values=3)
	dropdown.callback = dropdown_callback
	myview = View(timeout=180)
	myview.add_item(dropdown)

	await ctx.send('Hello! Are you bored?', view=myview)

@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command(name="pic")
async def Dog(ctx):
	response = requests.get("https://dog.ceo/api/breeds/image/random")
	image_link = response.json()["message"]
	await ctx.send(image_link)

@commands.cooldown(1, 3, commands.BucketType.user)
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

@commands.cooldown(1, 20, commands.BucketType.user)
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

# @bot.command(name='hi')
# async def hi(ctx, *args):
	
# 	hi = Button(style=ButtonStyle.primary, label="hi")
# 	bye = Button(style=ButtonStyle.danger, label="bye")
# 	sub = Button(style=ButtonStyle.primary, label="sub!!", url="https://www.youtube.com/channel/UCqRLiT8Kv5RVmoNtnshKZwA?sub_confirmation=1")


# 	async def hi_callback(interaction):
# 		await interaction.response.send_message("Hello!!")
# 	async def bye_callback(interaction):
# 		await interaction.response.send_message("Bye :(")
	
# 	hi.callback = hi_callback
# 	bye.callback = bye_callback

# 	myview = View(timeout=180)
# 	for interaction in [sub, hi, bye]:
# 		myview.add_item(interaction)

# 	await ctx.send(f"hi {ctx.message.author.mention}", view=myview)


@bot.command(name='support')
async def support(ctx, *args):
	hi = Button(label="click me", style=ButtonStyle.blurple)

	async def hi_callback(interaction):
		await interaction.response.send_message("Hello!!")
	
	hi.callback = hi_callback

	myview = View(timeout=180)
	myview.add_item(hi)

	await ctx.send(f"hi {ctx.message.author.mention}", view=myview)

# @commands.cooldown(1, 5, commands.BucketType.user)
# @bot.command(name='speak')
@bot.slash_command(guild_ids=[910701806231904297])
async def speak(interaction: Interaction, msg:str, fontSize: int = SlashOption(
        name="picker",
        choices={"30pt": 30, "50pt": 50, "70pt": 70},
    )):
	# msg = " ".join(args)

	font = ImageFont.truetype("PatrickHand-Regular.ttf", fontSize)
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
		# await ctx.channel.send(file=img)
		# ephermal to hide msg
		await interaction.response.send_message(file=img, ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandOnCooldown):
		em = Embed(title=f"Slow it down bro!",description=f"Try again in {error.retry_after:.2f}s.", color=Color.red())
		await ctx.send(embed=em)
	else:
		print(error)

@bot.event
async def on_ready():
	print(f"Loggined in as: {bot.user.name}")
	# await schedule_daily_message()

if __name__ == '__main__':
	bot.run("PASTE YOUR TOKEN HERE")