from distutils.log import debug, error
from matplotlib import image
from matplotlib.pyplot import text
from nextcord.ext import commands
from pathvalidate import validate_symbol
import requests
import json
import random
import datetime
import asyncio
from PIL import Image, ImageFont, ImageDraw
import textwrap
from nextcord import File, ButtonStyle, Embed, Color, SelectOption, Intents, Interaction, SlashOption, Member
from nextcord.ui import Button, View, Select
import nextcord
from gtts import gTTS
import pyttsx3

# engine = pyttsx3.init('sapi5')
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)
# engine.setProperty('rate', 130)


# pip install nextcord --upgrade
# reinvite bot with bot AND application.commands perm
# https://docs.nextcord.dev/en/stable/interactions.html

links = json.load(open("gifs.json"))
helpGuide = json.load(open("help.json"))

intents = Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="dog ", intents=intents)
bot.remove_command("help")

# create help embed using page number and helpGuide


def createHelpEmbed(pageNum=0, inline=False):
    pageNum = (pageNum) % len(list(helpGuide))
    pageTitle = list(helpGuide)[pageNum]
    embed = Embed(color=0x0080ff, title=pageTitle)
    for key, val in helpGuide[pageTitle].items():
        embed.add_field(name=bot.command_prefix+key, value=val, inline=inline)
        embed.set_footer(text=f"Page {pageNum+1} of {len(list(helpGuide))}")
    return embed


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = Embed(title=f"Slow it down bro!",
                   description=f"Try again in {error.retry_after:.2f}s.", color=Color.red())
        await ctx.send(embed=em)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the permissions to do that!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found.")
    else:
        print(type(error))
        print(error)

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def Ban(ctx, user: Member, reason=None, delete_message_days=1):
    await ctx.message.author.guild.ban(user, reason=reason, delete_message_days=delete_message_days)
    embed = Embed(title="successfully banned user", color=nextcord.Color.red())
    embedData = {
		"Member": user.mention,
		"Reason for ban": reason,
		"Days of messages deleted" : delete_message_days
    }
    for [fieldName, fieldVal] in embedData.items():
        embed.add_field(name=fieldName+":", value=fieldVal, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def Unban(ctx, userId: int, reason=None):
    user = await bot.fetch_user(userId)
    await ctx.message.author.guild.unban(user, reason=reason)
    embed = Embed(title="successfully unbanned user", color=nextcord.Color.green())
    embedData = {
		"Member": user.mention,
		"Reason for unban": reason,
    }
    for [fieldName, fieldVal] in embedData.items():
        embed.add_field(name=fieldName+":", value=fieldVal, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="kick")
@commands.has_permissions(ban_members=True)
async def Kick(ctx, user: Member, reason=None):
    await ctx.message.author.guild.kick(user, reason=reason)
    embed = Embed(title="successfully kicked user", color=nextcord.Color.red())
    embedData = {
		"Member": user.mention,
		"Reason for ban": reason,
    }
    for [fieldName, fieldVal] in embedData.items():
        embed.add_field(name=fieldName+":", value=fieldVal, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="profile")
async def Profile(ctx, user: Member = None):
    if user == None:
        user = ctx.message.author
    inline = True
    embed = Embed(title=user.name+"#"+user.discriminator, color=0x0080ff)
    userData = {
        "Mention": user.mention,
        "Nick": user.nick,
        "Created at": user.created_at.strftime("%b %d, %Y, %T"),
        "Joined at": user.joined_at.strftime("%b %d, %Y, %T"),
        "Server": user.guild,
        "Top role": user.top_role
    }
    for [fieldName, fieldVal] in userData.items():
        embed.add_field(name=fieldName+":", value=fieldVal, inline=inline)
    embed.set_footer(text=f"id: {user.id}")

    embed.set_thumbnail(user.display_avatar)
    await ctx.send(embed=embed)

    # for server
    # descriptionIn embeds.0.thumbnail.url: Scheme "none" is not supported. Scheme must be one of ('http', 'https').
    # member count
    # online count
    # icon
    # owner name
    # created at


@bot.command(name="server", pass_context=True)
async def Server(ctx):
    guild = ctx.message.author.guild
    inline = True
    embed = Embed(title=guild.name, color=0x0080ff)
    userData = {
        "Owner": guild.owner.mention,
        "Channels": len(guild.channels),
        "Members": guild.member_count,
        "Created at": guild.created_at.strftime("%b %d, %Y, %T"),
        "Description": guild.description,
        # "Active" : guild.presence_count,
    }
    for [fieldName, fieldVal] in userData.items():
        embed.add_field(name=fieldName+":", value=fieldVal, inline=inline)
    embed.set_footer(text=f"id: {guild.id}")

    embed.set_thumbnail(guild.icon)
    await ctx.send(embed=embed)


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
    nextButton.callback = next_callback

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

    option1 = SelectOption(label="chill", value="gif",
                           description="doggo is lonely", emoji="😎")
    option2 = SelectOption(label="play", value="play",
                           description="doggo is bored", emoji="🙂")
    option3 = SelectOption(label="feed", value="feed",
                           description="doggo is hungry", emoji="😋")
    dropdown = Select(placeholder="What would you like to do with doggo?", options=[
                      option1, option2, option3], max_values=3)
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
async def daily(ctx, mystr: str, hour: int, minute: int, second: int):
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



# @bot.slash_command(guild_ids=[910701806231904297])
# async def speak(interaction: Interaction, msg: str, fontSize: int = SlashOption(
#     name="picker",
#     choices={"30pt": 30, "50pt": 50, "70pt": 70},
# )):
@commands.cooldown(1, 5, commands.BucketType.user)
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
        # ephermal to hide msg
        # await interaction.response.send_message(file=img, ephemeral=True)



@bot.command(name='leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send("👋")

@bot.command(name='stop')
async def leave(ctx):
    user = ctx.message.author
    if user.voice != None:
        try:
            vc = ctx.voice_client
        except:
            await ctx.send("there is nothing to stop")
        if vc != None and vc.is_playing():
            vc.stop()
            await ctx.send("stopped")
        else:
            await ctx.send("there is nothing to stop")

@bot.command(name='join')
async def stop(ctx):
    user = ctx.message.author
    if user.voice != None:
        try:
            await user.voice.channel.connect()
        except:
            await ctx.send("I'm already in the vc!")
    else:
        await ctx.send('You need to be in a vc to run this command!')

@bot.command(name='bark')
async def bark(ctx):
    user = ctx.message.author
    if user.voice != None:
        try:
            vc = await user.voice.channel.connect()
        except:
            vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        source = await nextcord.FFmpegOpusAudio.from_probe("dog-bark.mp3", method='fallback')
        vc.play(source)
    else:
        await ctx.send('You need to be in a vc to run this command!')


@bot.command(name='tts')
async def tts(ctx, *args):
    text = " ".join(args)
    user = ctx.message.author
    if user.voice != None:
        try:
            vc = await user.voice.channel.connect()
        except:
            vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()

        myobj = gTTS(text=text, lang="en", slow=False)
        myobj.save("tts-audio.mp3")

        source = await nextcord.FFmpegOpusAudio.from_probe("tts-audio.mp3", method='fallback')
        vc.play(source)
    else:
        await ctx.send('You need to be in a vc to run this command!')

@bot.event
async def on_ready():
    print(f"Loggined in as: {bot.user.name}")

if __name__ == '__main__':
    bot.run("PASTE YOUR TOKEN HERE")
