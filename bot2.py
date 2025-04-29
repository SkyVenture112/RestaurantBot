import discord
from discord.ext import commands
from datetime import datetime
import pymysql
import random

DISCORD_TOKEN = "MTM1OTM2NjY3ODExNDQ2NzkwMA.GosVbz.oF-BWPc_laD61wlzcon1n5vdNfeJfi0sTITeq0"
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Cpsc408!"
MYSQL_DATABASE = "menu"

# Database connection function
def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

# Bot setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "?"], intents=intents, help_command=None)
# Commands
@bot.command()
async def menu(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT itemID, Name, Price
            FROM MenuTable
            WHERE isAvailable = TRUE
        """)
        menu_items = cursor.fetchall()
    conn.close()

    if not menu_items:
        await ctx.send("The menu is currently empty.")
    else:
        response = "**Menu:**\n"
        for item in menu_items:
            response += f"ID: {item['itemID']} | {item['Name']} - ${item['Price']:.2f}\n"
        await ctx.send(response)

@bot.command()
async def order(ctx, *item_ids):
    customer_name = f"DiscordUser_{ctx.author.id}"
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Find or create customer
        cursor.execute("""
            SELECT customerID
            FROM CustomerTable
            WHERE Name = %s
        """, (customer_name,))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customerID']
        else:
            cursor.execute("SELECT MAX(customerID) AS max_id FROM CustomerTable")
            result = cursor.fetchone()
            new_customer_id = (result['max_id'] or 0) + 1

            cursor.execute("""
                INSERT INTO CustomerTable (customerID, Name, Phone)
                VALUES (%s, %s, %s)
            """, (new_customer_id, customer_name, "N/A"))
            conn.commit()

            customer_id = new_customer_id

        # Create order
        current_time = datetime.now()
        cursor.execute("SELECT MAX(orderID) AS max_order_id FROM OrderTable")
        result = cursor.fetchone()
        new_order_id = (result['max_order_id'] or 0) + 1

        cursor.execute("""
            INSERT INTO OrderTable (orderID, orderDate, customerID, Status)
            VALUES (%s, %s, %s, 'Unfulfilled')
        """, (new_order_id, current_time, customer_id))

        order_id = new_order_id

        # Add order items
        for item_id in item_ids:
            cursor.execute("""
                SELECT itemID
                FROM MenuTable
                WHERE itemID = %s
                  AND isAvailable = TRUE
            """, (item_id,))
            item = cursor.fetchone()
            if item:
                cursor.execute("""
                    INSERT INTO OrderDetailsTable (orderID, itemID, Quantity)
                    VALUES (%s, %s, 1)
                """, (order_id, item_id))
        conn.commit()
    conn.close()

    await ctx.send(f"Order placed successfully! Your order ID is {order_id}.")

@bot.command()
async def reserve(ctx, date, time, party_size: int):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        customer_name = f"DiscordUser_{ctx.author.id}"

        # Ensure customer exists
        cursor.execute("""
            SELECT customerID FROM CustomerTable WHERE Name = %s
        """, (customer_name,))
        customer = cursor.fetchone()

        if not customer:
            cursor.execute("""
                INSERT INTO CustomerTable (Name, Phone)
                VALUES (%s, %s)
            """, (customer_name, "N/A"))
            conn.commit()
            customer_id = cursor.lastrowid
        else:
            customer_id = customer['customerID']

        # Make Reservation
        try:
            reservation_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            cursor.execute("""
                INSERT INTO ReservationTable (reservationDate, customerID, time)
                VALUES (%s, %s, %s)
            """, (reservation_datetime.date(), customer_id, reservation_datetime.time()))
            conn.commit()
            await ctx.send(f"Reservation made for {reservation_datetime} with {party_size} people.")
        except ValueError:
            await ctx.send("Invalid date/time format. Use YYYY-MM-DD HH:MM")
    conn.close()

@bot.command()
async def feedback(ctx, rating: int, *, comment):
    if not (1 <= rating <= 5):
        await ctx.send("Rating must be between 1 and 5.")
        return

    conn = get_db_connection()
    with conn.cursor() as cursor:
        customer_name = f"DiscordUser_{ctx.author.id}"

        cursor.execute("""
            SELECT customerID FROM CustomerTable WHERE Name = %s
        """, (customer_name,))
        customer = cursor.fetchone()

        if not customer:
            await ctx.send("You must place an order or reserve first to leave feedback!")
            conn.close()
            return

        cursor.execute("""
            INSERT INTO RatingTable (customerID, Rating, Comment)
            VALUES (%s, %s, %s)
        """, (customer['customerID'], rating, comment))
        conn.commit()
    conn.close()

    await ctx.send("Thank you for your feedback!")

# ADMIN COMMANDS
@bot.command()
@commands.has_permissions(administrator=True)
async def add_item(ctx, name, price: float):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO MenuTable (Name, Price, isAvailable)
            VALUES (%s, %s, TRUE)
        """, (name, price))
        conn.commit()
    conn.close()

    await ctx.send(f"Item '{name}' added to the menu.")

@bot.command()
@commands.has_permissions(administrator=True)
async def remove_item(ctx, item_id: int):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE MenuTable
            SET isAvailable = FALSE
            WHERE itemID = %s
        """, (item_id,))
        conn.commit()
    conn.close()

    await ctx.send(f"Item ID {item_id} marked as unavailable.")

@bot.command()
@commands.has_permissions(administrator=True)
async def view_orders(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT orderID, customerID, orderDate, Status
            FROM OrderTable
            ORDER BY orderDate DESC
            LIMIT 10
        """)
        orders = cursor.fetchall()
    conn.close()

    if not orders:
        await ctx.send("No orders found.")
    else:
        response = "**Recent Orders:**\n"
        for order in orders:
            response += f"Order {order['orderID']} | Customer {order['customerID']} | {order['orderDate']} | {order['Status']}\n"
        await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def export_sales(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM OrderTable")
        orders = cursor.fetchall()
    conn.close()

    if not orders:
        await ctx.send("No sales to export.")
        return

    filename = "sales_report.csv"
    with open(filename, "w") as f:
        headers = orders[0].keys()
        f.write(",".join(headers) + "\n")
        for order in orders:
            f.write(",".join(str(order[h]) for h in headers) + "\n")

    await ctx.send(file=discord.File(filename))

@bot.command(name="help")
async def bot_help(ctx):
    help_text = (
        "**User Commands:**\n"
        "`!menu` - View the current menu\n"
        "`!order [item_ids...]` - Place an order\n"
        "`!reserve YYYY-MM-DD HH:MM party_size` - Make a reservation\n"
        "`!feedback rating comment` - Leave feedback\n\n"
        "**Admin Commands:**\n"
        "`!add_item name price` - Add a menu item\n"
        "`!remove_item item_id` - Mark an item unavailable\n"
        "`!view_orders` - View recent orders\n"
        "`!export_sales` - Export sales report\n"
    )
    await ctx.send(help_text)

# Run the bot
bot.run(DISCORD_TOKEN)
