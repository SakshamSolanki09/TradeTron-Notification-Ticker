import requests
import json
from http.cookies import SimpleCookie 
import time
import datetime
import html

print('EOD Order Book Live')
print("Notification Ticker")

chatid = ['cid'] #chat ids to send messages to
telegramcommandid = ['cid'] #ids to accept commands from
bottoken = 'bottoken here' #add telegram bot token here
telegramupdateurl = "https://api.telegram.org/bot"+ bottoken + "/GetUpdates?offset="
updateid = ''
addchatsfromid = []
changecookieids = []
removechatids = []
allchatslog={}




def resetMessageList():
    global chatid
    f = open("mlist.txt",'r')
    l = f.readline().rstrip(',')
    if l != '':
        chatid = l.replace('\n','').split(',')
    f.close()

def resetCookies():
    global tt_cookies
    if tt_cookies == None:
        f = open("cookie.txt",'r')
        cookie = f.readline()
        tt_cookies = doCookies(cookie)
        f.close()

def doCookies(cookieS):
    if cookieS == '':
        return
    cookie = SimpleCookie()
    cookie.load(cookieS)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies

tt_params = {'execution':'LIVE AUTO'}
tt_headers = {'x-requested-with': 'XMLHttpRequest','Accept': 'application/json'}
inp = input("Enter TT Cookie")
tt_cookies = inp
tt_cookies = doCookies(tt_cookies)
usage = 0

#-------------------------------------------Important-------------------------------------------
NOTIFICATION_URL = "https://tradetron.tech/api/dashboard/recent/notification?strategies=5014494,5014498,5014512,5014513,5015133,5107235,"
#Inspect >> Network >> Notification Request >> Request URL <- copy here

last_notification_id = 0

def messageTelegram(msg, chatids):
    for i in range(len(chatids)):
        requests.post("https://api.telegram.org/bot"+ bottoken + "/sendMessage?chat_id="+chatids[i]+"&text="+(msg).replace("&",'').replace("reg;",'')+'&parse_mode=html&disable_web_page_preview=true')



def get_message():
    try:
        msg = ''
        global NOTIFICATION_URL,tt_cookies,tt_headers,tt_params,last_notification_id
        response = requests.get(NOTIFICATION_URL,headers=tt_headers,cookies=tt_cookies)
        notifications = json.loads(response.text)['data']
        _id = []
        _recent_message = []
        _strat = []
        for i in range(len(notifications)):
            date = datetime.datetime.strptime(notifications[i]['created_at'],"%Y-%m-%d %H:%M:%S")
            id = notifications[i]['id']
            if(id == last_notification_id):
                break
            recent_message = notifications[i]["message"]
            strat = notifications[i]['strategy']['template']['name']
            if("Entry satisfied" not in recent_message and "Exit satisfied" not in recent_message):
                continue
            
            msg += f"{recent_message}\n{str(date)}\n<b>({strat})</b>\n\n"
        last_notification_id = notifications[0]['id']
        return msg
    except:
        print("Except")
        return ""


def get_todays_message():
    try:
        msg= '<b> Notifications Today:</b>\n\n'
        global NOTIFICATION_URL,tt_cookies,tt_headers,tt_params,last_notification_id
        response = requests.get(NOTIFICATION_URL,headers=tt_headers,cookies=tt_cookies)
        notifications = json.loads(response.text)['data']
        _id = []
        _recent_message = []
        _strat = []
        for i in range(len(notifications)-1,0,-1):
            date = datetime.datetime.strptime(notifications[i]['created_at'],"%Y-%m-%d %H:%M:%S")
            id = notifications[i]['id']
            recent_message = notifications[i]["message"]
            strat = notifications[i]['strategy']['template']['name']
            if("Entry satisfied" not in recent_message and "Exit satisfied" not in recent_message):
                continue
            msg += f"{recent_message}\n {str(date)} \n<b>({strat})</b>\n\n"
        last_notification_id = notifications[0]['id']
        return msg
    except:
        return ""

