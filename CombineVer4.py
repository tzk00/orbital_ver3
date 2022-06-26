#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import math
import json
import logging
import time

from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    CallbackContext,
)
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
from requests.adapters import HTTPAdapter

from random import randint


import telebot
from telebot import types
from telebot import util

proxy = None
session = None

API_URL = None
FILE_URL = None

CONNECT_TIMEOUT = 15
READ_TIMEOUT = 30

LONG_POLLING_TIMEOUT = 10 # Should be positive, short polling should be used for testing purposes only (https://core.telegram.org/bots/api#getupdates)

SESSION_TIME_TO_LIVE = 600  # In seconds. None - live forever, 0 - one-time

RETRY_ON_ERROR = False
RETRY_TIMEOUT = 2
MAX_RETRIES = 15
RETRY_ENGINE = 1

CUSTOM_SERIALIZER = None
CUSTOM_REQUEST_SENDER = None

ENABLE_MIDDLEWARE = False

token = '5546411933:AAG_5VKCoJG2AyrCaNpj3jm9cpoltzIpm_4'

### DATASETS ###
USERS = []
USERS_DATA = {}
LOCATION = []
CUISINES_SELECTED = []
BUDGET_SELECTED = []
NUMBER_OF_PEOPLE = 0
types_cuisine = ["Chinese", "Japanese", "Thai", "European", "Indian", "Vegetarian"]
types_budget = ["$", "$$", "$$$"]
SAMPLE_DATABASE = [['Li Bai Cantonese Restaurant', '4.4', '39 Scotts Rd, Sheraton Towers Singapore, Singapore 228230', '228230', 'Chinese', '$$$'], ['Joie', '4.5', '181 Orchard Rd, #12 - 01, Singapore 238896', '238896', 'Vegetarian', '$$$'], ['Grand Shanghai Restaurant', '4.2', "390 Havelock Rd, Level 1 King's Centre, Singapore 169662", '169662', 'Chinese', '$$$'], ['Swee Choon Tim Sum Restaurant', '4.2', '183/185/187/189, Jln Besar, 191/193, 208882', '208882', 'chinese', '$$'], ['Tenya Orchard Central', '4.3', '181 Orchard Rd, #B1-01 Orchard Central, Singapore 238896', '238896', 'Japanese', '$$'], ['Yan Restaurant at National Gallery Singapore 宴中餐馆', '4.1', "1 Saint Andrew's Road #05-02 National Gallery, Singapore 178957", '178957', 'Chinese', '$$$'], ['Blue Jasmine', '4', '10 Farrer Park Station Rd, Level 5 Holiday Inn Singapore, Singapore 217564', '217564', 'Thai', '$$'], ['Empress', '4.3', '1 Empress Pl, #01-03 Asian Civilisations Museum, Singapore 179555', '179555', 'Chinese', '$$$'], ['Dong Bei Xiao Chu', '4.4', '12 Upper Cross St, Singapore 058329', '058329', 'Chinese', '$$'], ['Wah Lok Cantonese Restaurant', '4.4', '76 Bras Basah Rd, Singapore 189558', '189558', 'Chinese', '$$$'], ['The Masons Table', '4.4', '23A Coleman St, Singapore 179806', '179806', 'Restaurant', '$$'], ['Botan, Pekin Street', '4.2', '37 Pekin St, #01-01 Far East Square, Singapore 048767', '048767', 'Japanese', '$$'], ['Nalan Restaurant (City Hall)', '4', '13 Stamford Rd, #B2-54 Capitol Singapore, Singapore 178905', '178905', 'Vegetarian', '$$'], ['Shiv Sagar Veg. Restaurant', '3.6', '172 Race Course Rd, Singapore 218605', '218605', 'Vegetarian', '$$'], ['Zam Zam Restaurant, Singapore', '4.2', '697-699 North Bridge Rd, Singapore 198675', '198675', 'Indian', '$'], ['Imperial Treasure Cantonese Cuisine', '4.3', '02-112, 1 Kim Seng Promenade, Great World, 237994', '237994', 'Chinese', '$$$'], ['Komala Vilas Restaurant, Singapore', '4.2', '76-78 Serangoon Rd, Singapore 217981', '217981', 'Vegetarian', '$$'], ['Misaki', '4.4', '12 Marina Blvd, #01-01, Singapore 018982', '018982', 'Japanese', '$$'], ['Poulet + Brasserie - ION Orchard', '4.8', '2 Orchard Turn, #B3-21 ION Orchard, 238801', '238801', 'European', '$$'], ['Cherry Garden', '4.4', '5 Raffles Ave, Singapore 039797', '039797', 'Chinese', '$$$'], ['SUN with MOON Japanese Dining & Cafe', '4.3', '501 Orchard Rd, #03 -15 Wheelock Place, Singapore 238880', '238880', 'Japanese', '$$'], ['Imperial Treasure Super Peking Duck', '4.4', '05-42/45, Paragon, 290 Orchard Rd, 238859', '238859', 'Chinese', '$$$'], ['Peach Garden', '3.7', '65 Chulia St, #33 floor, 01, Singapore 049513', '049513', 'Chinese', '$$$'], ['Imperial Treasure Steamboat Restaurant', '4.1', '2 Orchard Turn, #04-12A ION Orchard, Singapore 238801', '238801', 'Chinese', '$$$'], ['Da Luca Italian Restaurant', '4.3', 'Goldhill Plaza #01-19/21, #1, Singapore 308899', '308899', 'European', '$$$'], ['Treasures Yi Dian Xin', '4.3', 'B1-37, Raffles City Shopping Centre, 252 North Bridge Rd, 179103', '179103', 'Chinese', '$$$'], ['Herbivore', '4.4', '190 Middle Rd, #01-13/14 Fortune Centre, Singapore 188979', '188979', 'Vegetarian', '$$$'], ['Kai Garden (Marina Square)', '4.3', '6 Raffles Boulevard #03-128A/128B, 039594', '039594', 'Chinese', '$$$'], ['Swatow Seafood', '3.9', '181 Lor 4 Toa Payoh, #02-602, Singapore 310181', '310181', 'Chinese', '$$'], ['itadakimasu by PARCO', '3.9', '100 Tras St, #02-10/11, #03 - 10 to 15 and #03 - K1, 079027', '079027', 'Japanese', '$$'], ['Cassia', '4.7', '1 The Knolls, Sentosa Island, 098297', '098297', 'Chinese', '$$$'], ['Crystal Jade Dining IN', '4.1', '11 HarbourFront Walk, #01-112 VivoCity, Singapore 098585', '098585', 'Chinese', '$$'], ['Ichiban Sushi (Toa Payoh)', '3.7', '490 #01-12 Lor 6 Toa Payoh, HDB Hub, Singapore 310493', '310493', 'Japanese', '$$'], ['Whampoa Keng Fish Head Steamboat @ Balestier', '4.1', '556 Balestier Rd, Singapore 329872', '329872', 'Restaurant', '$$'], ['Beng Hiang Restaurant', '3.9', '135 Jurong Gateway Rd, #02-337, Singapore 600135', '600135', 'Chinese', '$$'], ['Donya Japanese Cuisine @ TOA PAYOH 126', '3.5', '126 Lor 1 Toa Payoh, Singapore 310126', '310126', 'Japanese', '$'], ['Real Food, Orchard Central', '4.1', '181 Orchard Rd, #02-16 to 19, Singapore 238896', '238896', 'Vegetarian', '$$']]


