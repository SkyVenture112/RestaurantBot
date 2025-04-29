import discord
from discord.ext import commands
from datetime import datetime
import pymysql

DISCORD_TOKEN = "MTM1OTM2NjY3ODExNDQ2NzkwMA.GosVbz.oF-BWPc_laD61wlzcon1n5vdNfeJfi0sTITeq0"
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "CPSC408!"
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
@bot.command(name="menu")
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

@bot.command(name="order")
async def order(ctx, *item_ids):
    user = str(ctx.author.id)
    conn = get_db_connection()
    with conn.cursor() as cursor:
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

@bot.command(name="reserve")
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

@bot.command(name="feedback")
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

@bot.command(name="add_item")
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

@bot.command(name="remove_item")
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

@bot.command(name="view_orders")
@commands.has_permissions(administrator=True)
async def view_orders(ctx):
    try:
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
            return

        response = "**Recent Orders:**\n"
        for order in orders:
            response += f"Order {order['orderID']} | Customer {order['customerID']} | ${order['totalAmount']:.2f} | Status: {order['status']}\n"
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error retrieving orders: {str(e)}")

@view_orders.error
async def view_orders_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need administrator permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

@bot.command(name="export_sales")
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

@bot.command(name="help")
async def bot_help(ctx):
    help_text = (
        "**User Commands:**\n"
        "`!menu` - View the current menu\n"
        "`!order [item_ids...]` - Place an order by item ID\n"
        "`!reserve YYYY-MM-DD HH:MM party_size` - Make a reservation\n"
        "`!feedback rating comment` - Leave a rating and comment\n\n"
        "**Admin Commands:**\n"
        "`!add_item name price description` - Add a new menu item\n"
        "`!remove_item item_id` - Mark a menu item as unavailable\n"
        "`!view_orders` - View the latest orders\n"
        "`!export_sales` - Export a CSV of sales data\n"
    )
    await ctx.send(help_text)

# Run the bot
bot.run(DISCORD_TOKEN)
