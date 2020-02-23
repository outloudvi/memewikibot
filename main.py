from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, InlineQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.utils.helpers import escape_markdown
from memewiki import get_raw_text, get_raw_page, get_smw_object, search_smw_query, commit_edit
from utils import parse_jisfw_text
from config import apikey
from tinydb import write as db_write
from tinydb import read as db_read
from uuid import uuid4
import json


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
    if len(ctx.args) < 2:
        update.message.reply_markdown("用法： /addtag ID 标签名")
        return
    meme_id = ctx.args[0]
    tag_to_add = ctx.args[1]
    pagename = "JISFW:" + meme_id
    smw = get_smw_object(pagename)
    if "Tag" in smw and tag_to_add in smw["Tag"]:
        update.message.reply_markdown(
            "#{} 已存在于 {} 中。".format(tag_to_add, pagename))
        return
    if smw == {}:
        # Page doesn't exist
        keyboard = [[InlineKeyboardButton("Yes", callback_data=db_write({
            "action": "create_page",
            "pagename": pagename,
            "jisfw_id": meme_id,
            "tag_to_add": tag_to_add
        })),
            InlineKeyboardButton("No", callback_data=db_write({
                "action": ""
            }))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            '此页 {} 不存在。要创建并添加标签 #{} 么？注意，你的显示名将会出现在编辑摘要中。'.format(pagename, tag_to_add), reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("Yes", callback_data=db_write({
            "action": "add_tag",
            "pagename": pagename,
            "tag_to_add": tag_to_add
        })),
            InlineKeyboardButton("No", callback_data=db_write({
                "action": ""
            }))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            '{} 已确定。要添加标签 #{} 么？注意，你的显示名将会出现在编辑摘要中。'.format(pagename, tag_to_add), reply_markup=reply_markup)


def add_jisfw_tag_handler(update, ctx):
    query = update.callback_query
    data = db_read(update.callback_query.data)
    if data["action"] == "create_page":
        query.edit_message_text(text="正在创建页面 {} 并添加标签 #{}。".format(
            data["pagename"], data["tag_to_add"]))
        commit_edit(data, update.callback_query.from_user)
        query.edit_message_text(text="已完成。")
    elif data["action"] == "add_tag":
        query.edit_message_text(text="正在添加标签 #{} 至 {}。".format(
            data["tag_to_add"], data["pagename"]))
        commit_edit(data, update.callback_query.from_user)
        query.edit_message_text(text="已完成。")
    else:
        query.edit_message_text(text="操作已结束。")


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


def error_callback(update, context):
    print(context.error.args, context.error.with_traceback)


def inline_handler(update, context):
    """Handle the inline query."""
    query = update.inline_query.query
    if query == "":
        update.inline_query.answer([])
    lines = search_smw_query("[[Tag::{}]]".format(query))
    results = []
    for i in lines["results"]:
        results.append(InlineQueryResultArticle(
            id=uuid4(),
            title=i,
            input_message_content=InputTextMessageContent(
                "t.me/" + i.replace(":", "/")
            )))
    update.inline_query.answer(results)


updater = Updater(apikey, use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('info', view_jisfw_info))
updater.dispatcher.add_handler(CommandHandler('entity', search_jisfw_entity))
updater.dispatcher.add_handler(CommandHandler('tag', search_jisfw_tag))
updater.dispatcher.add_handler(CommandHandler('source', search_jisfw_source))
updater.dispatcher.add_handler(CommandHandler('addtag', add_jisfw_tag))
updater.dispatcher.add_handler(CallbackQueryHandler(add_jisfw_tag_handler))
updater.dispatcher.add_handler(InlineQueryHandler(inline_handler))
updater.dispatcher.add_error_handler(error_callback)

updater.start_polling()
updater.idle()
