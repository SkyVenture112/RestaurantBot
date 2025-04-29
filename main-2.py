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

# ========== USER COMMANDS ==========

# !menu
@bot.command()
async def menu(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT itemID, Name, Price 
            FROM MenuTable 
            WHERE isAvailable = TRUE
        """)
        items = cursor.fetchall()
    conn.close()

    if not items:
        await ctx.send("Menu is currently empty.")
    else:
        response = "**Menu:**\n"
        for item in items:
            response += f"ID {item['itemID']}: {item['Name']} - ${item['Price']:.2f}\n"
        await ctx.send(response)

# !order
@bot.command()
async def order(ctx, *item_ids):
    if not item_ids:
        await ctx.send("Please provide item IDs to order.")
        return

    user = str(ctx.author.id)
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Check or create customer
        cursor.execute("""
            SELECT customerID 
            FROM CustomerTable 
            WHERE discord_user_id = %s
        """, (user,))
        customer = cursor.fetchone()

        if not customer:
            cursor.execute("""
                INSERT INTO CustomerTable (Name, Phone, discord_user_id) 
                VALUES (%s, %s, %s)
            """, (str(ctx.author), "N/A", user))
            conn.commit()
            cursor.execute("""
                SELECT customerID 
                FROM CustomerTable 
                WHERE discord_user_id = %s
            """, (user,))
            customer = cursor.fetchone()

        customer_id = customer['customerID']

        # Create order
        cursor.execute("""
            INSERT INTO Orders (customerID, orderDate, totalAmount, status) 
            VALUES (%s, NOW(), 0, 'Pending')
        """, (customer_id,))
        order_id = cursor.lastrowid

        # Insert each item into OrderDetails
        total_amount = 0.0
        for item_id in item_ids:
            cursor.execute("""
                SELECT Price 
                FROM MenuTable 
                WHERE itemID = %s 
                  AND isAvailable = TRUE
            """, (item_id,))
            item = cursor.fetchone()
            if item:
                cursor.execute("""
                    INSERT INTO OrderDetails (orderID, itemID, quantity) 
                    VALUES (%s, %s, 1)
                """, (order_id, item_id))
                total_amount += float(item['Price'])

        cursor.execute("""
            UPDATE Orders 
            SET totalAmount = %s 
            WHERE orderID = %s
        """, (total_amount, order_id))
        conn.commit()
    conn.close()

    await ctx.send(f"Order placed successfully. Total: ${total_amount:.2f}")

# !reserve
@bot.command()
async def reserve(ctx, date, time, party_size: int):
    user = str(ctx.author.id)
    datetime_str = f"{date} {time}"
    try:
        reservation_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        await ctx.send("Invalid date/time format. Use YYYY-MM-DD HH:MM")
        return

    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Check or create customer
        cursor.execute("""
            SELECT customerID 
            FROM CustomerTable 
            WHERE discord_user_id = %s
        """, (user,))
        customer = cursor.fetchone()

        if not customer:
            cursor.execute("""
                INSERT INTO CustomerTable (Name, Phone, discord_user_id) 
                VALUES (%s, %s, %s)
            """, (str(ctx.author), "N/A", user))
            conn.commit()
            cursor.execute("""
                SELECT customerID 
                FROM CustomerTable 
                WHERE discord_user_id = %s
            """, (user,))
            customer = cursor.fetchone()

        customer_id = customer['customerID']

        cursor.execute("""
            INSERT INTO Reservations (customerID, reservationTime, partySize, status) 
            VALUES (%s, %s, %s, 'Pending')
        """, (customer_id, reservation_time, party_size))
        conn.commit()
    conn.close()

    await ctx.send(f"Reservation made for {reservation_time} with {party_size} people.")

# !feedback
@bot.command()
async def feedback(ctx, rating: int, *, comment):
    if rating < 1 or rating > 5:
        await ctx.send("Rating must be between 1 and 5 stars.")
        return

    user = str(ctx.author.id)
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO Feedback (discord_user_id, rating, comment, feedbackTime)
            VALUES (%s, %s, %s, NOW())
        """, (user, rating, comment))
        conn.commit()
    conn.close()

    await ctx.send("Thank you for your feedback!")

# ========== ADMIN COMMANDS ==========

# !add_item
@bot.command()
@commands.has_permissions(administrator=True)
async def add_item(ctx, name, price: float, *, description="No description."):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO MenuTable (Name, Price, isAvailable)
            VALUES (%s, %s, TRUE)
        """, (name, price))
        conn.commit()
    conn.close()

    await ctx.send(f"Item '{name}' added to the menu.")

# !remove_item
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

# !view_orders
@bot.command()
@commands.has_permissions(administrator=True)
async def view_orders(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT orderID, customerID, orderDate, totalAmount, status 
            FROM Orders
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
            response += f"Order {order['orderID']} | Customer {order['customerID']} | ${order['totalAmount']:.2f} | Status: {order['status']}\n"
        await ctx.send(response)

# !update_reservation



# !export_sales
@bot.command()
@commands.has_permissions(administrator=True)
async def export_sales(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM Orders
        """)
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
            f.write(",".join([str(order[h]) for h in headers]) + "\n")

    await ctx.send(file=discord.File(filename))

# !export_feedback



# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
