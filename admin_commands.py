import discord
import csv
from discord.ext import commands
from db import get_db_connection


def register(bot):
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def mark_fulfilled(ctx, order_id: int):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM OrderTable
                WHERE orderID = %s
            """, (order_id,))
            order = cursor.fetchone()
            if not order:
                await ctx.send("Order not found.")
            else:
                cursor.execute("""
                    UPDATE OrderTable
                    SET Status = 'Fulfilled', fulfilledTime = NOW()
                    WHERE orderID = %s
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
    async def view_feedback(ctx):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.ratingID, c.Name AS customerName, r.Rating, r.Comment
                FROM RatingTable r
                JOIN CustomerTable c ON r.customerID = c.customerID
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
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT orderID, orderDate, customerID, Status, totalAmount
                FROM OrderTable
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
                SELECT c.Name, AVG(r.Rating) AS avg_rating, COUNT(*) AS total_reviews
                FROM RatingTable r
                JOIN CustomerTable c ON r.customerID = c.customerID
                GROUP BY c.Name
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

    @bot.command()
    async def cancel_order(ctx, order_id: int):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT *
                FROM OrderTable
                WHERE orderID = %s
            """, (order_id,))
            order = cursor.fetchone()
            if not order:
                await ctx.send("Order not found.")
            elif order['Status'] == 'Fulfilled':
                await ctx.send("Cannot cancel a fulfilled order.")
            else:
                cursor.execute("""
                    UPDATE OrderTable
                    SET isCanceled = 1
                    WHERE orderID = %s
                """, (order_id,))
                conn.commit()
                await ctx.send(f"Order {order_id} has been canceled.")
        conn.close()

    @bot.command()
    async def top_spender_on_expensive(ctx):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT c.Name
                FROM CustomerTable c
                JOIN OrderTable o ON c.customerID = o.customerID
                JOIN OrderDetailsTable d ON o.orderID = d.orderID
                WHERE d.itemID = (
                    SELECT itemID
                    FROM MenuTable
                    ORDER BY Price DESC
                    LIMIT 1
                )
            """)
            customers = cursor.fetchall()
        conn.close()

        if customers:
            names = ', '.join([c['Name'] for c in customers])
            await ctx.send(f"Customers who ordered the most expensive item: {names}")
        else:
            await ctx.send("No one has ordered the most expensive item yet.")

    @bot.command()
    async def full_order_history(ctx):
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT o.orderID, c.Name AS customerName, m.Name AS itemName, d.Quantity, o.orderDate
                FROM OrderTable o
                JOIN CustomerTable c ON o.customerID = c.customerID
                JOIN OrderDetailsTable d ON o.orderID = d.orderID
                JOIN MenuTable m ON d.itemID = m.itemID
                ORDER BY o.orderDate DESC
            """)
            rows = cursor.fetchall()
        conn.close()

        if not rows:
            await ctx.send("No orders found.")
            return

        response = "**Full Order History:**\n"
        for row in rows:
            response += (
                f"Order ID: {row['orderID']} | Customer: {row['customerName']} | "
                f"Item: {row['itemName']} x{row['Quantity']} | Date: {row['orderDate']}\n"
            )

        response_chunks = [response[i:i + 2000] for i in range(0, len(response), 2000)]
        for chunk in response_chunks:
            await ctx.send(chunk)