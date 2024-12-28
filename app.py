import os
import sys
import random
import logging
import re
import time
from collections import defaultdict
from threading import Thread
import telebot
import instaloader
from flask import Flask
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')


def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run_flask_app)
    t.start()

# Start the Flask app in a thread
keep_alive()

API_TOKEN="7823631612:AAHBFokBpoQGxKo6KTbUoVL-JE95R649uPA"
ADMIN_ID="1539505459"


bot = telebot.TeleBot(API_TOKEN)

# In-memory list to store user IDs
user_ids = set()

def add_user(user_id):
    user_ids.add(user_id)

def remove_user(user_id):
    user_ids.discard(user_id)

def get_all_users():
    return list(user_ids)

# List of keywords for different report categories
report_keywords = {
    "HATE": ["devil", "666", "savage", "love", "hate", "followers", "selling", "sold", "seller", "dick", "ban", "banned", "free", "method", "paid",
             "kill", "gand", "murder", "basterd", "motherfucker", "fucker", "chud", "fucked", "fucks", "दुश्मन", "slut", "shit", "shitty", "people", 
             "enemy", "chut", "chudegi", "chudega", "lund", "choot", "land", "gun", "fire", "firearms", "madarchod", "teri maa ki chut", "baap", 
             "teri behan ki gand", "behanchod", "bhosda", "chutiya", "hacking", "carding", "jacking", "abuse", "666", "devil", "emperor", "hitler", 
             "chuda", "bhosdike", "bhosdi ke"],
    "SELF": ["suicide", "blood", "death", "dead", "kill myself", "suicide", "murder", "harm", "harmful", "hurt", "knife", "attack", "marwa","sword", 
             "कातिल", "chud", "warn", "बहिनचोद", "गांड", "लंड", "चूत", "भोसड़ा", "मादरचोद", "मादर चोद", "बिच", "चुतीया", "रण्डी", "teri maa chod dunga", 
             "teri mummy chod dunga", "maa chuda", "gand marwa", "gand mrwa", "gaand", "chudle fer", "chod dunga"],
    "BULLY": ["@", "bullying", "bully", "me", "you", "harassment", "insult", "दुश्मन", "fuck", "dick", "kill", "chudegi", "jhaatu", "jhaantu", "jhantu", 
               "chudega", "suicide", "hack", "warn", "warning", "aware", "teri maa chod dunga", "teri mummy chod dunga", "maa chuda", "gand marwa", "gand mrwa", 
               "gaand", "chudle fer", "chod dunga"],
    "VIOLENT": ["hitler", "osama bin laden", "guns", "soldiers", "masks", "flags", "kill", "fuck", "dick", "hitler", "war", "fight", "plane", "murder", "attack", 
                "chudoge", "soja", "aeroplane", "chud", "chudoge", "hijda", "fucker", "fucks", "slut", "slave", "pervert", "hijde", "जंग", "dicky", "manipulate", 
                "manipulative", "violence", "sex", "slapper", "porn", "nudes", "chuda", "randi", "raand", "rand", "kamini", "kamina", "randibaazi", "chutmari", 
                "बहिनचोद", "गांड", "लंड", "चूत", "भोसड़ा", "मादरचोद", "मादर चोद", "बिच", "चुतीया", "रण्डी"],
    "ILLEGAL": ["drugs", "cocaine", "plants", "trees", "medicines", "scam", "qr code", "drugs", "hitler", "gun", "guns", "kill animals", "cow", "dung", 
                "dog", "dinosaur", "cheetah", "dodo"],
    "PRETENDING": ["verified", "tick"],
    "NUDITY": ["nude", "sex", "send nudes", "nude", "porn", "sex", "fuck", "dick", "pussy", "sexy", "cleavage", "nangi", "nanga", "naked", "rape", "lust", 
               "meme", "sticker", "stickers", "private"],
    "SPAM": ["phone number", "chut", "lund", "teri maa kaa bhosda", "chutiye", "bitch", "tera baap", "teri behan", "chod dunga", "maar dunga", "feel kar apne baap ko"],
    "SCAM": ["scam", "bully", "fraud", "racist", "money", "paisa", "qr code", "soja", "hijde", "hijda", "chut", "lund", "fuck", "fucks", "fucked", "dick", 
             "rupees", "rupee", "dhokha", "dagabaj", "dhokhebaj", "dhokhebaaj", "carding", "hacking", "gun", "chuda", "randi", "raand", "rand", "kamini", 
             "kamina", "randibaazi", "chutmari", "bhosdike", "bhosdi ke", "meme", "sticker", "stickers", "bloody", "private", "बहिनचोद", "गांड", "लंड", 
             "चूत", "भोसड़ा", "मादरचोद", "मादर चोद", "बिच", "चुतीया", "रण्डी"],
    "VIOLENCE": ["kill", "fuck", "dick", "hitler", "war", "fight", "plane", "murder", "attack", "chudoge", "soja", "aeroplane", "chud", "chudoge", "hijda", 
                "fucker", "fucks", "slut", "slave", "pervert", "hijde", "जंग", "dicky", "manipulate", "manipulative", "violence", "sex", "slapper", "porn", 
                "nudes", "chuda", "randi", "raand", "rand", "kamini", "kamina", "randibaazi", "chutmari", "बहिनचोद", "गांड", "लंड", "चूत", "भोसड़ा", 
                "मादरचोद", "मादर चोद", "बिच", "चुतीया", "रण्डी"]
}

def check_keywords(text, keywords):
    return any(keyword in text.lower() for keyword in keywords)