### FUNCTIONS ###

def count_num(thing, chosen_list):
  num = 0
  for i in chosen_list:
    if i == thing:
      num += 1

  return num

#final_selection have not accounted for what if both choices got same num of selection#

def final_selection(choices_list, chosen_list):
  dic = {}
  for i in choices_list:
    dic[i] = count_num(i, chosen_list)

  largest = 0
  final = ""
  for key, val in dic.items():
    if val > largest:
      largest = val
      final = key

  return final

def _get_req_session(reset=False):
    if SESSION_TIME_TO_LIVE:
        # If session TTL is set - check time passed
        creation_date = util.per_thread('req_session_time', lambda: datetime.now(), reset)
        # noinspection PyTypeChecker
        if (datetime.now() - creation_date).total_seconds() > SESSION_TIME_TO_LIVE:
            # Force session reset
            reset = True
            # Save reset time
            util.per_thread('req_session_time', lambda: datetime.now(), True)

    if SESSION_TIME_TO_LIVE == 0:
        # Session is one-time use
        return requests.sessions.Session()
    else:
        # Session lives some time or forever once created. Default
        return util.per_thread('req_session', lambda: session if session else requests.sessions.Session(), reset)


def _make_request(token, method_name, method='get', params=None, files=None):
    """
    Makes a request to the Telegram API.
    :param token: The bot's API token. (Created with @BotFather)
    :param method_name: Name of the API method to be called. (E.g. 'getUpdates')
    :param method: HTTP method to be used. Defaults to 'get'.
    :param params: Optional parameters. Should be a dictionary with key-value pairs.
    :param files: Optional files.
    :return: The result parsed to a JSON dictionary.
    """
    if not token:
        raise Exception('Bot token is not defined')
    if API_URL:
        # noinspection PyUnresolvedReferences
        request_url = API_URL.format(token, method_name)
    else:
        request_url = "https://api.telegram.org/bot{0}/{1}".format(token, method_name)

    logger.debug("Request: method={0} url={1} params={2} files={3}".format(method, request_url, params, files).replace(token, token.split(':')[0] + ":{TOKEN}"))
    read_timeout = READ_TIMEOUT
    connect_timeout = CONNECT_TIMEOUT
    if files and format_header_param:
        fields.format_header_param = _no_encode(format_header_param)
    if params:
        if 'timeout' in params:
            read_timeout = params.pop('timeout')
            connect_timeout = read_timeout
        if 'long_polling_timeout' in params:
            # For getUpdates. It's the only function with timeout parameter on the BOT API side
            long_polling_timeout = params.pop('long_polling_timeout')
            params['timeout'] = long_polling_timeout
            # Long polling hangs for a given time. Read timeout should be greater that long_polling_timeout
            read_timeout = max(long_polling_timeout + 5, read_timeout)

    params = params or None # Set params to None if empty
    result = None
    if RETRY_ON_ERROR and RETRY_ENGINE == 1:
        got_result = False
        current_try = 0
        while not got_result and current_try<MAX_RETRIES-1:
            current_try+=1
            try:
                result = _get_req_session().request(
                    method, request_url, params=params, files=files,
                    timeout=(connect_timeout, read_timeout), proxies=proxy)
                got_result = True
            except HTTPError:
                logger.debug("HTTP Error on {0} method (Try #{1})".format(method_name, current_try))
                time.sleep(RETRY_TIMEOUT)
            except ConnectionError:
                logger.debug("Connection Error on {0} method (Try #{1})".format(method_name, current_try))
                time.sleep(RETRY_TIMEOUT)
            except Timeout:
                logger.debug("Timeout Error on {0} method (Try #{1})".format(method_name, current_try))
                time.sleep(RETRY_TIMEOUT)
        if not got_result:
            result = _get_req_session().request(
                    method, request_url, params=params, files=files,
                    timeout=(connect_timeout, read_timeout), proxies=proxy)
    elif RETRY_ON_ERROR and RETRY_ENGINE == 2:
        http = _get_req_session()
        # noinspection PyUnresolvedReferences
        retry_strategy = requests.packages.urllib3.util.retry.Retry(
            total=MAX_RETRIES,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        for prefix in ('http://', 'https://'):
            http.mount(prefix, adapter)
        result = http.request(
            method, request_url, params=params, files=files,
            timeout=(connect_timeout, read_timeout), proxies=proxy)
    elif CUSTOM_REQUEST_SENDER:
        # noinspection PyCallingNonCallable
        result = CUSTOM_REQUEST_SENDER(
            method, request_url, params=params, files=files,
            timeout=(connect_timeout, read_timeout), proxies=proxy)
    else:
        result = _get_req_session().request(
            method, request_url, params=params, files=files,
            timeout=(connect_timeout, read_timeout), proxies=proxy)
    
    logger.debug("The server returned: '{0}'".format(result.text.encode('utf8')))
    
    json_result = _check_result(method_name, result)
    if json_result:
        return json_result['result']

def _check_result(method_name, result):
    """
    Checks whether `result` is a valid API response.
    A result is considered invalid if:
        - The server returned an HTTP response code other than 200
        - The content of the result is invalid JSON.
        - The method call was unsuccessful (The JSON 'ok' field equals False)
    :raises ApiException: if one of the above listed cases is applicable
    :param method_name: The name of the method called
    :param result: The returned result of the method request
    :return: The result parsed to a JSON dictionary.
    """
    try:
        result_json = result.json()
    except:
        if result.status_code != 200:
            raise ApiHTTPException(method_name, result)
        else:
            raise ApiInvalidJSONException(method_name, result)
    else:    
        if not result_json['ok']:
            raise ApiTelegramException(method_name, result, result_json)
            
        return result_json


def get_chat_member_count(selected_token, chat_id):
    method_url = r'getChatMemberCount'
    payload = {'chat_id': chat_id}
    return _make_request(selected_token, method_url, params=payload)

### LATITUDE AND LONGDITUDE BASED ON POSTAL CODE ###
def get_lat_lon(postal):
    response = requests.get(f'http://dev.virtualearth.net/REST/v1/Locations/SG/{postal}?key=AkIB6ZipHktncZiBRp2PKZlbcdl1wlen0reP9vT22iWi5X6-s89T4KEvWjFAY7m2')
    data = json.loads(response.text)
    return data['resourceSets'][0]['resources'][0]['geocodePoints'][0]['coordinates']

def get_confidence(postal):
    response = requests.get(f'http://dev.virtualearth.net/REST/v1/Locations/SG/{postal}?key=AkIB6ZipHktncZiBRp2PKZlbcdl1wlen0reP9vT22iWi5X6-s89T4KEvWjFAY7m2')
    data = json.loads(response.text)
    return data['resourceSets'][0]['resources'][0]['confidence']



def rad(x):
    return x * math.pi / 180.0;

def getHaversineDistance(p1, p2):
    R = 6378137; # Earth’s mean radius in meter
    dLat = rad(p2[0] - p1[0]);
    dLong = rad(p2[1] - p1[1]);
    a = (math.sin(dLat / 2) * math.sin(dLat / 2) +
        math.cos(rad(p1[0])) * math.cos(rad(p2[0])) *
        math.sin(dLong / 2) * math.sin(dLong / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c #
    return d # // returns the distance in meter

def centralLocation(locationLst):
    latLst = list(map(lambda x : get_lat_lon(x)[0], locationLst))
    centralLat = sum(latLst)/len(latLst)
    lonLst = list(map(lambda x : get_lat_lon(x)[1], locationLst))
    centralLon = sum(lonLst)/len(lonLst)
    return [centralLat, centralLon]


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND, THIRD, FOURTH = range(4)
# Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, ELEVEN = range(11)

def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    user_id = update.message.from_user.username
    USERS.append(user_id)
    if user_id not in USERS_DATA:
        USERS_DATA[user_id] = [[], [], [], [], []]
        context.bot.send_message(chat_id=update.effective_chat.id, text = "Enter your age:")
        return THIRD
    if get_chat_member_count(token, update.effective_chat.id) - 1 == 1:
        keyboard = [
            [ 
                InlineKeyboardButton("I like to make decisions", callback_data=str(TEN)),
                InlineKeyboardButton("I'm lazy", callback_data=str(ELEVEN)),  
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send message with text and appended InlineKeyboard
        update.message.reply_text("Choose an option", reply_markup=reply_markup)
        return FIRST
    keyboard = [
        [
            InlineKeyboardButton("Chinese", callback_data=str(ONE)),
            InlineKeyboardButton("Japanese", callback_data=str(TWO)),
            InlineKeyboardButton("Thai", callback_data=str(THREE)),
            InlineKeyboardButton("European", callback_data=str(FOUR)),
            InlineKeyboardButton("Indian", callback_data=str(FIVE)),
            InlineKeyboardButton("Vegetarian", callback_data=str(SIX)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Choose a cuisine", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST
    
     

def ten(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Chinese", callback_data=str(ONE)),
            InlineKeyboardButton("Japanese", callback_data=str(TWO)),
            InlineKeyboardButton("Thai", callback_data=str(THREE)),
            InlineKeyboardButton("European", callback_data=str(FOUR)),
            InlineKeyboardButton("Indian", callback_data=str(FIVE)),
            InlineKeyboardButton("Vegetarian", callback_data=str(SIX)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    query.edit_message_text(
        text="Choose a cuisine", reply_markup=reply_markup
    )
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST

def user_age(update: Update, context: CallbackContext) ->  int:
    user_id = USERS[-1]
    if int(update.message.text) > 100:
        context.bot.send_message(chat_id=update.effective_chat.id, text = "Please enter a valid age")
        return THIRD
    USERS_DATA[user_id][0] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text = "Male/Female")
    return FOURTH

def user_gender(update: Update, context: CallbackContext) -> int:
    user_id = USERS[-1]
    USERS_DATA[user_id][1] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text = "Proceed? Y/N")
    return FIRST
    
def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return FIRST


def one(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    CUISINES_SELECTED.append("Chinese")
    user_id = USERS[-1]
    USERS_DATA[user_id][2].append("Chinese")
    query = update.callback_query
    print(query.message.from_user.username)
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$", callback_data=str(SEVEN)),
            InlineKeyboardButton("$$", callback_data=str(EIGHT)),
            InlineKeyboardButton("$$$", callback_data=str(NINE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You chose Chinese. Next choose a budget", reply_markup=reply_markup
    )
    return FIRST


def two(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    CUISINES_SELECTED.append("Japanese")
    user_id = USERS[-1]
    USERS_DATA[user_id][2].append("Japanese")
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$", callback_data=str(SEVEN)),
            InlineKeyboardButton("$$", callback_data=str(EIGHT)),
            InlineKeyboardButton("$$$", callback_data=str(NINE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You chose Japanese. Next choose a budget", reply_markup=reply_markup
    )
    return FIRST

def three(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    CUISINES_SELECTED.append("Thai")
    user_id = USERS[-1]
    USERS_DATA[user_id][2].append("Thai")
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$", callback_data=str(SEVEN)),
            InlineKeyboardButton("$$", callback_data=str(EIGHT)),
            InlineKeyboardButton("$$$", callback_data=str(NINE)),
            
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You chose Thai. Next choose a budget", reply_markup=reply_markup
    )
    return FIRST

def four(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    CUISINES_SELECTED.append("European")
    user_id = USERS[-1]
    USERS_DATA[user_id][2].append("European")
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$", callback_data=str(SEVEN)),
            InlineKeyboardButton("$$", callback_data=str(EIGHT)),
            InlineKeyboardButton("$$$", callback_data=str(NINE)),
            
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You chose European. Next choose a budget", reply_markup=reply_markup
    )
    return FIRST

def five(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    CUISINES_SELECTED.append("Indian")
    user_id = USERS[-1]
    USERS_DATA[user_id][2].append("Indian")
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$", callback_data=str(SEVEN)),
            InlineKeyboardButton("$$", callback_data=str(EIGHT)),
            InlineKeyboardButton("$$$", callback_data=str(NINE)),
            
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You chose Indian. Next choose a budget", reply_markup=reply_markup
    )
    return FIRST

def six(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    CUISINES_SELECTED.append("Vegetarian")
    user_id = USERS[-1]
    USERS_DATA[user_id][2].append("Vegetarian")
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("$", callback_data=str(SEVEN)),
            InlineKeyboardButton("$$", callback_data=str(EIGHT)),
            InlineKeyboardButton("$$$", callback_data=str(NINE)),
            
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="You chose Vegetarian. Next choose a budget", reply_markup=reply_markup
    )
    return FIRST


def seven(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    BUDGET_SELECTED.append("$")
    user_id = USERS[-1]
    USERS_DATA[user_id][3].append("$")
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Enter your postal code"
    )
    # Transfer to conversation state `SECOND`
    return SECOND


def eight(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    BUDGET_SELECTED.append("$$")
    user_id = USERS[-1]
    USERS_DATA[user_id][3].append("$$")
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Enter your postal code"
    )
    return SECOND

def nine(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    BUDGET_SELECTED.append("$$$")
    user_id = USERS[-1]
    USERS_DATA[user_id][3].append("$$$")
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Enter your postal code"
    )
    return SECOND

def resetCommand(update: Update, context: CallbackContext):
    LOCATION.clear()
    CUISINES_SELECTED.clear()
    BUDGET_SELECTED.clear()
    context.bot.send_message(chat_id=update.effective_chat.id, text = "reset")

def eleven(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    recommendation = SAMPLE_DATABASE[randint(0,len(SAMPLE_DATABASE))][2]
    context.bot.send_message(chat_id=update.effective_chat.id, text = f"{recommendation}")
    LOCATION.clear()
    CUISINES_SELECTED.clear()
    BUDGET_SELECTED.clear()
    return ConversationHandler.END
    

def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    if get_confidence(f"{update.message.text}") != 'High' or int(update.message.text[:2]) > 80 or len(update.message.text) != 6:
      context.bot.send_message(chat_id=update.effective_chat.id, text = "Postal code not found! Please enter a valid postal code")
      return SECOND    
    LOCATION.append(f"{update.message.text}")
    user_id = USERS[-1]
    USERS_DATA[user_id][4].append(f"{update.message.text}")
    context.bot.send_message(chat_id=update.effective_chat.id, text = "Thank you")
    if len(BUDGET_SELECTED) == get_chat_member_count(token, update.effective_chat.id) - 1:
        try:
            final_cuisine = final_selection(types_cuisine, CUISINES_SELECTED)
            final_budget = final_selection(types_budget, BUDGET_SELECTED)
            final_location = centralLocation(LOCATION)
            context.bot.send_message(chat_id=update.effective_chat.id, text = "Deciding based on:" + "\n" + final_cuisine + "\n" + final_budget)
            context.bot.send_message(chat_id=update.effective_chat.id, text = final_location)
            new_result = list(filter(lambda x : final_cuisine == x[4], SAMPLE_DATABASE))
            new_result = list(filter(lambda x : final_budget == x[5], new_result))
            new_result = sorted(new_result, key = lambda x : getHaversineDistance(final_location, get_lat_lon(x[3])))
            context.bot.send_message(chat_id=update.effective_chat.id, text = f"{new_result[0][2]}")
            LOCATION.clear()
            CUISINES_SELECTED.clear()
            BUDGET_SELECTED.clear()
            return ConversationHandler.END
        except IndexError:
            context.bot.send_message(chat_id=update.effective_chat.id, text = "Cannot find suitable restaurant. Please try again.")
            LOCATION.clear()
            CUISINES_SELECTED.clear()
            BUDGET_SELECTED.clear()
            return ConversationHandler.END
          ### might need to remove LOCATION, CUISINE AND BUDGET inputs from USERS_DATA ###
        
            
            


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), start),
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                CallbackQueryHandler(five, pattern='^' + str(FIVE) + '$'),
                CallbackQueryHandler(six, pattern='^' + str(SIX) + '$'),
                CallbackQueryHandler(seven, pattern='^' + str(SEVEN) + '$'),
                CallbackQueryHandler(eight, pattern='^' + str(EIGHT) + '$'),
                CallbackQueryHandler(nine, pattern='^' + str(NINE) + '$'),
                CallbackQueryHandler(ten, pattern='^' + str(TEN) + '$'),
                CallbackQueryHandler(eleven, pattern='^' + str(ELEVEN) + '$'),
            ],
            SECOND: [
                CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
                #CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), end)
            ],
            THIRD: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), user_age)
            ],
            FOURTH: [
                MessageHandler(Filters.text & ~ (Filters.command | Filters.regex('^Done$')), user_gender)
            ]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
