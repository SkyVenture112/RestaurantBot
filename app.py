import discord
import pymysql
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

# MySQL connection setup
def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

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

@bot.command(name="reserve")
async def reserve(ctx, date, time):
    user_id = ctx.author.id
    username = ctx.author.name

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # TODO: Replace this with actual table - create_query = "INSERT INTO reservations (reservation_id, reservation_date, customer_id) VALUES (%s, %s, %s)"
            # cursor.execute(create_query, (customer_id, reservation_date))
        connection.commit()
        # TODO: Replace with actual attributes - await ctx.send(f"Reservation confirmed on **{date}**.")
    except pymysql.MySQLError as e:
        await ctx.send(f"Error: {e}")
    finally:
        connection.close()

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
