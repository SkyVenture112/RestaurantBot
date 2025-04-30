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
async def order(ctx):
    customer_name = f"DiscordUser_{ctx.author.id}"

    while True:
        # Fetch and display available items
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT itemID, Name, Price FROM MenuTable WHERE isAvailable = TRUE")
            menu_items = cursor.fetchall()
        conn.close()

        if not menu_items:
            await ctx.send("The menu is currently empty.")
            return

        response = "**Available Items:**\n"
        for item in menu_items:
            response += f"ID: {item['itemID']} | {item['Name']} - ${item['Price']:.2f}\n"
        response += "\nPlease enter the item IDs you want to order, separated by commas."
        await ctx.send(response)

        # Wait for user input
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for("message", check=check, timeout=60.0)
            item_ids = msg.content.split(",")
            item_ids = [int(item.strip()) for item in item_ids if item.strip().isdigit()]
        except Exception:
            await ctx.send("You took too long to respond. Please try again.")
            return

        # Check availability of items
        conn = get_db_connection()
        unavailable_items = []
        total_price = 0.0
        order_items = []

        with conn.cursor() as cursor:
            for item_id in item_ids:
                cursor.execute("SELECT itemID, Name, Price, isAvailable FROM MenuTable WHERE itemID = %s", (item_id,))
                item = cursor.fetchone()
                if item:
                    if item['isAvailable']:
                        order_items.append(item)
                        total_price += float(item['Price'])
                    else:
                        unavailable_items.append(item['Name'])
                else:
                    unavailable_items.append(f"Item ID {item_id}")

        # If there are unavailable items, notify the user and restart the loop
        if unavailable_items:
            await ctx.send(
                f"The following items are unavailable: {', '.join(unavailable_items)}. Please select from the available menu."
            )
            conn.close()
            continue

        # Place the order for available items
        with conn.cursor() as cursor:
            # Check if customer exists
            cursor.execute("SELECT customerID FROM CustomerTable WHERE Name = %s", (customer_name,))
            customer = cursor.fetchone()

            if customer:
                customer_id = customer['customerID']
            else:
                cursor.execute("SELECT MAX(customerID) AS max_id FROM CustomerTable")
                result = cursor.fetchone()
                new_customer_id = (result['max_id'] or 0) + 1
                cursor.execute("INSERT INTO CustomerTable (customerID, Name, Phone) VALUES (%s, %s, %s)",
                               (new_customer_id, customer_name, "N/A"))
                conn.commit()
                customer_id = new_customer_id

            # Create a new order
            current_time = datetime.now()
            cursor.execute("SELECT MAX(orderID) AS max_order_id FROM OrderTable")
            result = cursor.fetchone()
            new_order_id = (result['max_order_id'] or 0) + 1
            cursor.execute(
                "INSERT INTO OrderTable (orderID, orderDate, customerID, Status, totalAmount) VALUES (%s, %s, %s, "
                "'Unfulfilled', 0.00)",
                (new_order_id, current_time, customer_id))
            order_id = new_order_id

            # Add items to the order and mark them as unavailable
            for item in order_items:
                cursor.execute("INSERT INTO OrderDetailsTable (orderID, itemID, Quantity) VALUES (%s, %s, 1)",
                               (order_id, item['itemID']))
                cursor.execute("UPDATE MenuTable SET isAvailable = 0 WHERE itemID = %s", (item['itemID'],))

            # Update total price in the order
            cursor.execute("UPDATE OrderTable SET totalAmount = %s WHERE orderID = %s", (total_price, order_id))
            conn.commit()
        conn.close()

        # Notify the user of the successful order
        response = f"Order placed successfully! Total: **${total_price:.2f}** for Order ID {order_id}."
        await ctx.send(response)
        break














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
            cursor.execute("INSERT INTO CustomerTable (customerID, Name, Phone) VALUES (%s, %s, %s)",
                           (new_customer_id, customer_name, "N/A"))
            conn.commit()
            customer_id = new_customer_id

        cursor.execute("SELECT MAX(reservationID) AS max_res_id FROM ReservationTable")
        result = cursor.fetchone()
        new_reservation_id = (result['max_res_id'] or 0) + 1
        cursor.execute(
            "INSERT INTO ReservationTable (reservationID, reservationDate, customerID, time) VALUES (%s, %s, %s, %s)",
            (new_reservation_id, reservation_datetime.date(), customer_id, reservation_datetime.time()))
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
            cursor.execute("INSERT INTO CustomerTable (customerID, Name, Phone) VALUES (%s, %s, %s)",
                           (new_customer_id, customer_name, "N/A"))
            conn.commit()
            customer_id = new_customer_id

        cursor.execute("SELECT MAX(ratingID) AS max_rating_id FROM RatingTable")
        result = cursor.fetchone()
        new_rating_id = (result['max_rating_id'] or 0) + 1

        cursor.execute("INSERT INTO RatingTable (ratingID, customerID, Rating, Comment) VALUES (%s, %s, %s, %s)",
                       (new_rating_id, customer_id, rating, comment))
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


# ===== Run Bot =====
bot.run(DISCORD_TOKEN)
