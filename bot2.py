import discord
from discord.ext import commands
from datetime import datetime
import pymysql
import csv

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

@bot.command()
async def menu(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                itemID,
                Name,
                Price
            FROM
                MenuTable
            WHERE
                isAvailable = TRUE
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
    customer_name = ctx.author.display_name
    conn = get_db_connection()
    unavailable_items = []
    available_menu = []

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                itemID,
                Name
            FROM
                MenuTable
            WHERE
                isAvailable = TRUE
        """)
        available_menu = cursor.fetchall()

        for item_id in item_ids:
            cursor.execute("""
                SELECT
                    itemID,
                    Name,
                    isAvailable
                FROM
                    MenuTable
                WHERE
                    itemID = %s
            """, (item_id,))
            item = cursor.fetchone()
            if not item or not item['isAvailable']:
                unavailable_items.append(item_id)

        if unavailable_items:
            unavailable_message = f"The following items are out of stock: {', '.join(map(str, unavailable_items))}\n"
            available_message = "**Available items:**\n"
            for menu_item in available_menu:
                available_message += f"ID: {menu_item['itemID']} | {menu_item['Name']}\n"
            await ctx.send(unavailable_message + available_message)
            return

        cursor.execute("""
            SELECT
                customerID
            FROM
                CustomerTable
            WHERE
                Name = %s
        """, (customer_name,))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customerID']
        else:
            cursor.execute("""
                SELECT
                    MAX(customerID) AS max_id
                FROM
                    CustomerTable
            """)
            result = cursor.fetchone()
            new_customer_id = (result['max_id'] or 0) + 1
            cursor.execute("""
                INSERT INTO
                    CustomerTable (customerID, Name, Phone)
                VALUES
                    (%s, %s, %s)
            """, (new_customer_id, customer_name, "N/A"))
            conn.commit()
            customer_id = new_customer_id

        current_time = datetime.now()
        cursor.execute("""
            SELECT
                MAX(orderID) AS max_order_id
            FROM
                OrderTable
        """)
        result = cursor.fetchone()
        new_order_id = (result['max_order_id'] or 0) + 1
        cursor.execute("""
            INSERT INTO
                OrderTable (orderID, orderDate, customerID, Status, totalAmount)
            VALUES
                (%s, %s, %s, 'Unfulfilled', 0.00)
        """, (new_order_id, current_time, customer_id))
        order_id = new_order_id

        total_price = 0.0
        for item_id in item_ids:
            cursor.execute("""
                SELECT
                    itemID,
                    Price
                FROM
                    MenuTable
                WHERE
                    itemID = %s
                    AND isAvailable = TRUE
            """, (item_id,))
            item = cursor.fetchone()
            if item:
                cursor.execute("""
                    INSERT INTO
                        OrderDetailsTable (orderID, itemID, Quantity, priceAtOrder)
                    VALUES
                        (%s, %s, 1, %s)
                """, (order_id, item_id, item['Price']))
                total_price += float(item['Price'])
                cursor.execute("""
                    UPDATE
                        MenuTable
                    SET
                        isAvailable = FALSE
                    WHERE
                        itemID = %s
                """, (item_id,))

        cursor.execute("""
            UPDATE
                OrderTable
            SET
                totalAmount = %s
            WHERE
                orderID = %s
        """, (total_price, order_id))
        conn.commit()
    conn.close()

    await ctx.send(f"Order placed successfully! Total: **${total_price:.2f}** for Order ID {order_id}.")

@bot.command()
async def reserve(ctx, date, time, party_size: int):
    customer_name = ctx.author.display_name
    datetime_str = f"{date} {time}"
    try:
        reservation_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        await ctx.send("Invalid date/time format. Use YYYY-MM-DD HH:MM")
        return

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    customerID
                FROM
                    CustomerTable
                WHERE
                    Name = %s
            """, (customer_name,))
            customer = cursor.fetchone()

            if customer:
                customer_id = customer['customerID']
            else:
                cursor.execute("""
                    SELECT
                        MAX(customerID) AS max_id
                    FROM
                        CustomerTable
                """)
                result = cursor.fetchone()
                new_customer_id = (result['max_id'] or 0) + 1
                cursor.execute("""
                    INSERT INTO
                        CustomerTable (customerID, Name, Phone)
                    VALUES
                        (%s, %s, %s)
                """, (new_customer_id, customer_name, "N/A"))
                conn.commit()
                customer_id = new_customer_id

            cursor.execute("""
                SELECT
                    MAX(reservationID) AS max_res_id
                FROM
                    ReservationTable
            """)
            result = cursor.fetchone()
            new_reservation_id = (result['max_res_id'] or 0) + 1
            cursor.execute("""
                INSERT INTO
                    ReservationTable (reservationID, reservationDate, customerID, time, partySize, status)
                VALUES
                    (%s, %s, %s, %s, %s, 'Pending')
            """, (new_reservation_id, reservation_datetime.date(), customer_id, reservation_datetime.time(), party_size))
            conn.commit()

        conn.close()
        await ctx.send(f"Reservation successful! Reservation ID: **{new_reservation_id}**, Date: **{reservation_datetime.strftime('%Y-%m-%d')}**, Time: **{reservation_datetime.strftime('%H:%M')}**, Party Size: **{party_size}**.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def feedback(ctx, rating: str, *, comment):
    """Leave a rating and comment."""
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            await ctx.send(" Rating must be between 1 and 5.")
            return
    except ValueError:
        await ctx.send(" Rating must be a valid integer between 1 and 5.")
        return

    customer_name = ctx.author.display_name
    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                customerID
            FROM
                CustomerTable
            WHERE
                Name = %s
        """, (customer_name,))
        customer = cursor.fetchone()

        if customer:
            customer_id = customer['customerID']
        else:
            cursor.execute("""
                SELECT
                    MAX(customerID) AS max_id
                FROM
                    CustomerTable
            """)
            customer_id = (cursor.fetchone()['max_id'] or 0) + 1
            cursor.execute("""
                INSERT INTO
                    CustomerTable (customerID, Name, Phone)
                VALUES
                    (%s, %s, %s)
            """, (customer_id, customer_name, "N/A"))
            conn.commit()

        cursor.execute("""
            SELECT
                MAX(ratingID) AS max_rating_id
            FROM
                RatingTable
        """)
        rating_id = (cursor.fetchone()['max_rating_id'] or 0) + 1
        cursor.execute("""
            INSERT INTO
                RatingTable (ratingID, customerID, Rating, Comment)
            VALUES
                (%s, %s, %s, %s)
        """, (rating_id, customer_id, rating, comment))
        conn.commit()

    conn.close()
    await ctx.send(" Thank you for your feedback!")



@bot.command()
async def popular_items(ctx, limit: int = 3): # Uses view vPopularItems created in database
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT v.itemID, 
                   v.Name,
                   v.Price, 
                   v.order_count
            FROM vPopularItems as v
            ORDER BY v.order_count DESC
            LIMIT %s
        """, (limit,))
        
    popular_items = cursor.fetchall()

    conn.close()

    if not popular_items:
        await ctx.send("No order history available.")
        return
    
    response = f"**Top {limit} Most Popular Menu Items:**\n\n"
    for item in popular_items:
        response += (
            f"**{item['Name']}**\n"
            f"Price: ${item['Price']:.2f} | "
            f"Ordered {item['order_count']} times\n")
    
    await ctx.send(response)

