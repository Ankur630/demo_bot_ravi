import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import pymongo
import threading
from datetime import date as d
from core import (bot_token, mongo_url, admins, merchant_id, merchant_key, subwallet_key, pay_comment)

bot = telebot.TeleBot(bot_token)
client = pymongo.MongoClient(mongo_url)
db = client['Demo']
data = db['Demo2']
cha = db['channels']
num = db['numbers']
@bot.message_handler(commands=['restart'])
def restart(msg):
    if msg.chat.id in admins:
        client.drop_database('Demo')
        bot.send_message(msg.chat.id, "*Bot Data Has Been Restarted*", parse_mode="Markdown")
# Channels Check
def delete_cha2(username):
    cha.delete_one({"Channel": username})


def add_cha2(username):
    cha.insert_one({"Channel": username})


def check1(user):
    channels = cha.find({}, {"Channel": 1, "_id": 0})
    if channels == None:
        return "Not_added"
    for Data in channels:
        for x in Data.values():
            try:
                result = bot.get_chat_member(x, user).status
                if 'kicked' in result:
                    return 'Left'
                if 'left' in result:
                    return 'Left'
            except:
                for i in admins:
                    bot.send_message(i, f"*Please Make Me Admin Here {x}*", parse_mode="Markdown")


# Pymongo Database Function

def update_user(user, type, newdata):
    user_db = data.find_one({"User": user})
    if user_db == None:
        add_user(user, 'Ban')
    else:
        data.update_one({"User": user}, {"$set": {type: newdata}})


def update_bot(type, newdata):
    data.update_one({"Bot": "Bot"}, {"$set": {type: newdata}})
    return "Done"


def add_user(user, hh):
    if hh == 'Ban':
        user_data = {"User": user, "Balance": 0.0, "Wallet": "None", "Ban": "Ban", "antihack": 0, "refer": 0,
                     "referby": "None", "Verify": "Not", "Bonus": 1}
    else:
        user_data = {"User": user, "Balance": 0.0, "Wallet": "None", "Ban": "Unban", "antihack": 0, "refer": 0,
                     "referby": "None", "Verify": "Not", "Bonus": 1}
    data.insert_one(user_data)


def user_data(user, type):
    user_db = data.find_one({"User": user})
    if user_db == None:
        add_user(user, 'add')
    else:
        database = user_db[type]
        return database


def add_bot(type):
    BotData = {"Bot": "Bot", "P_refer": 1.0, "M_with": 2.0, "curr": "INR", "P_channel": "@IDK", "Totalu": 0,
               "Totalw": 0.0, "Bonus": 0.1,"Bot_status":"✅ ON"}
    data.insert_one(BotData)
    print("Bot New Data Has Been Installed")
    get_bot(type)


def get_bot(type):
    bot_find = data.find_one({"Bot": "Bot"})
    if bot_find == None:
        add_bot(type)
        return
    result = bot_find[type]
    return result


per_refer = get_bot('P_refer')

def broad_2(msg,id):
    all_user = data.find({}, {"User": 1, "_id": 0})
    for Data in all_user:
        for x in Data.values():
            try:
                bot.send_message(x, f"*📢Broadcast By Admin*\n\n{msg}", parse_mode="Markdown",
                                 disable_web_page_preview=True)
            except:
                print("User Blocked Me ", x)
    bot.send_message(id,"*Broadcast Has Sended To All Users*",parse_mode='Markdown')
def broad(message):
    t1 = threading.Thread(target=broad_2,args=(message.text,message.chat.id))
    t1.start()


def add_cha(message):
    msg = message.text
    user = message.chat.id
    bot.send_message(user, "*Channel Has Been Added Make Sure You Make Bot Admin In Channel*", parse_mode="Markdown")
    t1 = threading.Thread(target=add_cha2, args=(msg,))
    t1.start()


def delete_cha(message):
    msg = message.text
    user = message.chat.id
    bot.send_message(user, "*channel Has been Deleted*", parse_mode="Markdown")
    t1 = threading.Thread(target=delete_cha2, args=(msg,))
    t1.start()


