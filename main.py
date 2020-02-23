from telegram.ext import Updater, CommandHandler
from memewiki import get_raw_text, get_raw_page, get_smw_object, search_smw_query
from utils import parse_jisfw_text
from config import apikey


def hello(update, context):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


def view_jisfw_info(update, ctx):
    id = ctx.args[0]
    update.message.reply_text(
        "正在 MemeWiki 搜索 t.me/JISFW/{} ...".format(id)
    )
    text = get_raw_text("JISFW:" + id)
    if text is None:
        update.message.reply_markdown(
            "MemeWiki 上没有此页。[在此创建](https://meme.outv.im/wiki/JISFW:{}?action=edit)。".format(id))
    else:
        obj = parse_jisfw_text(text)
        smw = get_smw_object("JISFW:" + id)
        if "redirect" in obj:
            update.message.reply_text("这是一个重定向页面。请参见 " + obj["redirect"] + "。")
            return
        text = ""
        if len(obj["id"]) > 1:
            text += "这是一组梗，包括{}\n".format("|".join(obj["id"]))
        if "Entity" in smw:
        entities = list(map(lambda x: x["item"], smw["Entity"]))
        if len(entities):
            text += "实体：" + ", ".join(entities) + "\n"
        if "Tag" in smw:
        tags = list(map(lambda x: x["item"], smw["Tag"]))
        if len(tags):
            text += "分类：#" + " , #".join(tags) + "\n"
        if "Source" in smw:
            text += "来源：" + smw["Source"][0]["item"]
        if text == "":
            text = "MemeWiki 上有此页，但没有任何标签。"
        update.message.reply_text(text)


def add_jisfw_tag(update, ctx):
    update.message.reply_markdown(
        "此功能尚未完成，但可在 [这里](https://meme.outv.im/wiki/JISFW:{}) 修改标签。".format(ctx.args[0])
    )


def search_prop(update, ctx, prop):
    print("Searching", prop, ctx.args[0])
    result = search_smw_query("[[{}::{}]]".format(prop, ctx.args[0]))
    update.message.reply_markdown(
        "搜索 **{}::{}** \n".format(prop, ctx.args[0]) +
        "结果：\n" + "\n".join(list(map(lambda x: "[{}](t.me/{})".format(x, x.replace(":", "/")), result["results"]))) + "\n\n" +
        "第{}页，本页{}条结果，用时{}s".format(
            result["meta"]["offset"]+1, result["meta"]["count"], result["meta"]["time"])
    )


def search_jisfw_entity(update, ctx):
    search_prop(update, ctx, "Entity")

def search_jisfw_tag(update, ctx):
    search_prop(update, ctx, "Tag")


def search_jisfw_source(update, ctx):
    search_prop(update, ctx, "Source")


updater = Updater(apikey, use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('info', view_jisfw_info))
updater.dispatcher.add_handler(CommandHandler('entity', search_jisfw_entity))
updater.dispatcher.add_handler(CommandHandler('tag', search_jisfw_tag))
updater.dispatcher.add_handler(CommandHandler('source', search_jisfw_source))
updater.dispatcher.add_handler(CommandHandler('addtag', add_jisfw_tag))
updater.dispatcher.add_handler(CommandHandler('deltag', add_jisfw_tag))

updater.start_polling()
updater.idle()
