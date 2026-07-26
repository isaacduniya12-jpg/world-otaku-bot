import discord
from discord.ext import commands
from discord import app_commands
import os
import aiohttp

# --- BOT ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commandes slash synchronisées")
    except Exception as e:
        print(f"Erreur sync: {e}")

# --- COMMANDE /anime ---
@bot.tree.command(name="anime", description="Cherche un anime et donne ses infos")
@app_commands.describe(nom="Nom de l'anime à chercher")
async def anime(interaction: discord.Interaction, nom: str):
    await interaction.response.defer()

    url = f"https://api.jikan.moe/v4/anime?q={nom}&limit=1&sfw=true"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    if not data['data']:
        await interaction.followup.send(f"Aucun anime trouvé pour **{nom}** 😭")
        return

    anime_data = data['data'][0]

    embed = discord.Embed(
        title=anime_data['title'],
        description=anime_data['synopsis'][:400] + "..." if len(anime_data['synopsis']) > 400 else anime_data['synopsis'],
        color=discord.Color.purple(),
        url=anime_data['url']
    )
    embed.add_field(name="⭐ Score", value=f"{anime_data['score']} / 10", inline=True)
    embed.add_field(name="📺 Épisodes", value=anime_data['episodes'], inline=True)
    embed.add_field(name="📅 Statut", value=anime_data['status'], inline=True)
    embed.set_image(url=anime_data['images']['jpg']['large_image_url'])
    embed.set_footer(text=f"Type: {anime_data['type']} | Source: MyAnimeList")

    await interaction.followup.send(embed=embed)

# --- LANCEMENT ---
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