def with_2(id, amo):
    pay_c = get_bot('P_channel')
    curr = get_bot('curr')
    m_with = get_bot('M_with')
    bal = user_data(id, 'Balance')
    wallet = user_data(id, "Wallet")
    if amo.isdigit == False:
        bot.send_message(id, "*⛔ Only Numeric Value Allowed*", parse_mode="Markdown")
        return
    if int(amo) < m_with:
        bot.send_message(id, f"*⚠️ Minimum Withdrawal Is {m_with} {curr}*", parse_mode="Markdown")
        return
    if float(amo) > bal:
        bot.send_message(id, "*⛔ Entered Amount Is Greater Than Your Balance*", parse_mode="Markdown")
        return
    oldus = get_bot("Totalw")
    newus = oldus + int(amo)
    t1 = threading.Thread(target=update_bot, args=("Totalw", newus))
    t1.start()

    oldbal = user_data(id, 'Balance')
    newbal = oldbal - float(amo)
    t2 = threading.Thread(target=update_user, args=(id, 'Balance', float(newbal)))
    t2.start()
    bal2 = user_data(id, 'Balance')
    if bal2 < 0:
        return
    url = f"https://job2all.xyz/api/index.php?mid={merchant_id}&mkey={merchant_key}&guid={subwallet_key}&mob={wallet}&amount={amo}&info={pay_comment}"
    r = requests.get(url)
    bot.send_message(id,
                     f"*✅ New Withdrawal Processed ✅\n\n🚀Amount : {amo} {curr}\n\n⛔️ Wallet :* `{wallet}`*\n\n💡 Bot : @{bot.get_me().username}*",
                     parse_mode="Markdown")
    try:
        bot.send_message(pay_c,
                         f"*✅ New Withdrawal Requested ✅\n\n🟢 User : *[{id}](tg://user?id={id})*\n\n🚀Amount : {amo} {curr}\n\n⛔️ Address : *`{wallet}`*\n\n💡 Bot : @{bot.get_me().username}*",
                         parse_mode="Markdown", disable_web_page_preview=True)
    except:
        print("Bot Is Not Admin In Payment Channel ", pay_c)


def with_1(message):
    try:
        amo = message.text
        id = message.chat.id
        curr = get_bot('curr')
        m_with = get_bot('M_with')
        bal = user_data(id, 'Balance')
        wallet = user_data(id, "Wallet")
        antihack = user_data(id, "antihack")

        if antihack == 1:
            bot.send_message(id, "*⛔ Please Conform Your Previus Request Or Cancel*", parse_mode="Markdown")
            return
        if amo.isnumeric() == False:
            bot.send_message(id, "*⛔ Only Numeric Value Allowed*", parse_mode="Markdown")
            return
        if int(amo) != m_with:
            bot.send_message(id, f"*⚠️ Minimum Withdrawal Is {m_with} {curr}*", parse_mode="Markdown")
            return
        if float(amo) > bal:
            bot.send_message(id, "*⛔ Entered Amount Is Greater Than Your Balance*", parse_mode="Markdown")
            return
        t1 = threading.Thread(target=update_user, args=(id, "antihack", 1))
        t1.start()
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('✅Approve', callback_data=f"agree_{amo}"),
                   InlineKeyboardButton("❌Cancel", callback_data="cancel"))
        bot.send_message(id,
                         f"*🤘Withdrawal Confirmation\n\n🔰 Amount : {amo} {curr}\n🗂 Wallet : {wallet}\n\n✌️Confirm Your Transaction By Clicking On '✅ Approve'*",
                         parse_mode="Markdown", reply_markup=markup)
    except:
        print("Error In With1 Command")


def menu(id):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('💰 Balance')
    keyboard.row('🙌🏻 Invite', '🎁 Bonus', '🗂 Wallet')
    keyboard.row('💳 Withdraw', '📊 Statistics')
    bot.send_message(id, "*🏡 Welcome To Main Menu*", parse_mode="Markdown", reply_markup=keyboard)


def set_bonus(message):
    curr = get_bot('curr')
    id = message.chat.id
    if message.text.isdigit == False:
        bot.send_message(id, "*Please Send A Valid ID*", parse_mode="Markdown")
    else:
        id = message.chat.id
        amo = message.text
        if amo < '1':
            haha = f'{amo}'
        else:
            haha = f'{amo}.0'
        t1 = threading.Thread(target=update_bot, args=('Bonus', float(haha)))
        t1.start()
        bot.send_message(id, f"*Bonus Has Been Updated To {haha} {curr}*", parse_mode="Markdown")


