import discord
import pymysql
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

# MySQL Connection setup
def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Bot event: on_ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Example command: check database connectivity
@bot.command(name="testdb")
async def test_database(ctx):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            result = cursor.fetchone()
            await ctx.send(f"MySQL version: {result['VERSION()']}")
        connection.close()
    except Exception as e:
        await ctx.send(f"Database connection failed: {e}")

# Example reservation command
@bot.command(name="reserve")
async def reserve(ctx, restaurant_name, date, time):
    user_id = ctx.author.id
    username = ctx.author.name

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Example table schema: reservations(user_id, username, restaurant, reservation_date, reservation_time)
            sql = "INSERT INTO reservations (user_id, username, restaurant, reservation_date, reservation_time) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (user_id, username, restaurant_name, date, time))
        connection.commit()
        await ctx.send(f"Reservation confirmed at **{restaurant_name}** on **{date}** at **{time}**.")
    except pymysql.MySQLError as e:
        await ctx.send(f"Error: {e}")
    finally:
        connection.close()

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))