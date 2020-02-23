from telegram.ext import Updater, CommandHandler
from memewiki import get_raw_text, get_raw_page
from utils import parse_jisfw_text
from config import apikey


def hello(update, context):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


def view_jisfw_tag(update, ctx):
    id = ctx.args[0]
    update.message.reply_text(
        "正在 MemeWiki 搜索 t.me/JISFW/{} ...".format(id)
    )
    text = get_raw_text("JISFW:" + id)
    if text is None:
        update.message.reply_text("MemeWiki 上没有此页。")
    else:
        obj = parse_jisfw_text(text)
        if "redirect" in obj:
            update.message.reply_text("这是一个重定向页面。请参见 " + obj["redirect"] + "。")
            return
        text = ""
        if len(obj["id"]) > 1:
            text += "这是一组梗，包括{}\n".format("|".join(obj["id"]))
        if len(obj["entities"]):
            text += "实体：" + ", ".join(obj["entities"]) + "\n"
        if len(obj["categories"]):
            text += "分类：#" + " , #".join(obj["categories"]) + "\n"
        if obj["source"]:
            text += "来源：" + obj["source"]
        if text == "":
            text = "MemeWiki 上有此页，但没有任何标签。"
        update.message.reply_text(text)


def add_jisfw_tag(update, ctx):
    id = ctx.args[0]
    update.message.reply_text(
        "正在 MemeWiki 搜索 t.me/JISFW/{} ...".format(id)
    )
    page = get_raw_page("JISFW:"+id)
    if page is None:
        update.message.reply_text("MemeWiki 上没有此页。")
    # else:
    #     update.message.reply_text(parse_jisfw_text(text))


updater = Updater(apikey, use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('tagof', view_jisfw_tag))
updater.dispatcher.add_handler(CommandHandler('addtag', add_jisfw_tag))

updater.start_polling()
updater.idle()