def set_prefer(message):
    curr = get_bot('curr')
    id = message.chat.id
    if message.text.isdigit == False:
        bot.send_message(id, "*Please Send A Valid ID*", parse_mode="Markdown")
    else:
        id = message.chat.id
        amo = message.text
        if amo < '1':
            haha = f'{amo}'
        else:
            haha = f'{amo}.0'
        t1 = threading.Thread(target=update_bot, args=('P_refer', float(haha)))
        t1.start()
        bot.send_message(id, f"*Per Refer Has Been Set To {amo} {curr}*", parse_mode="Markdown")


def m_withdraw(message):
    curr = get_bot('curr')
    id = message.chat.id
    amo = int(message.text)
    t1 = threading.Thread(target=update_bot, args=("M_with", amo))
    t1.start()
    bot.send_message(id, f"*Minimum Withdraw Has Been Set To {amo} {curr}*", parse_mode="Markdown")


def set_curr(message):
    id = message.chat.id
    cur = message.text
    t1 = threading.Thread(target=update_bot, args=('curr', cur))
    t1.start()
    bot.send_message(id, f"*Currency Has Been Set To {cur}*", parse_mode="Markdown")


def Pay_channel(message):
    id = message.chat.id
    cha = message.text
    t1 = threading.Thread(target=update_bot, args=('P_channel', cha))
    t1.start()
    bot.send_message(id, f"*Your Payment Channel Has Been Set To {cha}*", parse_mode="Markdown")


def banu(message):
    id = message.chat.id
    banid = message.text
    if banid.isdigit == True:
        bot.send_message(id, "*Please Send A Valid ID*", parse_mode="Markdown")
    else:
        t1 = threading.Thread(target=update_user, args=(int(banid), "Ban", "Ban"))
        t1.start()
        bot.send_message(id, "*User Has Been Banned*", parse_mode="Markdown")


def unbanu(message):
    id = message.chat.id
    banid = message.text
    if banid.isdigit == True:
        bot.send_message(id, "*Please Send A Valid ID*", parse_mode="Markdown")
    else:
        t1 = threading.Thread(target=update_user, args=(int(banid), "Ban", "Unban"))
        t1.start()
        bot.send_message(id, "*User Has Been Unbanned*", parse_mode="Markdown")


def setnum(message):
    land = num.find_one({"Number": message.text})
    if message.text.isdigit == False:
        bot.send_message(message.chat.id, "*⛔Please Send A Valid Mobile Number*", parse_mode="Markdown")
    elif len(message.text) != 10:
        bot.send_message(message.chat.id, "*⛔Please Send A Valid Mobile Number*", parse_mode="Markdown")
    elif land != None:
        bot.send_message(message.chat.id, "*⛔This Number is Already Added In Bot*", parse_mode="Markdown")
    else:
        t1 = threading.Thread(target=update_user, args=(message.chat.id, "Wallet", message.text))
        t1.start()
        num.insert_one({"Number": message.text, "User": message.chat.id})
        bot.send_message(message.chat.id, f"*🗂️Your Number Has Been Updated To {message.text}*", parse_mode="Markdown")


@bot.message_handler(commands=['add'])
def add(message):
    id = message.chat.id
    if id in admins:
        oldbal = user_data(id, 'Balance')
        newbal = oldbal + 1000
        t1 = threading.Thread(target=update_user, args=(id, 'Balance', float(newbal)))
        t1.start()


