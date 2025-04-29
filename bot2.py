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

def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "?"], intents=intents, help_command=None)

# ===== Commands =====

@bot.command()
async def menu(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT itemID, Name, Price FROM MenuTable WHERE isAvailable = TRUE")
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
        cursor.execute("SELECT customerID FROM CustomerTable WHERE Name = %s", (customer_name,))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customerID']
        else:
            cursor.execute("SELECT MAX(customerID) AS max_id FROM CustomerTable")
            result = cursor.fetchone()
            new_customer_id = (result['max_id'] or 0) + 1
            cursor.execute("INSERT INTO CustomerTable (customerID, Name, Phone) VALUES (%s, %s, %s)", (new_customer_id, customer_name, "N/A"))
            conn.commit()
            customer_id = new_customer_id

        current_time = datetime.now()
        cursor.execute("SELECT MAX(orderID) AS max_order_id FROM OrderTable")
        result = cursor.fetchone()
        new_order_id = (result['max_order_id'] or 0) + 1
        cursor.execute("INSERT INTO OrderTable (orderID, orderDate, customerID, Status, totalAmount) VALUES (%s, %s, %s, 'Unfulfilled', 0.00)", (new_order_id, current_time, customer_id))
        order_id = new_order_id

        total_price = 0.0
        item_ids_clean = []
        for raw in item_ids:
            for part in raw.split(","):
                part = part.strip()
                if part.isdigit():
                    item_ids_clean.append(int(part))

        for item_id in item_ids_clean:
            cursor.execute("SELECT itemID, Price FROM MenuTable WHERE itemID = %s AND isAvailable = TRUE", (item_id,))
            item = cursor.fetchone()
            if item:
                cursor.execute("INSERT INTO OrderDetailsTable (orderID, itemID, Quantity) VALUES (%s, %s, 1)", (order_id, item_id))
                total_price += item['Price']

        cursor.execute("UPDATE OrderTable SET totalAmount = %s WHERE orderID = %s", (total_price, order_id))
        conn.commit()
    conn.close()

    await ctx.send(f"Order placed successfully! Total: **${total_price:.2f}** for Order ID {order_id}.")

@bot.command()
async def reserve(ctx, date, time, party_size: int):
    customer_name = f"DiscordUser_{ctx.author.id}"
    datetime_str = f"{date} {time}"
    try:
        reservation_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        await ctx.send("Invalid date/time format. Use YYYY-MM-DD HH:MM")
        return

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT customerID FROM CustomerTable WHERE Name = %s", (customer_name,))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customerID']
        else:
            cursor.execute("SELECT MAX(customerID) AS max_id FROM CustomerTable")
            result = cursor.fetchone()
            new_customer_id = (result['max_id'] or 0) + 1
            cursor.execute("INSERT INTO CustomerTable (customerID, Name, Phone) VALUES (%s, %s, %s)", (new_customer_id, customer_name, "N/A"))
            conn.commit()
            customer_id = new_customer_id

        cursor.execute("SELECT MAX(reservationID) AS max_res_id FROM ReservationTable")
        result = cursor.fetchone()
        new_reservation_id = (result['max_res_id'] or 0) + 1
        cursor.execute("INSERT INTO ReservationTable (reservationID, reservationDate, customerID, time) VALUES (%s, %s, %s, %s)", (new_reservation_id, reservation_datetime.date(), customer_id, reservation_datetime.time()))
        conn.commit()
    conn.close()

    await ctx.send(f"Reservation made for {reservation_datetime.strftime('%Y-%m-%d %H:%M')} with {party_size} people.")

@bot.command()
async def feedback(ctx, rating: int, *, comment):
    if rating < 1 or rating > 5:
        await ctx.send("Rating must be between 1 and 5 stars.")
        return

    customer_name = f"DiscordUser_{ctx.author.id}"
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT customerID FROM CustomerTable WHERE Name = %s", (customer_name,))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customerID']
        else:
            cursor.execute("SELECT MAX(customerID) AS max_id FROM CustomerTable")
            result = cursor.fetchone()
            new_customer_id = (result['max_id'] or 0) + 1
            cursor.execute("INSERT INTO CustomerTable (customerID, Name, Phone) VALUES (%s, %s, %s)", (new_customer_id, customer_name, "N/A"))
            conn.commit()
            customer_id = new_customer_id

        cursor.execute("SELECT MAX(ratingID) AS max_rating_id FROM RatingTable")
        result = cursor.fetchone()
        new_rating_id = (result['max_rating_id'] or 0) + 1

        cursor.execute("INSERT INTO RatingTable (ratingID, customerID, Rating, Comment) VALUES (%s, %s, %s, %s)", (new_rating_id, customer_id, rating, comment))
        conn.commit()
    conn.close()

    await ctx.send("Thank you for your feedback!")

@bot.command()
@commands.has_permissions(administrator=True)
async def view_orders(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT o.orderID, c.Name, o.totalAmount, o.Status, o.orderDate
            FROM OrderTable o
            JOIN CustomerTable c ON o.customerID = c.customerID
            ORDER BY o.orderDate DESC
            LIMIT 10
        """)
        orders = cursor.fetchall()
    conn.close()

    if not orders:
        await ctx.send("No orders found.")
    else:
        response = "**Recent Orders:**\n"
        for order in orders:
            response += f"Order {order['orderID']} | {order['Name']} | ${order['totalAmount']:.2f} | Status: {order['Status']}\n"
        await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def view_feedback(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.ratingID, c.Name, r.Rating, r.Comment
            FROM RatingTable r
            JOIN CustomerTable c ON r.customerID = c.customerID
            ORDER BY r.ratingID DESC
        """)
        feedbacks = cursor.fetchall()
    conn.close()

    if not feedbacks:
        await ctx.send("No feedback found.")
    else:
        response = "**Feedback:**\n"
        for fb in feedbacks:
            response += f"{fb['Name']} rated {fb['Rating']}/5: \"{fb['Comment']}\"\n"
        await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def view_reservations(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.reservationID, c.Name, r.reservationDate, r.time
            FROM ReservationTable r
            JOIN CustomerTable c ON r.customerID = c.customerID
            ORDER BY r.reservationDate DESC
        """)
        reservations = cursor.fetchall()
    conn.close()

    if not reservations:
        await ctx.send("No reservations found.")
    else:
        response = "**Reservations:**\n"
        for res in reservations:
            response += f"Reservation {res['reservationID']} | {res['Name']} on {res['reservationDate']} at {res['time']}\n"
        await ctx.send(response)

@bot.command(name="help")
async def bot_help(ctx):
    help_text = (
        "**User Commands:**\n"
        "`!menu` - View the menu\n"
        "`!order [item_ids...]` - Place an order (comma or space separated)\n"
        "`!reserve YYYY-MM-DD HH:MM party_size` - Make a reservation\n"
        "`!feedback rating comment` - Leave feedback\n"
        "\n"
        "**Admin Commands:**\n"
        "`!view_orders` - View recent orders\n"
        "`!view_reservations` - View upcoming reservations\n"
        "`!view_feedback` - View customer feedback\n"
    )
    await ctx.send(help_text)

# ===== Run Bot =====
bot.run(DISCORD_TOKEN)



