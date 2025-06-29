import os
import discord
from discord.ext import commands
from discord import app_commands
from myserver import server_on
import datetime
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())






@bot.event
async def on_ready():
    print("Bot online!")
    synced = await bot.tree.sync()
    print(f"{len(synced)} command(S)")


#leave join
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1383311084617732096)
    text =f"เห้ ใครกันเนี่ย"
    text2 = f"{member.mention}"
    emmbed = discord.Embed(title = "นักบินที่หลงทาง",    description=text2,
                           color = 0x886bbf)
    emmbed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    emmbed.add_field(name="JOIN DATE", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    await  channel.send(text)
    await  channel.send(embed = emmbed)
#mes
@bot.event
async  def on_member_remove(member):
    channel = bot.get_channel(1383315449009143881)
    text = f"อ่าว หายไปซะแล้ว"
    text2 = f"{member.mention}"
    emmbed = discord.Embed(title="---------", description=text2,
                           color=0x6d0707
                           )
    await  channel.send(text)
    await  channel.send(embed=emmbed)

@bot.event
async def on_message(message):
    mes = message.content
    if mes == 'MACHU':
        await message.channel.send("นายเป็นใครมาเรียกชื่อเล่นฉัน")
    elif mes == 'amate' :
        await message.channel.send("ว่าไง , " + str(message.author.name))
    await bot.process_commands(message)


@bot.command()
async def hi(ctx):
    await ctx.send("hi")




@bot.tree.command(name='hellobot',description=' replies with hello ')
async  def  hellocommand(interaction):
    await  interaction.response.send_message("hello it's me machu")






@bot.tree.command(name ='name')
@app_commands.describe(name = "What's your name ")
async def  namecommand(interaction, name:str) :
    await  interaction.response.send_message(f"Hello {name}")




@bot.tree.command(name="clear", description="delete message ")
@app_commands.describe(amount="type amount that you want to delete  (max 100)")
async def clear(interaction: discord.Interaction, amount: int):
    if amount < 1 or amount > 100 :
        await interaction.response.send_message("only 1–100", ephemeral=True)
        return
    await interaction.response.defer()
    deleted = await interaction.channel.purge(limit=amount+1)
    await interaction.followup.send(f"{len(deleted)} deleted")
    
#role give
EMOJI = "✅"
ROLE_NAME = "member"
@bot.command()
async def reactrole(ctx):
    message = await ctx.send("----------------- กด ✅ เพื่อเป็น member -----------------")
    await message.add_reaction(EMOJI)

    # เก็บ message ID เพื่อเช็กใน on_raw_reaction_add
    bot.react_message_id = message.id

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != getattr(bot, 'react_message_id', None):
        return

    if str(payload.emoji.name) == EMOJI:
        guild = bot.get_guild(payload.guild_id)
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            member = guild.get_member(payload.user_id)
            if member and not member.bot:
                await member.add_roles(role)
                print(f"Gave {role.name} to {member.name}")

#help command
@bot.tree.command(name="help", description="bot command")
async def helpcommand(interaction):
    embed1 = discord.Embed(title = "Bot Commands",    description="",
                           color = 0x886bbf,
                           timestamp=discord.utils.utcnow())
    embed1.add_field(name='/clear',value='clear message', inline=False)

    await  interaction.response.send_message(embed = embed1)


#log voice chat
vc_entry_time = {}

@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = bot.get_channel(1388826937375457322)

    # เข้าห้อง
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(
            title=f"🎧 ได้เข้าห้อง **{after.channel.name}**",
            description=f"Machu -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
            color=discord.Color.green()
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url)

        await log_channel.send(embed=embed)

    # ออกจากห้อง
    elif before.channel is not None and after.channel is None:
        join_time = vc_entry_time.pop(member.id, None)
        now = datetime.datetime.now()

        duration = ""
        if join_time:
            time_spent = now - join_time
            duration = str(time_spent).split('.')[0]  # เอาแค่ HH:MM:SS ตัด microseconds

        embed = discord.Embed(
            title=f"👋 ได้ออกจาก **{before.channel.name}**(🕒 อยู่ในห้อง **{duration}**)",
            description=f"Machu -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
            color=discord.Color.red()
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        await log_channel.send(embed=embed)

    # ย้ายห้อง
    elif before.channel != after.channel:
        # อัปเดตเวลาย้ายห้อง
        vc_entry_time[member.id] = datetime.datetime.now()
        embed = discord.Embed(
            title=f"🔄 ย้ายห้องจาก  **{before.channel.name}** ไปยัง **{after.channel.name}**",
            description=f"Machu -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
            color=discord.Color.blurple()
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        await log_channel.send(embed=embed)







server_on()

bot.run(os.getenv('TOKEN'))
