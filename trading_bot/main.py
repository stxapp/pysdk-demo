import logging

from stxsdk.exceptions import AuthenticationFailedException

from trading_bot.bot import TradingBot

logger = logging.getLogger(__file__)


def initiate_bot():
    try:
        print("Initiating the Trading Bot.")
        email = input("Please enter email address: ")
        password = input("Please enter password: ")
        # creating the trading bot object
        bot = TradingBot(email, password)
        # initiating the bot to start the defined routines
        bot.initiate()
    # the bot first authenticate the user then starts its defined routines
    # this handles the authentication failure exception in case if the
    # provided credentials are invalid
    except AuthenticationFailedException as exc:
        logger.exception(str(exc))
    # it handles any other general exception raised during the process
    except Exception as exc:
        logger.exception(str(exc))


# It's the start of the file, this commands represents that this file will execute from here
if __name__ == "__main__":
    initiate_bot()
