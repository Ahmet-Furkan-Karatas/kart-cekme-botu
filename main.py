import discord
from discord.ext import commands
import logic
import config  
import sqlite3

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

db = logic.DB_Manager(config.DATABASE)

def kart_nadirlik(overall):
    overall = int(overall)
    if overall >= 85:
        return "Altın ⭐⭐⭐"
    elif 75 <= overall < 85:
        return "Gümüş ⭐⭐"
    else:
        return "Bronz ⭐"

@bot.command()
async def kart_çek(ctx):
    conn = sqlite3.connect("football.db")
    cursor = conn.cursor()

    cursor.execute("SELECT Name, Overall, Club, Nationality, Photo, Value FROM data ORDER BY RANDOM() LIMIT 1")
    oyuncu = cursor.fetchone()
    conn.close()

    if not oyuncu:
        await ctx.send("❌ Oyuncu verisi bulunamadı. Veritabanını kontrol et!")
        return

    name, overall, club, nationality, photo, value = oyuncu
    rarity = kart_nadirlik(overall)

    db.kullanici_ekle(ctx.author.id, ctx.author.name)

    db.kullanici_puan_guncelle(ctx.author.id, int(overall))

    db.kart_ekle(ctx.author.id, name, overall, club, nationality, rarity, photo)

    embed = discord.Embed(title=f"{name}", color=discord.Color.blue())
    embed.add_field(name="Rating", value=overall, inline=False)
    embed.add_field(name="Kulüp", value=club, inline=False)
    embed.add_field(name="Milli Takım", value=nationality, inline=False)
    embed.add_field(name="Nadirliği", value=rarity, inline=False)
    embed.add_field(name="Piyasa Değeri", value=value, inline=False)

    if photo:
        embed.set_thumbnail(url=photo)

    await ctx.send(embed=embed)

@bot.command()
async def kartlarım(ctx):
    kartlar = db.kullanici_kartlari(ctx.author.id)

    if not kartlar:
        await ctx.send("Henüz kartınız yok!")
        return

    mesaj = "Kartlarınız:\n"
    for kart_name, overall, rarity in kartlar:
        mesaj += f"{kart_name} - {overall} - {rarity}\n"

    await ctx.send(mesaj)

@bot.command()
async def liderlik(ctx):
    liderler = db.liderlik_siralamasi()

    if not liderler:
        await ctx.send("Henüz liderlik sıralaması bulunmamaktadır.")
        return

    mesaj = "**Liderlik Sıralaması:**\n"
    for i, (user_id, puan) in enumerate(liderler, start=1):
        user = await bot.fetch_user(user_id)
        mesaj += f"{i}. {user.name} - Puan: {puan}\n"

    await ctx.send(mesaj)

bot.run(config.TOKEN)
