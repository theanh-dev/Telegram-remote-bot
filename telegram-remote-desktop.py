from telegram.ext import *
from telegram import KeyboardButton, ReplyKeyboardMarkup
from mss import mss
import tempfile
import os
import psutil
import ctypes
import webbrowser
import pyperclip
import subprocess
import os
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from PIL import Image

class TelegramBot:

    def __init__(self):
        f = open('auth.json')
        auth = json.load(f)
        self.TOKEN = auth["TOKEN"]
        self.CHAT_ID = auth["CHAT_ID"]
        self.USERNAME = auth["USERNAME"]

        # Load all paths
        with open('check-in-list.json', encoding='utf-8') as f:
            checkin_list = json.load(f)
            self.CHECK_IN_DICTIONARY = {
                entry["name"]: entry["path"] for entry in checkin_list
            }


    def start_command(self, update, context):
        buttons = [[KeyboardButton("⚠ Screen status")], 
        [KeyboardButton("🔒 Lock screen")], 
        [KeyboardButton("🔁 Reboot")], 
        [KeyboardButton("📍 Check in")], 
        # [KeyboardButton("🔓 Unlock screen")], 
        [KeyboardButton("📸 Take screenshot")],
        [KeyboardButton("✂ Paste clipboard")], 
        [KeyboardButton("📄 List process")], 
        [KeyboardButton("💤 Sleep")],
        [KeyboardButton("💡 More commands")]]

        context.bot.send_message(
            chat_id=self.CHAT_ID, text="I will do what you command.", reply_markup=ReplyKeyboardMarkup(buttons))

    def error(self, update, context):
        print(f"Update {update} caused error {context.error}")

    def take_screenshot(self):
        try:
            TEMPDIR = tempfile.gettempdir()
            file_path = os.path.join(TEMPDIR, 'monitor-all.jpg')

            with mss() as sct:
                screenshot = sct.grab(sct.monitors[0])  # Capture all monitors
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                img.save(file_path, format='JPEG', quality=70) 

            return file_path
        except Exception as e:
            print(f"[!] Screenshot error: {e}")
            return None

    def reboot(self):
        os.system("shutdown /r /f /t 0") 

    # Run multiple file already defined in self.CHECK_IN_DICTIONARY
    def check_in(self, name):
        if name not in self.CHECK_IN_DICTIONARY:
            return f"❌ No check-in script found for '{name}'"
           
        file = self.CHECK_IN_DICTIONARY[name]
        if os.path.exists(file):
            try:
                subprocess.run(file, shell=True, check=True)
                return f"Initialized check-in process for '{name}'."
            except subprocess.CalledProcessError as e:
                return f"❌ Check-in failed for '{name}': {e}"
        else:
            return f"❌ Check-in file not found for '{name}'."

    # unable to make this work due to windows security blocked programs from being able to unlock windows
    # def unlock_screen(self):
    # # Since the password is already stored in self.PC_PASSWORD, we can use it directly.
    #     password = str(self.PC_PASSWORD)
    #     try:
    #         pyautogui.press('enter') 
    #         time.sleep(2)
    #         print("First enter")

    #         for char in password:
    #             pyautogui.press(char)
    #             time.sleep(0.05)  


    #         # pyautogui.typewrite(str(password))
    #         print("After password")

    #         pyautogui.press('enter')
    #         print("Second enter")
  
    #         time.sleep(2)
    #         # Check if the screen is still locked
    #         for proc in psutil.process_iter():
    #             if (proc.name() == "LogonUI.exe"):  # If the process is still running, it means the screen is locked
    #                 return "Error: Screen is still locked, could not unlock."
        
    #         # If LogonUI.exe process is not found, it means the screen is unlocked
    #         return "Screen unlocked successfully"
    #     except Exception as e:
    #         return f"Error while unlocking screen: {str(e)}"

    def schedule(self, hour, minute):
        def schedule_loop():
            while True:
                now = datetime.now()
                scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                if scheduled_time < now:
                    scheduled_time += timedelta(days=1)

                wait_seconds = (scheduled_time - now).total_seconds()
                print(f"[i] Scheduled reboot in {wait_seconds} seconds at {scheduled_time}")
                time.sleep(wait_seconds)
                print("[i] Rebooting now...")
                self.reboot()
                # Wait a bit in case reboot fails or is delayed
                time.sleep(60) 

        thread = threading.Thread(target=schedule_loop, daemon=True)
        thread.start()


    def handle_message(self, update, input_text, context):
        usr_msg = input_text.split()

        if input_text == "more commands":
            return """url <link>: open a link on the browser\nkill <proc>: terminate process\ncmd <command>: execute shell command\ncd <dir>: change directory\ndownload <file>: download a file"""

        if input_text == 'screen status':
            for proc in psutil.process_iter():
                if (proc.name() == "LogonUI.exe"):
                    return 'Screen is Locked'
            return 'Screen is Unlocked'
        
        if input_text == 'reboot':
            self.reboot()
            return "Sending reboot signal"

        if input_text == 'lock screen':
            try:
                ctypes.windll.user32.LockWorkStation()
                return "Screen locked successfully"
            except:
                return "Error while locking screen"

        if input_text == 'check in':
            buttons = [[KeyboardButton(name)] for name in self.CHECK_IN_DICTIONARY.keys()]
            buttons.append([KeyboardButton("All")])
            buttons.append([KeyboardButton("Back")])
            context.bot.send_message(
                chat_id=self.CHAT_ID,
                text="Who do you want to check in for?",
                reply_markup=ReplyKeyboardMarkup(buttons)
            )
            return None
        
        if input_text in self.CHECK_IN_DICTIONARY:
            return self.check_in(input_text)
        
        if input_text == 'all':
            results = []
            for name in self.CHECK_IN_DICTIONARY:
                results.append(self.check_in(name))
            return "\n\n".join(results)
        
        if input_text == "back":
            return self.start_command(update, context)

        # if input_text == 'unlock screen':
        #     try:
        #         response = self.unlock_screen()
        #         return response
        #     except Exception as e:
        #         return f"Error while unlocking screen: {str(e)}"

        if input_text == "take screenshot":
            try:
                update.message.bot.send_photo(
                    chat_id=self.CHAT_ID, photo=open(self.take_screenshot(), 'rb'))
                return None
            except Exception as e:
                return f"❌ Failed to take screenshot: {e}"

        if input_text == "paste clipboard":
            return pyperclip.paste()

        if input_text == "sleep":
            try:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "Windows was put to sleep"
            except:
                return "Cannot put Windows to sleep"

        if input_text == "list process":
            try:
                proc_list = []
                for proc in psutil.process_iter():
                    if proc.name() not in proc_list:
                        proc_list.append(proc.name())
                processes = "\n".join(proc_list)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            return processes

        if usr_msg[0] == 'kill':
            proc_list = []
            for proc in psutil.process_iter():
                p = proc_list.append([proc.name(), str(proc.pid)])
            try:
                for p in proc_list:
                    if p[0] == usr_msg[1]:
                        psutil.Process(int(p[1])).terminate()
                return 'Process terminated successfully'
            except:
                return 'Error occured while killing the process'

        if usr_msg[0] == 'url':
            try:
                webbrowser.open(usr_msg[1])
                return 'Link opened successfully'
            except:
                return 'Error occured while opening link'

        if usr_msg[0] == "cd":
            if usr_msg[1]:
                try:
                    os.chdir(usr_msg[1])
                except:
                    return "Directory not found !"
                res = os.getcwd()
                if res:
                    return res

        if usr_msg[0] == "download":
            if usr_msg[1]:
                if os.path.exists(usr_msg[1]):
                    try:
                        document = open(usr_msg[1], 'rb')
                        update.message.bot.send_document(
                            self.CHAT_ID, document)
                    except:
                        return "Something went wrong !"

        if usr_msg[0] == "cmd":
            res = subprocess.Popen(
                usr_msg[1:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
            stdout = res.stdout.read().decode("utf-8", 'ignore').strip()
            stderr = res.stderr.read().decode("utf-8", 'ignore').strip()
            if stdout:
                return (stdout)
            elif stderr:
                return (stderr)
            else:
                return ''

    def send_response(self, update, context):
        user_message = update.message.text
        if update.message.chat["username"] != str(self.USERNAME):
            print("[!] " + update.message.chat["username"] +
                  ' tried to use this bot')
            context.bot.send_message(
                chat_id=self.CHAT_ID, text="Nothing to see here.")
        else:
            user_message = user_message.encode(
                'ascii', 'ignore').decode('ascii').strip(' ')
            user_message = user_message[0].lower() + user_message[1:]
            response = self.handle_message(update, user_message, context)
            if response:
                if (len(response) > 4096):
                    for i in range(0, len(response), 4096):
                        context.bot.send_message(
                            chat_id=self.CHAT_ID, text=response[i:4096+i])
                else:
                    context.bot.send_message(
                        chat_id=self.CHAT_ID, text=response)

    def start_bot(self):
        updater = Updater(self.TOKEN, use_context=True)
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", self.start_command))
        dp.add_handler(MessageHandler(Filters.text, self.send_response))
        dp.add_error_handler(self.error)

        # Start background scheduler
        self.schedule(hour=7, minute=45)

        updater.start_polling()
        print("[+] BOT has started")
        updater.idle()


bot = TelegramBot()
bot.start_bot()
