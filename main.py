from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.utils.helpers import escape_markdown
from memewiki import get_raw_text, get_raw_page, get_smw_object, search_smw_query, commit_edit
from utils import parse_jisfw_text
from config import apikey
import tinydb as db
from uuid import uuid4
import json
import re


def hello(update, context):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


def view_jisfw_info(update, ctx, override_id=None):
    id = -1
    if ctx.args and len(ctx.args):
        id = ctx.args[0]
    if override_id:
        id = override_id
    if id == -1:
        return
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
        text = "JISFW:{}".format(id)
        if len(obj["id"]) > 1:
            text += "这是一组梗，包括{}\n".format("|".join(obj["id"]))
        if "Entity" in smw:
            entities = list(
                map(lambda x: x["item"].replace("#0##", ""), smw["Entity"]))
            if len(entities):
                text += "实体：" + ", ".join(entities) + "\n"
        if "Tag" in smw:
            tags = list(
                map(lambda x: x["item"].replace("#0##", ""), smw["Tag"]))
            if len(tags):
                text += "分类：#" + " , #".join(tags) + "\n"
        if "Source" in smw:
            text += "来源：" + smw["Source"][0]["item"]
        if text == "":
            text = "MemeWiki 上有此页，但没有任何标签。"
        update.message.reply_text(text)


def add_jisfw_tag(update, ctx):
    if len(ctx.args) < 2:
        update.message.reply_markdown("用法： /addtag ID ...标签名")
        return
    meme_id = ctx.args[0]
    if not meme_id.isnumeric():
        update.message.reply_markdown("ID 应是一个数字。")
        return
    tags_to_add = ctx.args[1:]
    pagename = "JISFW:" + meme_id
    smw = get_smw_object(pagename)
    for tag in tags_to_add:
        if "Tag" in smw and tag in smw["Tag"]:
            update.message.reply_markdown(
                "#{} 已存在于 {} 中。".format(tag, pagename))
            return
    base = ""
    if smw == {}:
        # Page doesn't exist
        keyboard = [[InlineKeyboardButton("Yes", callback_data=db.write_tmp({
            "action": "create_page",
            "pagename": pagename,
            "jisfw_id": meme_id,
            "tags_to_add": tags_to_add
        })),
            InlineKeyboardButton("No", callback_data=db.write_tmp({
                "action": ""
            }))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        base = '此页 {} 不存在。'.format(pagename)
    else:
        keyboard = [[InlineKeyboardButton("Yes", callback_data=db.write_tmp({
            "action": "add_tag",
            "pagename": pagename,
            "tags_to_add": tags_to_add
        })),
            InlineKeyboardButton("No", callback_data=db.write_tmp({
                "action": ""
            }))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        base = '{} 已确定。'.format(pagename)
    update.message.reply_text(
        base + '要添加标签 #{} 么？注意，你的显示名将会出现在编辑摘要中。'.format(", #".join(tags_to_add)), reply_markup=reply_markup)


def add_jisfw_tag_handler(update, ctx):
    query = update.callback_query
    data = db.read_tmp(update.callback_query.data)
    tag_list_str = "#" + ", #".join(data["tags_to_add"])
    basetext = ""
    if data["action"] == "create_page":
        basetext = "正在创建页面 {} 并添加标签 {}...".format(
            data["pagename"], tag_list_str)

    elif data["action"] == "add_tag":
        basetext = "正在向 {} 添加标签 {}...".format(
            data["pagename"], tag_list_str)
    else:
        query.edit_message_text(text="操作已结束。什么都没有发生。")
        return
    query.edit_message_text(text=basetext)
    commit_edit(data, update.callback_query.from_user)
    query.edit_message_text(text=basetext + " 完成。")


def search_prop(update, ctx, prop):
    print("Searching", prop, ctx.args[0])
    if type(prop) == list:
        result = search_smw_query(" OR".join(
            list(map(lambda x: "[[{}::{}]]".format(x, ctx.args[0]), prop))))
    else:
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
    search_prop(update, ctx, ["Tag", "Entity"])


def search_jisfw_source(update, ctx):
    search_prop(update, ctx, "Source")


def error_callback(update, context):
    print(context.error.args, context.error.with_traceback)


def inline_handler(update, context):
    """Handle the inline query."""
    query = update.inline_query.query
    if query == "":
        update.inline_query.answer([])
    lines = search_smw_query(
        "[[Tag::{}]] OR [[Entity::{}]]".format(query, query))
    results = []
    for i in lines["results"]:
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=i,
            input_message_content=InputTextMessageContent(
                "#" + query + ": t.me/" + i.replace(":", "/"), parse_mode="Markdown"
            )))
    if len(results) == 0:
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title="啥都妹有", input_message_content=InputTextMessageContent(
                "#" + query + ": 啥都妹有"
            )))
    update.inline_query.answer(results)


JISFW_REGEX = re.compile(r"JISFW[:/]([0-9]+)( \?)?", re.I)


def check_pm_text(update, context):
    if not update.message:
        return
    if update.message.chat.type == "private":
        text = update.message.text
        print(text)
        match = JISFW_REGEX.search(text)
        if match:
            view_jisfw_info(update, context, match.group(1))


db.load("db.json")

updater = Updater(apikey, use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('info', view_jisfw_info))
updater.dispatcher.add_handler(CommandHandler('entity', search_jisfw_entity))
updater.dispatcher.add_handler(CommandHandler('tag', search_jisfw_tag))
updater.dispatcher.add_handler(CommandHandler('source', search_jisfw_source))
updater.dispatcher.add_handler(CommandHandler('addtag', add_jisfw_tag))
updater.dispatcher.add_handler(CallbackQueryHandler(add_jisfw_tag_handler))
updater.dispatcher.add_handler(InlineQueryHandler(inline_handler))
updater.dispatcher.add_handler(MessageHandler(Filters.text, check_pm_text))
updater.dispatcher.add_error_handler(error_callback)

updater.start_polling()
updater.idle()

db.save("db.json")