@bot.command()
@commands.has_permissions(administrator=True)
async def mark_fulfilled(ctx, order_id: int):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                *
            FROM
                OrderTable
            WHERE
                orderID = %s
        """, (order_id,))
        order = cursor.fetchone()
        if not order:
            await ctx.send("Order not found.")
        else:
            cursor.execute("""
                UPDATE
                    OrderTable
                SET
                    Status = 'Fulfilled',
                    fulfilledTime = NOW()
                WHERE
                    orderID = %s
            """, (order_id,))
            conn.commit()
            await ctx.send(f"Order {order_id} marked as fulfilled.")
    conn.close()

@bot.command()
@commands.has_permissions(administrator=True)
async def export_sales(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM OrderTable
        """)
        orders = cursor.fetchall()

    filename = "sales_export.csv"
    with open(filename, "w", newline="") as csvfile:
        if orders:
            fieldnames = orders[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in orders:
                writer.writerow(row)

    conn.close()
    await ctx.send(file=discord.File(filename))


@bot.command()
#@commands.has_permissions(administrator=True)
async def view_feedback(ctx):
    """View all feedback."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                r.ratingID,
                c.Name AS customerName,
                r.Rating,
                r.Comment
            FROM
                RatingTable r
            JOIN
                CustomerTable c
            ON
                r.customerID = c.customerID
        """)
        feedback = cursor.fetchall()
    conn.close()

    if not feedback:
        await ctx.send("No feedback found.")
    else:
        response = "**Feedback:**\n"
        for entry in feedback:
            response += (
                f"Rating ID: {entry['ratingID']} | Customer: {entry['customerName']} | "
                f"Rating: {entry['Rating']} | Comment: {entry['Comment']}\n"
            )
        await ctx.send(response)


@bot.command()
@commands.has_permissions(administrator=True)
async def view_orders(ctx):
    """View all orders."""
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                orderID,
                orderDate,
                customerID,
                Status,
                totalAmount
            FROM
                OrderTable
        """)
        orders = cursor.fetchall()
    conn.close()

    if not orders:
        await ctx.send("No orders found.")
    else:
        response = "**Orders:**\n"
        for order in orders:
            response += (
                f"Order ID: {order['orderID']} | Date: {order['orderDate']} | "
                f"Customer ID: {order['customerID']} | Status: {order['Status']} | "
                f"Total: ${order['totalAmount']:.2f}\n"
            )
        await ctx.send(response)



@bot.command()
@commands.has_permissions(administrator=True)
async def ratings_summary(ctx):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                c.Name,
                AVG(r.Rating) AS avg_rating,
                COUNT(*) AS total_reviews
            FROM
                RatingTable r
            JOIN
                CustomerTable c
            ON
                r.customerID = c.customerID
            GROUP BY
                c.Name
        """)
        summary = cursor.fetchall()

    conn.close()

    if not summary:
        await ctx.send("No ratings data available.")
    else:
        response = "**Ratings Summary:**\n"
        for row in summary:
            response += f"{row['Name']}: {row['avg_rating']:.2f}/5 from {row['total_reviews']} reviews\n"
        await ctx.send(response)

@bot.command(name="help")
async def bot_help(ctx):
    help_text = (
        "**User Commands:**\n"
        "`!menu` - View the menu\n"
        "`!order [item_ids...]` - Place an order (comma or space separated)\n"
        "`!reserve YYYY-MM-DD HH:MM party_size` - Make a reservation\n"
        "`!feedback rating comment` - Leave feedback\n"
        "`!popular_items` - View most popular menu items\n"
        "\n"
        "**Admin Commands:**\n"
        "`!mark_fulfilled order_id` - Mark an order as fulfilled\n"
        "`!export_sales` - Export sales data to CSV\n"
        "`!ratings_summary` - Show average customer ratings\n"
        "`!view_orders`,`!view_feedback` - View latest data\n"
    )
    await ctx.send(help_text)

bot.run(DISCORD_TOKEN)
