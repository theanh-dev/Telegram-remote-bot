# Telegram-Remote-Desktop
This program is used to remotely control your PC from your Telegram app. <b> Please use this responsibly </b>.<br>
Full blogpost [here](https://ahmed-z.github.io/the-blog/Control-your-Windows-computer-using-Telegram).
<p align="center">
  <img src="https://github.com/Ahmed-Z/Telegram-Remote-Desktop/blob/master/telegram-final-product.png" style="height:600px;" >
</p>

# Features

* Check screen status (Locked or unlocked).
* Lock screen.
* Take screenshots.
* Paste clipboard.
* List running processes.
* Kill running processes.
* Open URL in computer browser.
* Navigate file system.
* Execute system commands.
* Download files from computer.
* Put computer in sleep mode.

# Installation
This program is meant to be running on the PC you want to control remotely.

`git clone https://github.com/theanh-dev/Telegram-remote-bot.git`<br>

This program uses [Python 3.11](https://www.python.org/downloads/release/python-3110/), newer version of python will not work.

`cd Telegram-Remote-Desktop` <br><br>
After downloading you have to install dependencies:<br>
`pip3 install -r requirements.txt`

Run the bot with 
`py telegram-remote-desktop.py`

You can chat with your bot with `/start`

<h3>Configuration</h3>

You need to create a bot via @BotFather using the Telegram app to get the access token.<br>

Afterward, start a chat with @RawDataBot to retrieve your chat id.

You need to create `auth.json` file containing your access token, chat id and your telegram username.

```
{
    "TOKEN":"YOUR TOKEN",
    "CHAT_ID": "YOUR CHAT ID",
    "USERNAME: "YOUR TELEGRAM USERNAME"
}
```
<b><span style="color:red">IMPORTANT</span></b> | Only the account of the specified username is able to use the bot.

# Custom features
* Run multiple file at the same time
  - Create `check-in-list.json` file with format 
   ```
  {
      "name":"Your method name",
      "path": "file path to be ran"
  }
  ```
  - You can customize how check-in method behaves by modifying the `def check_in` and `def handle_message`
* Automatically schedule at a specific time: `def schedule`