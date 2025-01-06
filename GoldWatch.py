import gradio as gr
import asyncio
from playwright.async_api import async_playwright
from twilio.rest import Client
import os
import json
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser


async def checking(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        yes = await page.locator('div.cross').is_visible()
        if yes:
            await page.wait_for_selector('div.cross')
            await page.click('span.close')
            await asyncio.sleep(2)
        await asyncio.sleep(3)

        await page.wait_for_selector('div#divSpot')
        product_elements = await page.query_selector('div#divSpot')
        hmm = await product_elements.query_selector('tr.product-title-text')
        title_el = await hmm.query_selector('span.h') or await hmm.query_selector('span.e') or await hmm.query_selector('span.l')
        sideval = float(await title_el.inner_text()) if title_el else "N/A"
        print("The side value is: ", sideval)

        await page.wait_for_selector('div#divProduct')
        blah = await page.query_selector('div#divProduct')
        op = await blah.query_selector('div.t1mainproduct')
        ip = await op.query_selector_all('td.t1wth3')
        hg = ip[1]
        tit = await hg.query_selector('span.l.widthcls') or await hg.query_selector('span.h.widthcls') or await hg.query_selector('span.e.widthcls')
        tabval = float(await tit.inner_text()) if tit else "N/A"
        print("The table value is: ", tabval)

        return sideval, tabval

    await browser.close()
    
def choks(given,taken):
    if given == 0:
        return False
    else:
        return (given<=taken)

def jimmy(taken,given):
    if given == 0:
        return False
    else:
        return (taken<=given)

async def scrape_amazon(url, sidel, sideh, tabl, tabh, number):
    sideval, tabval = await checking(url)
    while choks(sidel,sideval) or jimmy(sideval,sideh) or choks(tabl,tabval) or jimmy(tabval,tabh):
        
        sideval, tabval = await checking(url)
        
        if jimmy(sideval, sidel) or choks(sideh,sideval)  or jimmy(tabval,tabl) or choks(tabh,tabval) :
            
            api_id = 'use ur api id from telegram org apps'
            api_hash = 'use ur api hash from telegram org apps'
            token = 'use ur token from telegram bot'
            message = f'THE PRICE OF GOLD 1KG IS {tabval} AND THE PRICE OF GOLD SPOT IS {sideval}'
            phone = 'ur number wiht +(country code)'
            
            # Use synchronous client for Telegram
            client = TelegramClient('session', api_id, api_hash)
            await client.start()  # Handles login and connection
            try:
                user = await client.get_entity(number)  # Asynchronously get entity
                user_id = user.id
                access_hash = user.access_hash
                receiver = InputPeerUser(user_id, access_hash)
                await client.send_message(receiver, message, parse_mode='html')
            except Exception as e:
                print(f"Error: {e}")
            await client.disconnect()
    else:
        if jimmy(sideval,sidel) or choks(sideh,sideval) or jimmy(tabval,tabl) or choks(tabh,tabval) :
            api_id = 'use ur api id from telegram org apps'
            api_hash = 'use ur api hash from telegram org apps'
            token = 'use ur token from telegram bot'
            message = f'THE PRICE OF GOLD 1KG IS {tabval} AND THE PRICE OF GOLD SPOT IS {sideval}'
            phone = 'ur number wiht +(country code)'
            
            # Use synchronous client for Telegram
            client = TelegramClient('session', api_id, api_hash)
            await client.start()  # Handles login and connection
            try:
                user = await client.get_entity(number)  # Asynchronously get entity
                user_id = user.id
                access_hash = user.access_hash
                receiver = InputPeerUser(user_id, access_hash)
                await client.send_message(receiver, message, parse_mode='html')
            except Exception as e:
                print(f"Error: {e}")
            await client.disconnect()


# Wrapper function for Gradio interface
def start_scraping(side_low, side_high, table_low, table_high, phone_number):
    url = "http://www.ambicaaspot.com/liverate.html"
    asyncio.run(scrape_amazon(url, float(side_low), float(side_high), float(table_low), float(table_high), phone_number))
    return f"The current gold values are :\nSide Low: {side_low}, Side High: {side_high}, Table Low: {table_low}, Table High: {table_high} \nand a notification has been sent to your mobile number"

# Gradio Interface
interface = gr.Interface(
    fn=start_scraping,
    inputs=[
        gr.Number(label="Side Low"),
        gr.Number(label="Side High"),
        gr.Number(label="Table Low"),
        gr.Number(label="Table High"),
        gr.Textbox(label="Phone Number (with '+')"),
    ],
    outputs="text",
    title="GOLD RATE",
    description="Kindly enter your required target values and phone number(for notification) and leave the blocks blank if not required: ",
)

# Launch the interface
interface.launch(server_name="0.0.0.0", server_port=7860)
