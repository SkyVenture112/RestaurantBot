from db import get_db_connection
from datetime import datetime


# Displays the available menu items to the user.
def register(bot):
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

    # Allows a user to place an order for specific menu items.
    @bot.command()
    async def order(ctx, *item_ids):
        customer_name = ctx.author.display_name
        conn = get_db_connection()
        conn.begin()
        unavailable_items = []

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT itemID, Name
                FROM MenuTable
                WHERE isAvailable = TRUE
            """)
            available_menu = cursor.fetchall()

            for item_id in item_ids:
                cursor.execute("""
                    SELECT itemID, Name, isAvailable
                    FROM MenuTable
                    WHERE itemID = %s
                """, (item_id,))
                item = cursor.fetchone()
                if not item or not item['isAvailable']:
                    unavailable_items.append(item_id)

            if unavailable_items:
                conn.rollback()
                conn.close()
                unavailable_message = f"The following items are out of stock: {', '.join(map(str, unavailable_items))}\n"
                available_message = "**Available items:**\n"
                for menu_item in available_menu:
                    available_message += f"ID: {menu_item['itemID']} | {menu_item['Name']}\n"
                await ctx.send(unavailable_message + available_message)
                return

            cursor.execute("""
                SELECT customerID
                FROM CustomerTable
                WHERE Name = %s
            """, (customer_name,))
            customer = cursor.fetchone()

            if customer:
                customer_id = customer['customerID']
            else:
                cursor.execute("""
                    SELECT MAX(customerID) AS max_id
                    FROM CustomerTable
                """)
                result = cursor.fetchone()
                customer_id = (result['max_id'] or 0) + 1
                cursor.execute("""
                    INSERT INTO CustomerTable (customerID, Name, Phone)
                    VALUES (%s, %s, %s)
                """, (customer_id, customer_name, "N/A"))

            cursor.execute("""
                SELECT MAX(orderID) AS max_order_id
                FROM OrderTable
            """)
            order_id = (cursor.fetchone()['max_order_id'] or 0) + 1
            cursor.execute("""
                INSERT INTO OrderTable (orderID, orderDate, customerID, Status, totalAmount)
                VALUES (%s, %s, %s, 'Unfulfilled', 0.00)
            """, (order_id, datetime.now(), customer_id))

            total_price = 0.0
            for item_id in item_ids:
                cursor.execute("""
                    SELECT itemID, Price
                    FROM MenuTable
                    WHERE itemID = %s AND isAvailable = TRUE
                """, (item_id,))
                item = cursor.fetchone()
                if item:
                    cursor.execute("""
                        INSERT INTO OrderDetailsTable (orderID, itemID, Quantity, priceAtOrder)
                        VALUES (%s, %s, 1, %s)
                    """, (order_id, item_id, item['Price']))
                    total_price += float(item['Price'])
                    cursor.execute("""
                        UPDATE MenuTable
                        SET isAvailable = FALSE
                        WHERE itemID = %s
                    """, (item_id,))

            cursor.execute("""
                UPDATE OrderTable
                SET totalAmount = %s
                WHERE orderID = %s
            """, (total_price, order_id))
            conn.commit()
        conn.close()
        await ctx.send(f"Order placed successfully! Total: **${total_price:.2f}** for Order ID {order_id}.")

    # Allows a user to make a reservation for a specific date, time, and party size.
    @bot.command()
    async def reserve(ctx, date, time, party_size: int):
        customer_name = ctx.author.display_name
        datetime_str = f"{date} {time}"
        try:
            reservation_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            await ctx.send("Invalid date/time format. Use YYYY-MM-DD HH:MM")
            return

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT customerID
                FROM CustomerTable
                WHERE Name = %s
            """, (customer_name,))
            customer = cursor.fetchone()
            if customer:
                customer_id = customer['customerID']
            else:
                cursor.execute("""
                    SELECT MAX(customerID) AS max_id
                    FROM CustomerTable
                """)
                result = cursor.fetchone()
                customer_id = (result['max_id'] or 0) + 1
                cursor.execute("""
                    INSERT INTO CustomerTable (customerID, Name, Phone)
                    VALUES (%s, %s, %s)
                """, (customer_id, customer_name, "N/A"))

            cursor.execute("""
                SELECT MAX(reservationID) AS max_res_id
                FROM ReservationTable
            """)
            res_id = (cursor.fetchone()['max_res_id'] or 0) + 1
            cursor.execute("""
                INSERT INTO ReservationTable (reservationID, reservationDate, customerID, time, partySize, status)
                VALUES (%s, %s, %s, %s, %s, 'Pending')
            """, (res_id, reservation_datetime.date(), customer_id, reservation_datetime.time(), party_size))
            conn.commit()
        conn.close()
        await ctx.send(
            f"Reservation successful! Reservation ID: **{res_id}**, Date: **{reservation_datetime.strftime('%Y-%m-%d')}**, Time: **{reservation_datetime.strftime('%H:%M')}**, Party Size: **{party_size}**.")

    # Allows a user to leave feedback with a rating and comment.
    @bot.command()
    async def feedback(ctx, rating: str, *, comment):
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
                SELECT customerID
                FROM CustomerTable
                WHERE Name = %s
            """, (customer_name,))
            customer = cursor.fetchone()
            if customer:
                customer_id = customer['customerID']
            else:
                cursor.execute("""
                    SELECT MAX(customerID) AS max_id
                    FROM CustomerTable
                """)
                customer_id = (cursor.fetchone()['max_id'] or 0) + 1
                cursor.execute("""
                    INSERT INTO CustomerTable (customerID, Name, Phone)
                    VALUES (%s, %s, %s)
                """, (customer_id, customer_name, "N/A"))

            cursor.execute("""
                SELECT MAX(ratingID) AS max_rating_id
                FROM RatingTable
            """)
            rating_id = (cursor.fetchone()['max_rating_id'] or 0) + 1
            cursor.execute("""
                INSERT INTO RatingTable (ratingID, customerID, Rating, Comment)
                VALUES (%s, %s, %s, %s)
            """, (rating_id, customer_id, rating, comment))
            conn.commit()
        conn.close()
        await ctx.send(" Thank you for your feedback!")

    # Displays the most popular menu items based on order history.
    @bot.command()
    async def popular_items(ctx, limit: int = 3):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT menutable.itemID, menutable.Name, menutable.Price,
                       COUNT(OrderDetailsTable.itemID) AS order_count
                FROM menutable
                LEFT JOIN OrderDetailsTable ON menutable.itemID = OrderDetailsTable.itemID
                GROUP BY menutable.itemID, menutable.Name, menutable.Price
                ORDER BY order_count DESC
                LIMIT %s
            """, (limit,))
            popular_items = cursor.fetchall()
        conn.close()

        if not popular_items:
            await ctx.send("No order history available.")
            return

        response = f"**Top {limit} Most Popular Menu Items:**\n\n"
        for item in popular_items:
            response += f"**{item['Name']}**\nPrice: ${item['Price']:.2f} | Ordered {item['order_count']} times\n"
        await ctx.send(response)