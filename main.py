import os, json, random, threading
import discord
from discord.ext import tasks, commands
from discord import app_commands
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "World Otaku Online 🌸"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

SONDAGES = [
  {"q":"Naruto vs One Piece?", "opts":["Naruto","One Piece"]},
  {"q":"Gojo vs Sukuna?", "opts":["Gojo","Sukuna"]},
  {"q":"Meilleure waifu?", "opts":["Nezuko","Zero Two","Hinata"]},
  {"q":"Meilleur rival?", "opts":["Sasuke","Zoro","Bakugo"]},
]

CONFIG_FILE="config.json"
def load_config():
    try:
        with open(CONFIG_FILE,"r") as f: return json.load(f)
    except: return {}
def save_config(d):
    with open(CONFIG_FILE,"w") as f: json.dump(d,f)

@bot.event
async def on_ready():
    print(f"Connecté {bot.user}")
    if not sondage_loop.is_running():
        sondage_loop.start()
    await bot.tree.sync()
    print("Sondage prêt!")

@tasks.loop(hours=3)
async def sondage_loop():
    conf=load_config()
    if not conf.get("channel"): return
    channel=bot.get_channel(conf["channel"])
    if not channel: return
    s=random.choice(SONDAGES)
    answers=[discord.PollAnswer(text=o) for o in s["opts"]]
    poll=discord.Poll(question=discord.PollQuestion(text=s["q"]), answers=answers, duration=24)
    await channel.send(poll=poll)

@bot.tree.command(name="setsondage", description="Définir où envoyer les sondages toutes les 3h")
@app_commands.checks.has_permissions(administrator=True)
async def setsondage(interaction: discord.Interaction, salon: discord.TextChannel):
    save_config({"channel": salon.id})
    await interaction.response.send_message(f"✅ Sondages activés dans {salon.mention} toutes les 3h!", ephemeral=True)

threading.Thread(target=run_flask).start()
bot.run(os.getenv("DISCORD_TOKEN"))
