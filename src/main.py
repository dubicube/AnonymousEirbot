import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import re
import logging

import threading
import os
import sys
import datetime
import threading
import time

from queue import Queue

DATACHAT_PATH = '../data/'

data_lock = threading.Lock()

def storeMessage(update, context):

    if update.message==None:
        print("Store message no message")
        return
    else:
        print("Store")
    global not_empty_chats
    global queue
    global threadingEvent
    dataChatName = getDataChatName(update)

    if not update.message.chat.id in not_empty_chats:
        error = False
        try:
            with data_lock:
                f = open(DATACHAT_PATH+dataChatName, 'r')
                data = f.read().split('\n')
                f.close()
                if len(data) == 1:
                    error = True
        except:
            error = True
        if error:
            initDataChat(update, context)
    with data_lock:
        f = open(DATACHAT_PATH+dataChatName, 'a')
        f.write(str(update.message.message_id)+' '+str(update.message.date)+'\n')
        f.close()
    if not update.message.chat.id in not_empty_chats:
        queue.put(1)
        threadingEvent.set()
        threadingEvent.clear()

def deleteMessages(dataChatName):
    alarm = None
    with data_lock:
        chat_id = getDataChatId(dataChatName)
        f = open(DATACHAT_PATH+dataChatName, 'r')
        data = f.read().split('\n')
        f.close()

        f = open(DATACHAT_PATH+dataChatName, 'w')
        f.write(data[0]+'\n')

        l = data[0].split(' ')
        del_time = datetime.timedelta(0, int(l[1]))
        now = datetime.datetime.now()
        i = 1
        while i < len(data):
            l = data[i]
            j = l.find('+')
            if j!=-1:
                l = l[:j]
            ls = l.split(' ')
            if len(ls) != 3:
                break
            msg_id = int(ls[0])
            date = ls[1].split('-')
            hour = ls[2].split(':')
            a = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(hour[0]),int(hour[1]),int(hour[2]))
            b = a + del_time
            if now > b and i!=len(data)-2:
                try:
                    print("Delete", chat_id, msg_id, date, hour)
                    updater.bot.deleteMessage(chat_id, msg_id)
                except:
                    print("Delete error")
            else:
                if alarm == None and i!=len(data)-2:
                    alarm = b
                f.write(l+'\n')
            i+=1
        f.close()
    return alarm

def di(update, context):
    storeMessage(update, context)

def shutdown():
    updater.stop()
    updater.is_idle = False
def stop(bot, update):
    print("Stopping...")
    threading.Thread(target=shutdown).start()

def getDataChatName(update):
    return 'chat'+str(update.message.chat.id)
def getDataChatNameID(id):
    return 'chat'+str(id)
def getDataChatId(dataChatName):
    return int(dataChatName[4:])

def initDataChat(update, context):
    msg = context.bot.send_message(update.message.chat_id, "Cancer incoming !\nPlease, allow all admin rights to this bot to achieve maximum cancer level.\nThis message will self destruct in 60s.")
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
    dataChatName = getDataChatNameID(chat_id)
    with data_lock:
        f = open(DATACHAT_PATH+dataChatName, 'w')
        f.write(str(user_id)+' 60\n')
        f.write(str(msg.message_id)+' '+str(msg.date)+'\n')
        f.close()

def telegram_new_member(update, context):
    admin_error = False
    delete_error = False
    for chat_member in update.message.new_chat_members:
        if chat_member.id == context.bot.id:
            initDataChat(update, context)
        else:
            try:
                context.bot.promote_chat_member(chat_id=update.message.chat.id, user_id=chat_member.id, can_change_info=True, can_post_messages=None, can_edit_messages=False, can_delete_messages=True, can_invite_users=True, can_restrict_members=False, can_pin_messages=True, can_promote_members=True, is_anonymous=True)
            except:
                print("Admin error")
                admin_error = True
            try:
                context.bot.deleteMessage(update.message.chat_id, update.message.message_id)
            except:
                print("Delete error")
                delete_error = True
    # if admin_error:
    #     context.bot.send_message(update.message.chat_id, "Bot has not enough admin rights to automatically configure new users")
    # if delete_error:
    #     context.bot.send_message(update.message.chat_id, "Bot cannot delete messages")

