
API_TOKEN="7823631612:AAHBFokBpoQGxKo6KTbUoVL-JE95R649uPA"
import telebot
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['movie'])
def movie(message):
    # This is the movie URL that will trigger the Telegram mini player
    movie_url = "https://canidiscover.github.io/Movie/"  # Replace with your movie URL or video link

    # Create the inline keyboard to send the link
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎬 Open Movie Player", url=movie_url
        )
    )
    
    # Send the message with the link to the mini player
    bot.reply_to(
        message,
        "Click below to start the movie player directly in Telegram:\n\n🎬 Enjoy your streaming!",
        reply_markup=markup
    )

if __name__ == "__main__":
    bot.polling(non_stop=True)

