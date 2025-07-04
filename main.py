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
status = cycle(["KIRA KIRA" ,'ต้องได้เจอกันแน่ๆ "กันดั้มบอกแบบนั้น"'])
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
    emmbed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    emmbed.add_field(name="LEFT DATE", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

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
@app_commands.checks.has_permissions(manage_messages=True) 
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
    embed1.add_field(name='/clear',value='clear message',inline=True)
    embed1.add_field(name='/vcstats',value='check vc statics',inline=True)
    embed1.add_field(name='/vcranking',value='vc leaderboard',inline=True)
    embed1.add_field(name='/studylog_start',value='start record studytimes',inline=False)
    embed1.add_field(name='/studylog_stop',value='stop record studytimes',inline=True)
    embed1.add_field(name='/studylog_stats',value='check studytimes',inline=True)
    embed1.add_field(name='/studylog_reset',value='reset studytimes',inline=False)
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

          user_id = str(member.id)
          vc_data = load_vc_data()

          if join_time:
              spent_sec = int((now - join_time).total_seconds())
              formatted_duration = str(datetime.timedelta(seconds=spent_sec))  # ✅ Fix here
              
              vc_data[user_id] = vc_data.get(user_id, 0) + spent_sec
              save_vc_data(vc_data)
          else:
              formatted_duration = "ไม่สามารถคำนวณได้"
          embed2 = discord.Embed(
              title=f"👋 ได้ออกจาก **{before.channel.name}** (🕒 อยู่ในห้อง **{formatted_duration}**)",  description=f"Machu -- {now.strftime('%Y-%m-%d %H:%M:%S')}",  color=discord.Color.red()
          )
         
    embed2.set_author(
        name=member.display_name,
        icon_url=member.avatar.url if member.avatar else member.default_avatar.url
    )
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

#vcranking
@bot.tree.command(name="vcranking", description="ดูอันดับคนที่อยู่ใน VC นานที่สุด")
async def vcranking(interaction: discord.Interaction):
    vc_data = load_vc_data()

    if not vc_data:
        await interaction.response.send_message("❌ ยังไม่มีข้อมูลการเข้า VC", ephemeral=True)
        return

    top_users = sorted(vc_data.items(), key=lambda x: x[1], reverse=True)[:10] # นำข้อมูลจาก vc_data (dict) มาจัดเรียงแบบ list , x[1] ค่าจำนวนวินาทีที่ใช้ใน VC ,reverse=True เรียงจากมากไปน้อย, [:10] เอาแค่ 10 อันดับแรก

    lines = []
    for i, (user_id, total_sec) in enumerate(top_users, start=1):
        user = await interaction.guild.fetch_member(int(user_id)) #ดึงสมาชิก (Member object) จาก ID , ใช้ fetch_member() เพื่อให้ได้ user แม้จะไม่อยู่ในแคช
        time_str = str(datetime.timedelta(seconds=total_sec))
        lines.append(f"`#{i}` {user.display_name} — **{time_str}**")

    embed = discord.Embed(
        title="🏆 VC Leaderboard",
        description="\n".join(lines),
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)
    
studylog_file = "studylog.json"
study_sessions = {}  # user_id: datetime when started

# โหลดข้อมูล
def load_studylog():
    if not os.path.exists(studylog_file):
        return {}
    with open(studylog_file, "r") as f:
        return json.load(f)

# บันทึกข้อมูล
def save_studylog(data):
    with open(studylog_file, "w") as f:
        json.dump(data, f)

# เริ่มเรียน
@bot.tree.command(name="studylog_start", description="เริ่มจับเวลาเรียน")
async def studylog_start(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id in study_sessions:
        await interaction.response.send_message("⏳ คุณกำลังเรียนอยู่แล้ว!", ephemeral=True)
        return

    study_sessions[user_id] = datetime.datetime.now()
    await interaction.response.send_message("🟢 เริ่มจับเวลาเรียนแล้ว!")

# หยุดจับเวลา
@bot.tree.command(name="studylog_stop", description="หยุดและบันทึกเวลาเรียน")
async def studylog_stop(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in study_sessions:
        await interaction.response.send_message("❌ คุณยังไม่ได้เริ่มเรียน!", ephemeral=True)
        return

    start_time = study_sessions.pop(user_id)
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    data = load_studylog()
    data[user_id] = data.get(user_id, 0) + int(duration)
    save_studylog(data)

    formatted = str(datetime.timedelta(seconds=int(duration)))
    await interaction.response.send_message(f"✅ คุณเรียนไปทั้งหมด: `{formatted}`")

# ดูเวลาสะสม
@bot.tree.command(name="studylog_stats", description="ดูเวลาที่คุณเคยเรียนทั้งหมด")
async def studylog_stats(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_studylog()
    total_seconds = data.get(user_id, 0)
    formatted = str(datetime.timedelta(seconds=total_seconds))
    if user_id in study_sessions:
        await interaction.response.send_message("⏳ คุณกำลังเรียนอยู่ โปรดใช้คำสั่งหลังเรียนเสร็จแล้ว!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📚 Study Summary",
        description=f"คุณเรียนสะสมทั้งหมด: **{formatted}**",
        color=discord.Color.green()
    )
    embed.set_author(
        name=interaction.user.display_name,
        icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="studylog_reset", description="รีเซ็ตเวลาเรียนทั้งหมดของคุณ")
async def studylog_reset(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_studylog()
    if user_id in study_sessions:
        await interaction.response.send_message("⏳ คุณกำลังเรียนอยู่ โปรดใช้คำสั่งหลังเรียนเสร็จแล้ว!", ephemeral=True)
        return

    if user_id not in data:
        await interaction.response.send_message("❌ คุณยังไม่มีเวลาเรียนที่บันทึกไว้!", ephemeral=True)
        return

    data[user_id] = 0
    save_studylog(data)
    await interaction.response.send_message("🔁 เวลาที่คุณเคยเรียนทั้งหมดถูกรีเซ็ตเรียบร้อยแล้ว!")



server_on()

bot.run(os.getenv('TOKEN'))
