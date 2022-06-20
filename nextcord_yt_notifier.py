from re import search
from nextcord import ChannelType, Interaction, SlashOption, Intents, SyncWebhook
from nextcord.abc import GuildChannel
from os import getenv
from sqlite3 import connect
from nextcord.ext import commands, tasks
from dotenv import load_dotenv
from requests import get

webhook_intent=Intents(webhooks=True)
bot = commands.Bot(intents=webhook_intent)
db = connect('youtubedata.db')

load_dotenv()
TOKEN=getenv('token')


@bot.event
async def on_ready():
    print("Bot Now Online!")

    #starting checking for vidoes everytime the bot's go online
    checkforvideos.start()

#checking for videos every 5 minutes


@tasks.loop(minutes=5)
async def checkforvideos():

  #printing here to show
  print("Now Checking!")

  #checking for all the channels in youtubedata.db file
  channel_ids = db.execute("SELECT channel_id FROM youtube").fetchall()
  for i in channel_ids:
    print(f"Now Checking For {i[0]}")

    #getting youtube channel's url
    channel = f"https://www.youtube.com/channel/{i[0]}"

    #getting html of the /videos page
    html = get(channel+"/videos").text

    #getting the latest video's url
    #put this line in try and except block cause it can give error some time if no video is uploaded on the channel
    try:
      latest_video_url = "https://www.youtube.com/watch?v=" + \
          search('(?<="videoId":").*?(?=")', html).group()
    except:
      continue

    #checking if url in youtubedata.db file is not equals to latest_video_url

    latest_video = db.execute(
        "SELECT latest_video FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()[0]

    if not str(latest_video) == latest_video_url:

      #changing the latest_video_url
      db.execute("UPDATE youtube SET latest_video = ? WHERE channel_id = ?",
                 (latest_video_url, i[0],))
      db.commit()

      #getting the channel to send the message
      webhook_url = db.execute(
          "SELECT webhook FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()
      webhook = SyncWebhook.from_url(webhook_url[0])

      #sending the msg in discord channel
      #you can mention any role like this if you want
      channel_name = db.execute(
          "SELECT channel_name FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()

      mention = db.execute(
          "SELECT mention FROM youtube WHERE channel_id = ?", (i[0],)).fetchone()

      if mention[0] == "None":
        msg = f"{channel_name[0]} just uploaded a new video!\nCheck it out: {latest_video_url}"
      else:
        msg = f"{mention[0]}\n{channel_name[0]} just uploaded a new video!\nCheck it out: {latest_video_url}"
      #if you'll send the url discord will automaitacly create embed for it
      #if you don't want to send embed for it then do <{latest_video_url}>

      webhook.send(msg)
      print(f"{latest_video_url} found and posted")

#creating command to add more youtube accounds data in youtubedata.db file



bot.run(TOKEN)
