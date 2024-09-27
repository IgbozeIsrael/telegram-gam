import telebot
import random
import pymongo
import string
import secrets

# Replace with your Telegram Bot API token
BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)

# Connect to MongoDB database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["jigsaw_game"]
users_collection = db["users"]

# Puzzle generation and handling
def generate_puzzle(image_path):
    # Implement image processing logic to divide the image into pieces
    # ...
    pieces = ["piece1.jpg", "piece2.jpg", "piece3.jpg", ...]  # Example
    correct_order = ["piece2", "piece1", "piece3"]  # Example
    return pieces, correct_order

def send_puzzle(chat_id, pieces):
    for piece in pieces:
        bot.send_photo(chat_id, open(piece, 'rb'))

# User input and game logic
def handle_user_input(message):
    chat_id = message.chat.id
    text = message.text
    user_id = message.from_user.id

    if text.startswith("/play"):
        pieces, correct_order = generate_puzzle("puzzle_image.jpg")
        send_puzzle(chat_id, pieces)
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"current_puzzle": correct_order}},
            upsert=True
        )

    elif text.startswith("/submit"):
        user_order = text.split()[1:]
        user_data = users_collection.find_one({"user_id": user_id})
        if user_data and user_data["current_puzzle"] == user_order:
            # Award points and update leaderboard
            users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"score": 10}}
            )
            bot.send_message(chat_id, "Congratulations! You solved the puzzle.")
        else:
            bot.send_message(chat_id, "Incorrect. Try again.")

# Leaderboard
def get_leaderboard():
    leaderboard = users_collection.find().sort("score", -1).limit(10)
    leaderboard_text = "Leaderboard:\n"
    for user in leaderboard:
        leaderboard_text += f"{user['username']}: {user['score']}\n"
    return leaderboard_text

# Referral system
def generate_referral_link(user_id):
    referral_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"referral_code": referral_code}}
    )
    return f"https://yourgame.com/refer?code={referral_code}"

# Bot handlers
@bot.message_handler(commands=["start", "help"])
def send_help(message):
    help_text = """
    Welcome to the Jigsaw Puzzle Game!

    Commands:
    /play - Start a new puzzle
    /leaderboard - View the leaderboard
    /refer - Get your referral link
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    handle_user_input(message)

# Start the bot
bot.polling()