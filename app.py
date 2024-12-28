
API_TOKEN="7823631612:AAHBFokBpoQGxKo6KTbUoVL-JE95R649uPA"
import telebot
bot = telebot.TeleBot(API_TOKEN)
# Command: /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Welcome to the Movie Bot! 🎬\n\n"
        "Type /movie to watch a movie inside Telegram!\n"
        "Type /terabox to watch a terabox inside Telegram!\n"
        "Type /info to see your user details.\n"
        "Type /about to learn more about us."
    )

# Command: /movie
@bot.message_handler(commands=['movie'])
def movie(message):
    # URL of your hosted movie player (Mini App)
    mini_app_url = "https://canidiscover.github.io/Movie/"  # Replace with your movie player URL

    # Create an inline keyboard with a button to open the Mini App
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎬 Watch Movie", web_app=telebot.types.WebAppInfo(mini_app_url)
        )
    )
    
    # Send the message with the link to open the Mini App
    bot.send_message(
        message.chat.id,
        "Click below to start the movie player directly inside Telegram:\n\n🎬 Enjoy your movie!",
        reply_markup=markup
    )

# Command: /info (User details)
@bot.message_handler(commands=['info'])
def info(message):
    user = message.from_user  # Get user details from the message
    user_details = (
        f"Your details:\n"
        f"👤 User ID: {user.id}\n"
        f"💬 Username: @{user.username if user.username else 'N/A'}\n"
        f"📛 First Name: {user.first_name}\n"
        f"🔍 Last Name: {user.last_name if user.last_name else 'N/A'}\n"
        f"🌍 Language: {user.language_code}\n"
    )
    bot.send_message(message.chat.id, user_details)

# Command: /about (About bot)
@bot.message_handler(commands=['about'])
def about(message):
    about_text = (
        "🎬 *About Movie Bot*\n\n"
        "Welcome to the Movie Bot, your go-to place to watch movies directly inside Telegram!\n"
        "This bot offers a seamless movie-watching experience with a built-in movie player, "
        "which opens directly within the Telegram app as a Mini App.\n\n"
        "*Features:*\n"
        "• Play movies directly in Telegram using the integrated Mini App.\n"
        "• View your user details with the /info command.\n"
        "• Learn more about us with the /about command.\n\n"
        "*About Us:*\n"
        "This bot is developed and maintained by SafeSecureAudit, a cybersecurity company providing automated website security tools.\n"
        "Visit us at: [SafeSecureAudit](https://safesecureaudit.com)\n\n"
        "The bot is created and owned by @indcrypt.\n\n"
        "👉 Stay tuned for more updates and features coming soon! 🚀"
        "Supported by @TNT_HUB_0 and @hackingrecordings"
    )
    bot.send_message(message.chat.id, about_text, parse_mode="Markdown")

@bot.message_handler(commands=['terabox'])
def terabox(message):

    movie_url = f"https://ashlynnterabox.netlify.app"

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎬 Open Movie Player", url=movie_url
        )
    )
    bot.reply_to(
        message,
        f"Click below to start the movie player with custom size:\n\n🎬 Enjoy your streaming!",
        reply_markup=markup
    )


# Start polling to check for incoming messages
if __name__ == "__main__":
    bot.polling(non_stop=True)