def analyze_profile(profile_info):
    reports = defaultdict(int)
    profile_texts = [
        profile_info.get("username", ""),
        profile_info.get("biography", ""),
    ]

    for text in profile_texts:
        for category, keywords in report_keywords.items():
            if check_keywords(text, keywords):
                reports[category] += 1

    if reports:
        unique_counts = random.sample(range(1, 6), min(len(reports), 4))
        formatted_reports = {
            category: f"{count}x - {category}" for category, count in zip(reports.keys(), unique_counts)
        }
    else:
        all_categories = list(report_keywords.keys())
        num_categories = random.randint(2, 5)
        selected_categories = random.sample(all_categories, num_categories)
        unique_counts = random.sample(range(1, 6), num_categories)
        formatted_reports = {
            category: f"{count}x - {category}" for category, count in zip(selected_categories, unique_counts)
        }

    return formatted_reports

def get_public_instagram_info(username):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        info = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "follower_count": profile.followers,
            "following_count": profile.followees,
            "is_private": profile.is_private,
            "post_count": profile.mediacount,
            "external_url": profile.external_url,
        }
        return info
    except instaloader.exceptions.ProfileNotExistsException:
        return None
    except instaloader.exceptions.InstaloaderException as e:
        logging.error(f"An error occurred: {e}")
        return None

def escape_markdown_v2(text):
    replacements = {
        '_': r'\_', '*': r'\*', '[': r'\[', ']': r'\]',
        '(': r'\(', ')': r'\)', '~': r'\~', '`': r'\`',
        '>': r'\>', '#': r'\#', '+': r'\+', '-': r'\-',
        '=': r'\=', '|': r'\|', '{': r'\{', '}': r'\}',
        '.': r'\.', '!': r'\!'
    }
    pattern = re.compile('|'.join(re.escape(key) for key in replacements.keys()))
    return pattern.sub(lambda x: replacements[x.group(0)], text)


@bot.message_handler(commands=['help'])
def help(message):
    help_text = (
        "👨‍💻 *SafeSecureAudit Instagram Profile Scanner Bot*\n\n"
        "This bot allows you to analyze Instagram profiles for potential security concerns.\n\n"
        "Commands:\n"
        "/start - Start the bot and receive a welcome message.\n"
        "/getban <username> - Scan an Instagram profile and receive a report on potential issues.\n"
        "Features: support safesecureaudit.com\n"
        "• Checks Instagram profiles for keywords related to abusive or suspicious content.\n"
        "• Provides detailed analysis on publicly available information, including biography, follower count, and post details.\n"
        "• Generates a report based on keyword analysis and profile details.\n\n"
        "👉 *Usage example*:\n"
        "/getban username\n"
        "Just replace 'username' with the Instagram handle you want to check.\n\n"
        "*Important:* The bot analyzes public Instagram profiles, and its accuracy may vary based on the information available."
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    add_user(user_id)  # Add user to the list
    markup = telebot.types.InlineKeyboardMarkup()
    bot.reply_to(message, "Welcome! Use /getban <username> to analyze an Instagram profile.<br>Welcome! Use /help to analyze an Instagram profile.", reply_markup=markup)

@bot.message_handler(commands=['getban'])
def analyze(message):
    username = message.text.split()[1:]  # Get username from command
    if not username:
        bot.reply_to(message, "😾 Wrong method. Use: /getban <username>")
        return

    username = ' '.join(username)
    bot.reply_to(message, f"🔍 Scanning Your Target Profile: {username}. Please wait...")

    profile_info = get_public_instagram_info(username)
    if profile_info:
        reports_to_file = analyze_profile(profile_info)
        result_text = f"**Public Information for {username}:**\n"
        result_text += f"Username: {profile_info.get('username', 'N/A')}\n"
        result_text += f"Full Name: {profile_info.get('full_name', 'N/A')}\n"
        result_text += f"Biography: {profile_info.get('biography', 'N/A')}\n"
        result_text += f"Followers: {profile_info.get('follower_count', 'N/A')}\n"
        result_text += f"Following: {profile_info.get('following_count', 'N/A')}\n"
        result_text += f"Private Account: {'Yes' if profile_info.get('is_private') else 'No'}\n"
        result_text += f"Posts: {profile_info.get('post_count', 'N/A')}\n"
        result_text += f"External URL: {profile_info.get('external_url', 'N/A')}\n\n"
        result_text += "Suggested Reports for Your Target:\n"
        result_text += "follow us on safesecureaudit.com\n"
        for report in reports_to_file.values():
            result_text += f"• {report}\n"
        result_text += "\n*Note: This method is based on available data and may not be fully accurate.*\n"

        result_text = escape_markdown_v2(result_text)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Visit Profile", url=f"https://instagram.com/{profile_info['username']}"))
        bot.send_message(message.chat.id, result_text, reply_markup=markup, parse_mode='MarkdownV2')
    else:
        bot.reply_to(message, f"❌ Profile {username} not found or an error occurred.")

@bot.message_handler(commands=['movie'])
def movie(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎬 Open Movie Player", url="https://canidiscover.github.io/Movie/"
        )
    )
    bot.reply_to(
        message,
        "Click below to start the movie player directly in Telegram:\n\n🎬 Enjoy your streaming!",
        reply_markup=markup
    )


if __name__ == "__main__":
    def start_bot_polling():
        while True:
            try:
                bot.polling(non_stop=True)
            except Exception as e:
                logging.error(f"Polling error: {e}")
                time.sleep(5)

    t = Thread(target=start_bot_polling, daemon=True)
    t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBot shutting down...")
        logging.info("Bot stopped by user.")
