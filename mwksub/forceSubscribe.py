import time
import logging
from Config import Config
from pyrogram import Client, filters
from helpers import forceSubscribe_sql as sql
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(lambda _, __, query: query.data == "onUnMuteRequest")
@Client.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
  user_id = cb.from_user.id
  chat_id = cb.message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    channel = chat_db.channel
    chat_member = client.get_chat_member(chat_id, user_id)
    if chat_member.restricted_by:
      if chat_member.restricted_by.id == (client.get_me()).id:
          try:
            client.get_chat_member(channel, user_id)
            client.unban_chat_member(chat_id, user_id)
            if cb.message.reply_to_message.from_user.id == user_id:
              cb.message.delete()
          except UserNotParticipant:
            client.answer_callback_query(cb.id, text="❗ ഇവിടെ കൊടുത്ത ചാനലിൽ വേഗം ജോയിൻ ചെയ്യൂ... എന്നിട്ട് താഴെ ഉള്ള 'UnMute Me' button അമർതൂ... എന്നാൽ മാത്രമേ നിങ്ങൾക്ക് ഇവിടെ മെസ്സേജ് അയക്കാൻ പറ്റൂ 🤷‍♀️.", show_alert=True)
      else:
        client.answer_callback_query(cb.id, text="❗ അച്ചോടാ.... 😇 നിന്നെ അഡ്മിൻസ് വേറെ എന്തോ കാര്യതിൻ മ്യുട്ട് ചെയ്തെക്കുവാണ് 🤷‍♀️.", show_alert=True)
    else:
      if not client.get_chat_member(chat_id, (client.get_me()).id).status == 'administrator':
        client.send_message(chat_id, f"❗ **{cb.from_user.mention} ഇങ്ങേർ കുറേ നേരമായി സ്വയം അണ്മ്യൂട്ട് ആക്കാൻ നോക്കുന്നു...🤷‍♀️ പക്ഷെ എനിക്ക് അവനെ അണ്മ്യൂട്ട് ആക്കാൻ കഴിയില്ല ഞാൻ അഡ്മിൻ അല്ല 😑 എന്നെ ഒന്നൂടെ അഡ്മിൻ ആക്കൂ 😇.**\n__#Leaving this chat...__")
        client.leave_chat(chat_id)
      else:
        client.answer_callback_query(cb.id, text="❗ Warning: Don't click the button if you can speak freely.", show_alert=True)



@Client.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
  chat_id = message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    user_id = message.from_user.id
    if not client.get_chat_member(chat_id, user_id).status in ("administrator", "creator") and not user_id in Config.SUDO_USERS:
      channel = chat_db.channel
      try:
        client.get_chat_member(channel, user_id)
      except UserNotParticipant:
        try:
          sent_message = message.reply_text(
              "{}, താങ്കൾ എന്റെ മൊയലാളി യുടെ ഈ [channel](https://t.me/{}) ഇപ്പോഴും **സബ്സ്ക്രൈബ് ചെയ്തിട്ടില്ല 🤫**. ദയവായി ഇവിടെ [join](https://t.me/{}) ചെയ്യൂ... എന്നിട്ട് **താഴെ കാണുന്ന Button അമർത്തൂ 🤷‍♀️** എന്നാൽ മാത്രമേ നിങ്ങൾക്ക് ഇവിടെ മെസ്സേജ് അയക്കാൻ ഒക്കൂ 😑.".format(message.from_user.mention, channel, channel),
              disable_web_page_preview=True,
              reply_markup=InlineKeyboardMarkup(
                  [[InlineKeyboardButton("UnMute Me", callback_data="onUnMuteRequest")]]
              )
          )
          client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        except ChatAdminRequired:
          sent_message.edit("❗ **ശിവനെ...😑 ഞാൻ അയിന് ഇവിടെ അഡ്മിൻ അല്ലാലോ.. 🤫.**\n__എന്നെ ബാൻ പെർമിഷൻ ഉള്ള അഡ്മിൻ ആക്കിയാലെ എനിക്ക് എന്തേലും ചെയ്യാൻ പറ്റൂ 🤷‍♀️.\n#Leaving this chat...__")
          client.leave_chat(chat_id)
      except ChatAdminRequired:
        client.send_message(chat_id, text=f"❗ **അച്ചോടാ... ഞാൻ ഈ @{channel} ഇൽ അഡ്മിൻ അല്ലാലോ 😐**\n__അവിടെയും എന്നെ ഒരു അഡ്മിൻ അക്കൂ... 😌.\n#Leaving this chat...__")
        client.leave_chat(chat_id)


