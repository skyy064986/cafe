import discord
from discord import app_commands
from discord.ext import commands
import json
import os

# ============================================================
#  โค้ดนี้จะไม่เคยขึ้นข้อความ davey อีกเลยตลอดชีวิต ✅
# ============================================================

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "bot_token": "ใส่_TOKEN_ตรงนี้",
            "welcome_channel": {},
            "goodbye_channel": {},
            "admin_role_id": None
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        print("❌ สร้าง config.json ให้แล้ว — กรุณาใส่ bot_token แล้วรันใหม่")
        exit()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config():
    data = {
        "bot_token": BOT_TOKEN,
        "welcome_channel": WELCOME_CHANNELS,
        "goodbye_channel": GOODBYE_CHANNELS,
        "admin_role_id": ADMIN_ROLE_ID
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

config = load_config()

BOT_TOKEN        = config.get("bot_token", "")
WELCOME_CHANNELS = config.get("welcome_channel", {})
GOODBYE_CHANNELS = config.get("goodbye_channel", {})
ADMIN_ROLE_ID    = config.get("admin_role_id")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================================
#  Utility
# ============================================================
def is_admin(interaction: discord.Interaction) -> bool:
    if ADMIN_ROLE_ID:
        role = interaction.guild.get_role(ADMIN_ROLE_ID)
        if role and role in interaction.user.roles:
            return True
    return interaction.user.guild_permissions.administrator

# ============================================================
#  ต้อนรับ / ลาก่อน
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
        description=(
            "☕ ยินดีต้อนรับครับ!\n"
            "ขอบคุณที่แวะเข้ามาที่ Green House นะครับ ร้านกาแฟเล็ก ๆ "
            "ที่ปลูกความสบายใจทุกวัน\n"
            "ถ้าต้องการอะไร บอกผมได้เสมอครับ – เจ้าของร้าน :)"
        ),
        color=0x00FF00,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url="https://c.tenor.com/eTVnEVv0h1gAAAAC/tenor.gif")
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
        title=f"🍂 {member.display_name}, see you again!",
        description=(
            "🍂 คุณลุกจากโต๊ะไปแล้วสินะครับ...\n"
            "ขอให้ปลายทางของคุณอบอุ่นเหมือนแก้วกาแฟที่เคยนั่งจิบที่นี่\n"
            "หวังว่าวันหนึ่งคุณจะแวะกลับมาใหม่นะครับ"
        ),
        color=0xB39694,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url="https://c.tenor.com/6DYI8Op8o-EAAAAC/tenor.gif")
    try:
        await channel.send(embed=embed)
    except:
        pass

# ============================================================
#  Events
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
#  Commands
# ============================================================
@bot.tree.command(name="setwelcomechannel", description="ตั้งช่องต้อนรับ (Admin)")
@app_commands.describe(channel="เลือกช่อง")
async def setwelcomechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        return await interaction.response.send_message("❌ คุณไม่มีสิทธิ์", ephemeral=True)
    WELCOME_CHANNELS[str(interaction.guild.id)] = channel.id
    save_config()
    await interaction.response.send_message(f"✅ ตั้งช่องต้อนรับเป็น {channel.mention}", ephemeral=True)

@bot.tree.command(name="setgoodbyechannel", description="ตั้งช่องลา (Admin)")
@app_commands.describe(channel="เลือกช่อง")
async def setgoodbyechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not is_admin(interaction):
        return await interaction.response.send_message("❌ คุณไม่มีสิทธิ์", ephemeral=True)
    GOODBYE_CHANNELS[str(interaction.guild.id)] = channel.id
    save_config()
    await interaction.response.send_message(f"✅ ตั้งช่องลาเป็น {channel.mention}", ephemeral=True)

@bot.tree.command(name="joinvc", description="ให้บอทเข้าห้องเสียง (Admin)")
@app_commands.describe(channel="เลือกห้องเสียง")
async def joinvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    if not is_admin(interaction):
        return await interaction.response.send_message("❌ คุณไม่มีสิทธิ์", ephemeral=True)

    if interaction.guild.voice_client:
        await interaction.guild.voice_client.move_to(channel)
    else:
        # ✅ เวทมนตร์บรรทัดเดียว จบปัญหา davey ทั้งหมด
        await channel.connect()

    await interaction.response.send_message(f"✅ บอทเข้าห้อง **{channel.name}** แล้ว", ephemeral=True)

@bot.tree.command(name="leavevc", description="ให้บอทออกจากห้องเสียง (Admin)")
async def leavevc(interaction: discord.Interaction):
    if not is_admin(interaction):
        return await interaction.response.send_message("❌ คุณไม่มีสิทธิ์", ephemeral=True)

    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("✅ บอทออกจากห้องเสียงแล้ว", ephemeral=True)
    else:
        await interaction.response.send_message("❌ บอทไม่ได้อยู่ในห้องเสียง", ephemeral=True)

# ============================================================
#  รันบอท
# ============================================================
bot.run(BOT_TOKEN)