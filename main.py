import os, json, random, threading
import discord
from discord.ext import tasks, commands
from discord import app_commands
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "World Otaku Online 🌸"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

SONDAGES = [
 {"q":"Naruto vs One Piece ?","opts":["Naruto","One Piece"]},
 {"q":"Gojo vs Sukuna ?","opts":["Gojo","Sukuna"]},
 {"q":"Meilleure waifu ?","opts":["Nezuko","Zero Two","Hinata","Mikasa"]},
]

def load_cfg():
 try:
  with open("sondage_config.json","r") as f: return json.load(f)
 except: return {}
def save_cfg(d):
 with open("sondage_config.json","w") as f: json.dump(d,f)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(hours=3)
async def sondage_auto():
 cfg=load_cfg()
 cid=cfg.get("channel_id")
 if not cid: return
 ch=bot.get_channel(cid)
 if not ch: return
 poll=random.choice(SONDAGES)
 embed=discord.Embed(title="📊 Sondage World Otaku 🌸", description=f"**{poll['q']}**\n\n"+"\n".join([f"{i+1}️⃣ {o}" for i,o in enumerate(poll['opts'])]), color=0xFF9EB5)
 msg=await ch.send(embed=embed)
 for i in range(len(poll['opts'])): await msg.add_reaction(f"{i+1}️⃣")

@bot.event
async def on_ready():
 print(f"Connecté {bot.user}")
 try: await bot.tree.sync()
 except: pass
 if not sondage_auto.is_running(): sondage_auto.start()

@bot.tree.command(name="setsondage", description="Définir salon sondage")
@app_commands.checks.has_permissions(administrator=True)
async def setsondage(interaction: discord.Interaction, channel: discord.TextChannel):
 save_cfg({"channel_id":channel.id})
 await interaction.response.send_message(f"✅ Sondages auto dans {channel.mention} toutes les 3h !", ephemeral=True)

threading.Thread(target=run_flask).start()
bot.run(os.getenv("DISCORD_TOKEN"))