@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status is "creator" or user.user.id in Config.SUDO_USERS:
    chat_id = message.chat.id
    if len(message.command) > 1:
      input_str = message.command[1]
      input_str = input_str.replace("@", "")
      if input_str.lower() in ("off", "no", "disable"):
        sql.disapprove(chat_id)
        message.reply_text("❌ **Force Subscribe നിർത്തി വെച്ചിരിക്കുന്നു 🤷‍♀️.**")
      elif input_str.lower() in ('clear'):
        sent_message = message.reply_text('**ഞാൻ മ്യൂട്ട് ആക്കിയ എല്ലാവരെയും അണ്മ്യൂട്ട് ആക്കുന്നു... ഇനി അതിന്റെ ഒരു കുറവ്‌ വേണ്ട 🤨**')
        try:
          for chat_member in client.get_chat_members(message.chat.id, filter="restricted"):
            if chat_member.restricted_by.id == (client.get_me()).id:
                client.unban_chat_member(chat_id, chat_member.user.id)
                time.sleep(1)
          sent_message.edit('✅ **ഞാൻ മ്യൂട്ട് ആക്കിയ എല്ലാവരെയും വിജയകരമായി അണ്മ്യൂട്ട് ആക്കിയിരിക്കുന്നു....😉**')
        except ChatAdminRequired:
          sent_message.edit('❗ **ശിവനെ...😑 ഞാൻ അയിന് ഇവിടെ അഡ്മിൻ അല്ലാലോ.. 🤫.**\n__എന്നെ ബാൻ പെർമിഷൻ ഉള്ള അഡ്മിൻ ആക്കിയാലെ എനിക്ക് എന്തേലും ചെയ്യാൻ പറ്റൂ 🤷‍♀️.\n#Leaving this chat...__')
      else:
        try:
          client.get_chat_member(input_str, "me")
          sql.add_channel(chat_id, input_str)
          message.reply_text(f"✅ **Force Subscribe നടപ്പിലാക്കിയിരിക്കുന്നു**\n__Force Subscribe നടപ്പിലാക്കി, ഇനി എല്ലാ ഗ്രൂപ്പ്‌ അംഗങ്ങളും ഈ [channel](https://t.me/{input_str}) ഇൽ ചെയ്താൽ മാത്രമെ ഗ്രൂപിൽ മെസ്സേജ് അയക്കാൻ പറ്റൂ.__", disable_web_page_preview=True)
        except UserNotParticipant:
          message.reply_text(f"❗ **അച്ചോടാ... ഞാൻ ഈ [channel](https://t.me/{input_str}) ഇൽ അഡ്മിൻ അല്ലാലോ 😐**\n__അവിടെയും എന്നെ ഒരു അഡ്മിൻ അക്കൂ... 😌.__", disable_web_page_preview=True)
        except (UsernameNotOccupied, PeerIdInvalid):
          message.reply_text(f"❗ **Invalid Channel Username.**")
        except Exception as err:
          message.reply_text(f"❗ **ERROR:** ```{err}```")
    else:
      if sql.fs_settings(chat_id):
        message.reply_text(f"✅ **ഈ ഗ്രൂപിൽ Force Subscribe നടപ്പിലാക്കി 😎.**\n__ഇതാണ് നമ്മുടെ [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__", disable_web_page_preview=True)
      else:
        message.reply_text("❌ **ഈ ഗ്രൂപ്പിൽ ഫോഴ്സ് സബ്സ്ക്രൈബ് ഓഫ് ആണ്.**")
  else:
      message.reply_text("❗ **പോയെടാ വധൂരി... നീ ഏതാ... സ്വന്തമായിട്ട് ഒരു ഗ്രൂപ്പ്‌ ഒക്കെ തുടങ്ങു... എന്നിട്ട് എനിക്കിട്ട് ഉണ്ടാക്കാൻ വാ**\n__You have to be the group creator to do that.__")
