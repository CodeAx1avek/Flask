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
    app.run(host='0.0.0.0', port=8080)

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
    "HATE": ["devil", "666", "savage", "love", "hate", "followers", "selling", "sold", "seller", "dick", "ban", "banned", "free", "method", "paid"],
    "SELF": ["suicide", "blood", "death", "dead", "kill myself"],
    "BULLY": ["@"],
    "VIOLENT": ["hitler", "osama bin laden", "guns", "soldiers", "masks", "flags"],
    "ILLEGAL": ["drugs", "cocaine", "plants", "trees", "medicines"],
    "PRETENDING": ["verified", "tick"],
    "NUDITY": ["nude", "sex", "send nudes"],
    "SPAM": ["phone number"]
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

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    add_user(user_id)  # Add user to the list
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Help", callback_data='help'))
    bot.reply_to(message, "Welcome! Use /getmeth <username> to analyze an Instagram profile.", reply_markup=markup)

@bot.message_handler(commands=['getmeth'])
def analyze(message):
    username = message.text.split()[1:]  # Get username from command
    if not username:
        bot.reply_to(message, "😾 Wrong method. Use: /getmeth <username>")
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
