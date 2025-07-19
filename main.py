import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import requests
from info import Config

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    welcome_msg = (
        f"👋 Hello {user.mention_html()}!\n\n"
        "Welcome to Movie Search Bot!\n\n"
        "🔍 Just send me the name of a movie or series you're looking for "
        "and I'll search it for you!"
    )
    await update.message.reply_html(welcome_msg)

async def search_movie(update: Update, context: CallbackContext) -> None:
    """Handle movie search requests."""
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("Please enter a movie/series name to search.")
        return
    
    try:
        response = requests.get(
            Config.API_BASE_URL,
            params={"query": query},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data["total_results"] == 0:
            await update.message.reply_text("No results found. Try a different search term.")
            return
            
        for result in data["results"]:
            caption = (
                f"🎬 <b>{result['title']}</b> ({result['year']})\n"
                f"📌 <b>Genre:</b> {result['genre']}\n"
                f"🌐 <b>Language:</b> {result['language']}\n\n"
                f"📝 <b>Description:</b> {result['description']}"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔗 Watch Here", url=result["postLink"])]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Try to send photo with caption, fallback to text message if photo fails
            try:
                await update.message.reply_photo(
                    photo=result["posterUrl"],
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except Exception as photo_error:
                logger.error(f"Error sending photo: {photo_error}")
                await update.message.reply_text(
                    caption,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        await update.message.reply_text("Sorry, there was an error processing your request. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again.")

def main() -> None:
    """Start the bot."""
    if not Config.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set")
    
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_movie))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