@bot.message_handler(commands=['panel'])
def panel(message):
    if message.chat.id in admins:
        bot_status = get_bot('Bot_status')
        if bot_status == "✅ ON":
            bot_button = "❌ OFF"
        else:
            bot_button = "✅ ON"
        bonus = get_bot('Bonus')
        pay_c = get_bot('P_channel')
        curr = get_bot('curr')
        m_with = get_bot('M_with')
        per_refer = get_bot('P_refer')
        channels = cha.find({}, {"Channel": 1, "_id": 0})
        if channels == None:
            return
        text = "*Channels : \n"
        for Data in channels:
            for x in Data.values():
                text += f"{x}\n"
        text += f"\nPer Refer : {per_refer} {curr}\n\nMinimun Withdraw : {m_with} {curr}\n\nBonus : {bonus} {curr}\n\nPayment Channel : {pay_c}"
        text += "*"
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton('Per Refer', callback_data="Per_r"),
                   InlineKeyboardButton('Minimum Withdraw', callback_data="Minimum_w"),
                   InlineKeyboardButton("Add Channel", callback_data="Add_cha"),
                   InlineKeyboardButton("Delete Channel", callback_data="Delete_cha"),
                   InlineKeyboardButton("Pay Channel", callback_data="Pay_cha"),
                   InlineKeyboardButton("Ban", callback_data="Ban"),
                   InlineKeyboardButton("Unban", callback_data="Unban"),
                   InlineKeyboardButton("Broadcast", callback_data="Broad"),
                   InlineKeyboardButton("Set Currency", callback_data="Set_curr"),
                   InlineKeyboardButton("Set Bonus", callback_data="bonus"),
                   InlineKeyboardButton(f"{bot_button} Bot",callback_data=f"bot_{bot_button}"))
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callbck_query(call):
    user = call.message.chat.id
    if call.data == 'Per_r':
        msg = bot.send_message(user, "*Send Amount You Want To Set*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, set_prefer)
    elif call.data == 'bonus':
        msg = bot.send_message(user, "*Send Amount You Want To Set*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, set_bonus)
    elif call.data == 'Minimum_w':
        msg = bot.send_message(user, "*Send Amount You Want To Set*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, m_withdraw)
    elif call.data == 'Add_cha':
        msg = bot.send_message(user, "*Send Channel Username You Want To Add*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, add_cha)
    elif call.data == 'Delete_cha':
        msg = bot.send_message(user, "*Send Channel Username You Want To Delete*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, delete_cha)
    elif call.data == 'Pay_cha':
        msg = bot.send_message(user, "*Send Channel Username You Want To Set*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, Pay_channel)
    elif call.data == 'Ban':
        msg = bot.send_message(user, "*Send His telegram Id*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, banu)
    elif call.data == 'Unban':
        msg = bot.send_message(user, "*Send His Telegram Id*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, unbanu)
    elif call.data == 'Set_curr':
        msg = bot.send_message(user, "*Send Currency Name You Want To Set*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, set_curr)
    elif call.data == 'Broad':
        msg = bot.send_message(user, "*Send Message You Want To Broadcast*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, broad)
    elif call.data == 'set_wallet':
        if get_bot('Bot_status') == "❌ OFF":
            bot.send_message(user, "*❌ Bot Is OFF*", parse_mode="Markdown")
            return
        msg = bot.send_message(user, "*🗂️Send Your Paytm Number\n\n⚠️Notice: You Cant Change Your Wallet Again*",
                               parse_mode="Markdown")
        bot.register_next_step_handler(msg, setnum)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            print("Error While Deleting Set Wallet Inline Button")
    elif call.data.startswith('bot_'):
        status = call.data.split('_')[1]
        t1 = threading.Thread(target=update_bot,args=("Bot_status",status))
        t1.start()
        bot_status = get_bot('Bot_status')
        if bot_status == "✅ ON":
            bot_button = "❌ OFF"
        else:
            bot_button = "✅ ON"
        bonus = get_bot('Bonus')
        pay_c = get_bot('P_channel')
        curr = get_bot('curr')
        m_with = get_bot('M_with')
        per_refer = get_bot('P_refer')
        channels = cha.find({}, {"Channel": 1, "_id": 0})
        if channels == None:
            return
        text = "*Channels : \n"
        for Data in channels:
            for x in Data.values():
                text += f"{x}\n"
        text += f"\nPer Refer : {per_refer} {curr}\n\nMinimun Withdraw : {m_with} {curr}\n\nBonus : {bonus} {curr}\n\nPayment Channel : {pay_c}"
        text += "*"
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton('Per Refer', callback_data="Per_r"),
                   InlineKeyboardButton('Minimum Withdraw', callback_data="Minimum_w"),
                   InlineKeyboardButton("Add Channel", callback_data="Add_cha"),
                   InlineKeyboardButton("Delete Channel", callback_data="Delete_cha"),
                   InlineKeyboardButton("Pay Channel", callback_data="Pay_cha"),
                   InlineKeyboardButton("Ban", callback_data="Ban"),
                   InlineKeyboardButton("Unban", callback_data="Unban"),
                   InlineKeyboardButton("Broadcast", callback_data="Broad"),
                   InlineKeyboardButton("Set Currency", callback_data="Set_curr"),
                   InlineKeyboardButton("Set Bonus", callback_data="bonus"),
                   InlineKeyboardButton(f"{bot_button} Bot", callback_data=f"bot_{bot_button}"))
        bot.edit_message_text(text,call.message.chat.id, call.message.message_id,reply_markup=markup,parse_mode="Markdown")
    elif call.data.startswith("agree_"):
        amo = call.data.split("_")[1]
        t1 = threading.Thread(target=update_user, args=(user, "antihack", 0))
        t1.start()
        t2 = threading.Thread(target=with_2, args=(user, amo))
        t2.start()
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            print("Error While Deleting Withdraw Approve Button")
    elif call.data == "cancel":
        t1 = threading.Thread(target=update_user, args=(user, "antihack", 0))
        t1.start()
        bot.send_message(call.message.chat.id, "*❌Your Withdrawl Canceled*", parse_mode="Markdown")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            print("Error While Deleting Withdraw Cancel Button")


def refer(user):
    curr = get_bot('curr')
    refer = user_data(user, 'refer')
    if refer == 0:
        update_user(user, 'refer', 1)
        oldus = get_bot('Totalu')
        newus = oldus + 1
        t1 = threading.Thread(target=update_bot, args=('Totalu', newus))
        t1.start()
        hh = user_data(user, "referby")
        if int(hh) == user:
            return
        elif int(hh) == 1:
            return
        else:
            bot.send_message(user, f"*💹 You Were Invited By *[{hh}](tg://user?id={hh})", parse_mode="Markdown")
            p_refer = get_bot('P_refer')
            oldB = user_data(int(hh), "Balance")
            newB = float(oldB) + float(p_refer)
            t1 = threading.Thread(target=update_user, args=(int(hh), "Balance", float(newB)))
            t1.start()
            bot.send_message(int(hh),
                             f"*💰 {float(p_refer)} {curr} Added To Your Balance*",
                             parse_mode="Markdown")


def send_start(user):
    channels = cha.find({}, {"Channel": 1, "_id": 0})
    if channels == None:
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('🟢Joined')
    msg_start = "*⛔Must Join All Our Channel\n"
    for Data in channels:
        for x in Data.values():
            msg_start += f"\n {x}\n"
    msg_start += "\n✅After Joining, Click On '🟢Joined'"
    msg_start += "*"
    bot.send_message(user, msg_start, parse_mode="Markdown", reply_markup=keyboard)


def subs(user):
    check = check1(user)
    if check == 'Left':
        t1 = threading.Thread(target=send_start, args=[user])
        t1.start()
    else:
        t1 = threading.Thread(target=menu, args=[user])
        t1.start()
        t2 = threading.Thread(target=refer, args=[user])
        t2.start()


@bot.message_handler(content_types=['contact'])
def contact(message):
    phone = message.contact.phone_number
    user = message.chat.id
    user2 = message.contact.user_id
    if user != user2:
        bot.send_message(user, '*⛔Its Not Your Number*', parse_mode="Markdown")
        return
    if phone.startswith("+91") or phone.startswith("91"):
        t1 = threading.Thread(target=update_user, args=(int(user), "Verify", "Done"))
        t1.start()
        t2 = threading.Thread(target=subs, args=[user])
        t2.start()
    else:
        t1 = threading.Thread(target=update_user, args=(int(user), "Ban", "Ban"))
        t1.start()
        bot.send_message(message.chat.id, "*⛔Only Indian Accounts Are Allowed*", parse_mode="Markdown")


@bot.message_handler(commands=['start'])
def start(message):
    user = message.chat.id
    if get_bot('Bot_status') == "❌ OFF":
        bot.send_message(user,"*❌ Bot Is OFF*",parse_mode="Markdown")
        return
    msg = message.text
    username = message.from_user.username
    if username == None:
        t1 = threading.Thread(target=update_user, args=(int(user), "Ban", "Ban"))
        t1.start()
        return
    ban = user_data(user, 'Ban')
    if ban == "Ban":
        bot.send_message(message.chat.id, "*💢 You Are Banned From Using This Bot*", parse_mode="Markdown")
        return
    t1 = threading.Thread(target=user_data, args=(user, "User"))
    t1.start()
    try:
        refid = message.text.split()[1]
    except:
        refid = 1
    refer = user_data(user, 'refer')
    if refer == 0:
        if refid != 1:
            bot.send_message(refid,
                             f"*🚧 New User On Your Invite Link :\n* [{message.chat.id}](tg://user?id={message.chat.id})",
                             parse_mode="Markdown")
        t1 = threading.Thread(target=update_user, args=(user, "referby", refid))
        t1.start()
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="💢 Share Contact", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id,
                     "*© Share Your Contact In Order\nTo Use This Bot ,It's Just A Number Verification\n\n⚠️Note :* `We Will Never Share Your Details With Anyone`",
                     parse_mode="Markdown", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def send_text(message):
    user = message.chat.id
    if get_bot('Bot_status') == "❌ OFF":
        bot.send_message(user,"*❌ Bot Is OFF*",parse_mode="Markdown")
        return
    curr = get_bot('curr')
    m_with = get_bot('M_with')
    per_refer = get_bot('P_refer')
    user = message.chat.id
    if user in admins:
        admin = user
    else:
        admin = 1
    msg = message.text
    wallet = user_data(user, "Wallet")
    ban = user_data(user, 'Ban')
    verify = user_data(user, 'Verify')
    if verify == "Not":
        bot.send_message(user, "*❌ Please Verify Your Account First /start*", parse_mode="Markdown")
        return
    elif ban == "Ban":
        bot.send_message(message.chat.id, "*💢 You Are Banned From Using This Bot*", parse_mode="Markdown")
        return
    elif message.text == "🎁 Bonus":
        bonus = get_bot("Bonus")
        date_user = user_data(user, "Bonus")
        date = str(d.today())
        if date_user == date:
            text = '*⛔️ You Already Recieved Bonus In Last 24 Hours*'
        else:
            text = f'*🎁 Congrats , You Recieved {bonus} {curr}\n\n🔎 Check Back After 24 Hours*'
            oldbal = user_data(user, 'Balance')
            newbal = oldbal + bonus
            t1 = threading.Thread(target=update_user, args=(user, 'Balance', float(newbal)))
            t1.start()
            t2 = threading.Thread(target=update_user, args=(user, 'Bonus', date))
            t2.start()
        bot.send_message(user, text, parse_mode="Markdown")
    elif msg == "🟢Joined":
        t1 = threading.Thread(target=subs, args=[user])

        t1.start()
    elif message.text == "💰 Balance":
        balance = user_data(user, 'Balance')
        wallet = user_data(user, 'Wallet')
        msg = f'*🙌🏻 User = {message.from_user.first_name}\n\n💰 Balance = {balance} {curr}\n\n🪢 Invite To Earn More*'
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    elif message.text == "🙌🏻 Invite":
        user = message.chat.id
        bot_name = bot.get_me().username
        msg = f"*🙌🏻 User = {message.from_user.first_name}\n\n🙌🏻 Your Invite Link = https://t.me/{bot_name}?start={user}\n\n🪢Invite To Earn {per_refer} {curr}*"
        bot.send_message(user, msg, parse_mode="Markdown", disable_web_page_preview=True)
    elif message.text == "🗂 Wallet":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f'🚧 Set {curr} Wallet 🚧', callback_data="set_wallet"))
        text = f"*💡 Your Currently Set INR Wallet Is: *`'{wallet}'`*\n\n🗂 It Will Be Used For Future Withdrawals*"
        bot.send_message(user, text, parse_mode="Markdown", reply_markup=markup)
    elif message.text == "📊 Statistics":
        id = message.chat.id
        witth = get_bot('Totalw')
        total = get_bot('Totalu')
        msg = f"*📊 Bot Live Stats 📊\n\n📤 Total Payouts : {witth} {curr}\n\n💡 Total Users : {total} Users\n\n🔎 Coded By: *[ⲘᏒ᭄кᴀʀᴀɴ✓](https://t.me/KaranYTop)"
        bot.send_message(id, msg, parse_mode="Markdown", disable_web_page_preview=True)
    elif message.text == "💳 Withdraw":
        id = message.chat.id
        bal = user_data(id, 'Balance')
        wallet = user_data(id, "Wallet")
        if bal < m_with:
            bot.send_message(id, f"*⚠️ Must Own AtLeast {m_with} {curr} To Make Withdrawal*", parse_mode="Markdown")
        elif wallet == "None":
            bot.send_message(id, "*⚠️ Set Your Wallet Using : *`🗂 Wallet`", parse_mode="Markdown")
        else:
            msg = bot.send_message(user, "*📤 Enter Amount To Withdraw*", parse_mode="Markdown")
            bot.register_next_step_handler(msg, with_1)


print("Done")
if __name__ == "__main__":
    bot.polling(none_stop=True)
