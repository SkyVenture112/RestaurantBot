import discord
from discord.ext import commands
import pymysql

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

try:
    import user_commands

    user_commands.register(bot)
except ImportError:
    print("Error: `user_commands` module not found.")

try:
    import admin_commands

    admin_commands.register(bot)
except ImportError:
    print("Error: `admin_commands` module not found.")


@bot.command(name="help")
async def bot_help(ctx):
    help_text = (
        "**User Commands:**\n"
        "`!menu` - View the menu\n"
        "`!order [item_ids...]` - Place an order\n"
        "`!reserve YYYY-MM-DD HH:MM party_size` - Make a reservation\n"
        "`!feedback rating comment` - Leave feedback\n"
        "`!popular_items [limit]` - View top menu items\n"
        "`!cancel_order order_id` - Cancel your order\n"
        "`!full_order_history` - View your order history\n\n"

        "**Admin Commands:**\n"
        "`!mark_fulfilled order_id` - Mark an order as fulfilled\n"
        "`!export_sales` - Export sales data to CSV\n"
        "`!view_feedback` - View all feedback\n"
        "`!view_orders` - View all orders\n"
        "`!ratings_summary` - Show average customer ratings\n"
        "`!top_spender_on_expensive` - View who ordered the most expensive item\n"
    )
    await ctx.send(help_text)


if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("Error: Discord token not found. Set it in the environment variables.")