def telegram():

    global updateid, removechatids, addchatsfromid, changecookieids, tt_cookies, chatid, telegramcommandid
    
    #check messages
    try:
        turl = 'a'
        try:
            turl = telegramupdateurl+str(int(updateid)+1 if updateid != "" else 0)
        except:
            turl = telegramupdateurl
        getupdate = json.loads(requests.get(turl).text)
        totalupdates = len(getupdate['result'])
        result = getupdate['result']
        lastupdate = getupdate['result'][totalupdates-1]
        updateidfetched = lastupdate['update_id']
        if 'chat' not in lastupdate['message'] : return
        updatemessage = lastupdate['message']['text']
        try:
            chat = lastupdate['message']['chat']            
        except:
            return
        if str(chat['id']) not in str(allchatslog):
            allchatslog[str(chat['id'])] = chat
    except Exception as e:
        updatemessage = ""
        return

    try:
        if(str(chat['id']) not in telegramcommandid):
            return
        
        if(addchatsfromid != [] and str(chat['id']) in addchatsfromid and updateid != updateidfetched):
            updateid = updateidfetched
            addchatsfromid = [i for i in addchatsfromid if i != str(chat['id'])]
            try:
                f = open('mlist.txt','w')
                ids = [i for i in updatemessage.split(",") if i not in chatid]
                chatid.extend(ids)
                strg = ''
                for i in chatid:
                    strg += i +','
                f.write(strg)
                f.close()
                messageTelegram('Added Successfully',telegramcommandid)
            except:
                messageTelegram('Something went wrong',telegramcommandid)
            return

        elif(removechatids != [] and str(chat['id']) in removechatids and updateid != updateidfetched):
            try:
                updateid =updateidfetched
                removechatids = [i for i in removechatids if i != str(chat['id'])]
                rids = updatemessage.split(',')
                strg = ''
                newlist = [i for i in chatid if i not in rids]       
                f = open('mlist.txt','w')
                for i in newlist:
                    strg+=i+','
                f.write(strg)
                chatid = newlist
                f.close()
                messageTelegram('Removed Successfully!',telegramcommandid)
            except Exception as e:
                print(e)
                messageTelegram('Update unsuccessful!',telegramcommandid)

        elif(changecookieids != [] and str(chat['id']) in changecookieids and updateid != updateidfetched):
            updateid = updateidfetched
            changecookieids = [i for i in changecookieids if i != str(chat['id'])]
            f = open('cookie.txt','w')
            f.write(updatemessage)
            f.close
            tt_cookies = doCookies(str(updatemessage))
            messageTelegram("Updated Successfully",telegramcommandid)

        elif((updatemessage == '/messagelist') and updateid != updateidfetched):
                updateid = updateidfetched
                messageTelegram(str(chatid),telegramcommandid)

        elif((updatemessage == '/updates') and updateid != updateidfetched):
                updateid = updateidfetched
                msg1 = ''
                
                for j in result: 
                    try:                        
                        msg1 += 'id: ' + str(j['message']['chat']['id']) +'\n'
                        msg1 += 'First name: ' + j['message']['chat']['first_name'] +'\n'
                        msg1 += 'Last name: ' + j['message']['chat']['last_name'] +'\n'
                        msg1 += 'Type: ' + j['message']['chat']['type'] +'\n\n'
                    except:print("problem in /updates")
                messageTelegram(str(result),chatid)
                print('All chats sent')
        
        elif((updatemessage == "/addmessagechat") and updateid != updateidfetched):
                updateid = updateidfetched
                msg = "Enter chatid seperated with ',' use /allchats to see all available chats:"
                messageTelegram(msg,telegramcommandid)
                addchatsfromid = str(chat['id'])
        
        elif((updatemessage == "/removemessagechat") and updateid != updateidfetched):
            updateid = updateidfetched
            removechatids.append(str(chat['id']))
            messageTelegram('Enter ID to remove from list',telegramcommandid)
        
        elif((updatemessage == "/changecookie") and updateid != updateidfetched):
            updateid = updateidfetched
            changecookieids.append(str(chat['id']))
            msg = 'Enter the new cookie'
            messageTelegram(msg,telegramcommandid)
        
        elif((updatemessage == "/notifications") and updateid != updateidfetched):
            updateid = updateidfetched
            print("here")
            msg = get_todays_message()
            messageTelegram(msg[0:4000],chatid)

        elif((updatemessage == "/help") and updateid != updateidfetched):
            updateid = updateidfetched
            msg = "/changecookie: Update TT_cookie\n/messagelist: list of ids posting pnl on\n/addmessagechat: Add chat to post message on\n/notifications:Get todays notifications\n/removemessagechat: Remove chatid from messagelist.\n/help: list of commands"
            messageTelegram(msg,telegramcommandid)
        
        elif( updateid != updateidfetched):
            updateid = updateidfetched
            messageTelegram("Unknown command use /help for info",telegramcommandid)

    except Exception as e:
        messageTelegram("Someting Went Wrong! erro:"+ str(e),telegramcommandid)



resetCookies()
resetMessageList()
while True:
    msg=get_message()
    messageTelegram(msg[:4000],chatid)
    telegram()
    time.sleep(2)#change delay here (2)
