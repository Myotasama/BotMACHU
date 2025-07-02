import os
import discord
from discord.ext import commands,tasks
from discord import app_commands
from myserver import server_on
import datetime
import json
from itertools import cycle
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

#botstatus
status = cycle(["KIRA KIRA" ," build by myota "])
@tasks.loop(seconds=5)
async def botstatus():
    await bot.change_presence(activity=discord.Game(next(status)))


@bot.event
async def on_ready():
    botstatus.start()
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


# Load data
VC_DATA_FILE = "vc_data.json"

def load_vc_data():
    if not os.path.exists(VC_DATA_FILE):
        return {}
    with open(VC_DATA_FILE, "r") as f:
        return json.load(f)

def save_vc_data(data):
    with open(VC_DATA_FILE, "w") as f:
        json.dump(data, f)


vc_entry_time = {}



@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = bot.get_channel(1388826937375457322)

    # เข้าห้อง
    if before.channel is None and after.channel is not None:
         vc_entry_time[member.id] = datetime.datetime.now()
         embed2 = discord.Embed(
            title=f"🎧 ได้เข้าห้อง **{after.channel.name}**",
            description=f"Machu -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
            color=discord.Color.green()
         )
         embed2.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url)

         await log_channel.send(embed=embed2)

    # ออกจากห้อง
    elif before.channel is not None and after.channel is None:
        join_time = vc_entry_time.pop(member.id, None)
        now = datetime.datetime.now()

        duration = ""

        user_id = str(member.id)
        vc_data = load_vc_data()

        if join_time:
            spent_sec = int((now - join_time).total_seconds())
            vc_data[user_id] = vc_data.get(user_id, 0) + spent_sec
            save_vc_data(vc_data)  # เอาแค่ HH:MM:SS ตัด microseconds + save data

        embed2 = discord.Embed(
            title=f"👋 ได้ออกจาก **{before.channel.name}**(🕒 อยู่ในห้อง **{duration}**)",
            description=f"Machu -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
            color=discord.Color.red()
        )
        embed2.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        await log_channel.send(embed=embed2)

    # ย้ายห้อง
    elif before.channel != after.channel:
        # อัปเดตเวลาย้ายห้อง
        vc_entry_time[member.id] = datetime.datetime.now()
        embed2 = discord.Embed(
            title=f"🔄 ย้ายห้องจาก  **{before.channel.name}** ไปยัง **{after.channel.name}**",
            description=f"Machu -- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ",
            color=discord.Color.blurple()
        )
        embed2.set_author(
            name=member.display_name,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        await log_channel.send(embed=embed2)

#vcstats
@bot.tree.command(name="vcstats", description="ดูเวลาที่คุณใช้ใน VC ทั้งหมด")
async def vcstats(interaction: discord.Interaction):
    vc_data = load_vc_data()
    user_id = str(interaction.user.id)
    total_sec = vc_data.get(user_id, 0)

    duration = str(datetime.timedelta(seconds=total_sec))

    embed = discord.Embed(
        title="📊 VC Statistics",
        description=f"คุณใช้เวลาใน Voice Channel ไปแล้วทั้งหมด: **{duration}**",
        color=discord.Color.blue()
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    )
    await interaction.response.send_message(embed=embed)







server_on()

bot.run(os.getenv('TOKEN'))
