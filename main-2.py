import discord
from discord.ext import commands
import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Database connection
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
    )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def menu(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT 
                name, 
                description, 
                price 
            FROM 
                MenuItems 
            WHERE 
                available = TRUE
        """)
        items = cursor.fetchall()
    conn.close()

    if not items:
        await ctx.send("Menu is currently empty.")
    else:
        response = "**Menu:**\n"
        for item in items:
            response += f"{item['name']} - {item['description']} - ${item['price']}\n"
        await ctx.send(response)

@bot.command()
async def order(ctx, *item_ids):
    if not item_ids:
        await ctx.send("Please provide item IDs to order.")
        return

    user = str(ctx.author.id)
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT 
                customer_id 
            FROM 
                Customers 
            WHERE 
                discord_user_id = %s
        """, (user,))
        customer = cursor.fetchone()

        if not customer:
            cursor.execute("""
                INSERT INTO Customers (discord_user_id, name) 
                VALUES (%s, %s)
            """, (user, str(ctx.author)))
            conn.commit()
            cursor.execute("""
                SELECT 
                    customer_id 
                FROM 
                    Customers 
                WHERE 
                    discord_user_id = %s
            """, (user,))
            customer = cursor.fetchone()

        customer_id = customer['customer_id']
        cursor.execute("""
            INSERT INTO Orders (customer_id, order_date, total_amount, status) 
            VALUES (%s, NOW(), 0, 'Pending')
        """, (customer_id,))
        order_id = cursor.lastrowid

        total_amount = 0.0
        for item_id in item_ids:
            cursor.execute("""
                SELECT 
                    price 
                FROM 
                    MenuItems 
                WHERE 
                    item_id = %s 
                    AND available = TRUE
            """, (item_id,))
            item = cursor.fetchone()
            if item:
                cursor.execute("""
                    INSERT INTO OrderDetails (order_id, item_id, quantity) 
                    VALUES (%s, %s, 1)
                """, (order_id, item_id))
                total_amount += float(item['price'])

        cursor.execute("""
            UPDATE Orders 
            SET total_amount = %s 
            WHERE order_id = %s
        """, (total_amount, order_id))
        conn.commit()
    conn.close()

    await ctx.send(f"Order placed successfully. Total: ${total_amount:.2f}")


@bot.command()
async def help(ctx):
    """List available commands."""
    help_text = (
        "**Available Commands:**\n"
        "`!menu` - View the current menu\n"
        "`!order [item_ids...]` - Place an order by item ID\n"
        "`!reserve YYYY-MM-DD HH:MM party_size` - Make a reservation\n"
        "`!feedback rating comment` - Leave a rating and comment\n"
        "\n**Admin Commands:**\n"
        "`!add_item name price description` - Add a new menu item\n"
        "`!remove_item item_id` - Mark a menu item as unavailable\n"
        "`!view_orders` - View all orders\n"
        "`!update_reservation reservation_id status` - Update reservation status\n"
        "`!export_sales` - Export sales report (CSV)\n"
        "`!export_feedback` - Export all feedback (CSV)"
    )
    await ctx.send(help_text)

bot.run(os.getenv("DISCORD_TOKEN"))
