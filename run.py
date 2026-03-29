import discord
from discord import app_commands
from discord.ext import commands
import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "welcome_channel": {},
            "goodbye_channel": {},
            "admin_role_id": None
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        print("สร้าง config.json ให้แล้ว")
        return default

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config():
    data = {
        "welcome_channel": WELCOME_CHANNELS,
        "goodbye_channel": GOODBYE_CHANNELS,
        "admin_role_id": ADMIN_ROLE_ID
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

config = load_config()

# ✅ ใช้ TOKEN จาก Render เท่านั้น
BOT_TOKEN = os.getenv("BOT_TOKEN")

WELCOME_CHANNELS = config.get("welcome_channel", {})
GOODBYE_CHANNELS = config.get("goodbye_channel", {})
ADMIN_ROLE_ID = config.get("admin_role_id")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
# Utility
# ============================================================
def is_admin(interaction: discord.Interaction) -> bool:
    if ADMIN_ROLE_ID:
        role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if role and role in interaction.user.roles:
            return True
    return interaction.user.guild_permissions.administrator

# ============================================================
# Welcome / Goodbye
# ============================================================
async def send_welcome(member: discord.Member):
    ch_id = WELCOME_CHANNELS.get(str(member.guild.id))
    if not ch_id:
        return
    channel = member.guild.get_channel(ch_id)
    if not channel:
        return

    embed = discord.Embed(
        title=f"☕ Welcome {member.display_name} to the cafe!",
        description="ยินดีต้อนรับสู่ร้านกาแฟของเรา ☕",
        color=0x00FF00,
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    try:
        await channel.send(embed=embed)
    except:
        pass

async def send_goodbye(member: discord.Member):
    ch_id = GOODBYE_CHANNELS.get(str(member.guild.id))
    if not ch_id:
        return
    channel = member.guild.get_channel(ch_id)
    if not channel:
        return

    embed = discord.Embed(
        title=f"🍂 {member.display_name} ออกจากร้านแล้ว",
        description="แล้วพบกันใหม่ ☕",
        color=0xB39694,
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    try:
        await channel.send(embed=embed)
    except:
        pass

# ============================================================
# Events
# ============================================================
@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Sync สำเร็จ {len(synced)} คำสั่ง")
    except Exception as e:
        print(f"❌ Sync ล้มเหลว: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    await send_welcome(member)

@bot.event
async def on_member_remove(member: discord.Member):
    await send_goodbye(member)

# ============================================================
# Commands
# ============================================================
@bot.tree.command(name="setwelcomechannel", description="ตั้งช่องต้อนรับ")
@app_commands.describe(channel="เลือกช่อง")
async def setwelcomechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

    WELCOME_CHANNELS[str(interaction.guild.id)] = channel.id
    save_config()
    await interaction.response.send_message("✅ ตั้งค่าช่องต้อนรับแล้ว", ephemeral=True)

@bot.tree.command(name="setgoodbyechannel", description="ตั้งช่องลา")
@app_commands.describe(channel="เลือกช่อง")
async def setgoodbyechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

    GOODBYE_CHANNELS[str(interaction.guild.id)] = channel.id
    save_config()
    await interaction.response.send_message("✅ ตั้งค่าช่องลาแล้ว", ephemeral=True)

# ❌ ปิดระบบ voice เพราะ Render ใช้ไม่ได้
@bot.tree.command(name="joinvc", description="เข้าห้องเสียง (ใช้ไม่ได้บนโฮสต์นี้)")
async def joinvc(interaction: discord.Interaction):
    await interaction.response.send_message("❌ โฮสต์นี้ไม่รองรับ Voice", ephemeral=True)

@bot.tree.command(name="leavevc", description="ออกห้องเสียง (ใช้ไม่ได้บนโฮสต์นี้)")
async def leavevc(interaction: discord.Interaction):
    await interaction.response.send_message("❌ โฮสต์นี้ไม่รองรับ Voice", ephemeral=True)

# ============================================================
# Run Bot
# ============================================================
if not BOT_TOKEN:
    print("❌ กรุณาใส่ BOT_TOKEN ใน Render")
    exit()

bot.run(BOT_TOKEN)
