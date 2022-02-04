"""new code"""
from nextcord.ext import commands

bot = commands.Bot(command_prefix = '!')

@bot.command(name="hi")
async def SendMessage(ctx):
    await ctx.send('Hello!')

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}')

if __name__ == '__main__':
    bot.run("PASTE YOUR TOKEN HERE")

"""new code"""