def admin(update, context):
    if update.message != None:
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        if update.message.reply_to_message != None:
            user_id = update.message.reply_to_message.from_user.id
        try:
            context.bot.promote_chat_member(chat_id=chat_id, user_id=user_id, can_change_info=True, can_post_messages=None, can_edit_messages=False, can_delete_messages=True, can_invite_users=True, can_restrict_members=False, can_pin_messages=True, can_promote_members=True, is_anonymous=True)
        except:
            print("Admin error")
            admin_error = True
        try:
            context.bot.deleteMessage(update.message.chat_id, update.message.message_id)
        except:
            print("Delete error")
            delete_error = True

def settime(update, context):
    global queue
    global threadingEvent
    storeMessage(update, context)
    params = update.message.text.split(' ')
    try:
        print(params[1])
        v = int(params[1])
        dataChatName = getDataChatName(update)
        with data_lock:
            f = open(DATACHAT_PATH+dataChatName, 'r')
            data = f.read().split('\n')
            f.close()
            l = data[0].split(' ')
            data[0] = l[0]+' '+params[1]
            f = open(DATACHAT_PATH+dataChatName, 'w')
            f.write('\n'.join(data))
            f.close()
        queue.put(1)
        threadingEvent.set()
        threadingEvent.clear()
        print("Time")
    except:
        print("Time error")

def getFiles(path):
    files = []
    for entry in os.scandir(path):
        if entry.is_file():
            files+=[entry.name]
    return files

def getBestAlarm(alarm_list):
    best_alarm = None
    a = None
    for (id, r) in alarm_list:
        if r!=None and (best_alarm==None or a>r):
            best_alarm = (id, r)
            a = r
    return best_alarm
def getBestAlarmI(alarm_list):
    best_i = -1
    a = None
    i = 0
    while i < len(alarm_list):
        (id, r) = alarm_list[i]
        if r!=None and (a==None or a>r):
            best_i = i
            a = r
        i+=1
    return best_i

queue = Queue()
not_empty_chats = []
def updateAlarms():
    global not_empty_chats
    alarm_list = []
    time.sleep(5)
    fl = ['chat'+TOKENS[2]] if TEST else getFiles(DATACHAT_PATH)
    i = 0
    while i < len(fl):
        id = getDataChatId(fl[i])
        r = deleteMessages(getDataChatNameID(id))
        if r != None:
            not_empty_chats+=[id]
        alarm_list += [(id, r)]
        i+=1
    best_alarm = getBestAlarmI(alarm_list)
    return (alarm_list, best_alarm)

def periodic_thread(e, a):
    (alarm_list, best_alarm) = updateAlarms()
    print(alarm_list, best_alarm)

    (best_id, best_t) = (0, None)
    if best_alarm != -1:
        (best_id, best_t) = alarm_list[best_alarm]
    while True:
        now = datetime.datetime.now()
        if best_t!= None and now>best_t:
            r = deleteMessages(getDataChatNameID(best_id))
            if r == None:
                not_empty_chats.remove(best_id)
            alarm_list[best_alarm] = (best_id, r)
            best_alarm = getBestAlarmI(alarm_list)
            (best_id, best_t) = alarm_list[best_alarm]
        else:
            delta_s = 2520
            if best_t != None:
                delta_s = (best_t-now).total_seconds()
            print("Sleeping", delta_s)
            if e.wait(timeout=delta_s):
                stop = False
                update = False
                while not queue.empty():
                    data = queue.get()
                    if data == -1:
                        stop = True
                    if data == 1:
                        update = True
                if update:
                    print("Update")
                    (alarm_list, best_alarm) = updateAlarms()
                    (best_id, best_t) = (0, None)
                    if best_alarm != -1:
                        (best_id, best_t) = alarm_list[best_alarm]
                if stop:
                    print("Peridic thread stopped")
                    break
def start_periodic_thread():
    global threadingEvent
    threadingEvent = threading.Event()
    threading.Thread(target=periodic_thread, args=(threadingEvent, 0)).start()
def stop_periodic_thread_fun():
    try:
        global threadingEvent
        threadingEvent.set()
        return True
    except:
        return False





TOKENS = open("../tokens", "r").read().split('\n')[:-1]
TEST = len(sys.argv)>1 and sys.argv[1]=='-t'
BOT_TOKEN = TOKENS[1] if TEST else TOKENS[0]
updater = Updater(BOT_TOKEN, use_context=True)

def main():
    dp = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dp.add_handler(CommandHandler('time', settime))
    dp.add_handler(CommandHandler('admin', admin))
    dp.add_handler(MessageHandler(Filters.all, di))
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, telegram_new_member))

    start_periodic_thread()

    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()
