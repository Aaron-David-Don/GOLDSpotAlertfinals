import gradio as gr
import asyncio
from playwright.async_api import async_playwright
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
import threading
import math

# Global variable to control stopping
stop_flag = False

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
        
        await browser.close()
        return sideval, tabval

async def send_notification(api_id, api_hash, number, message):
    client = TelegramClient('session', api_id, api_hash)
    await client.start()
    try:
        user = await client.get_entity(number)
        receiver = InputPeerUser(user.id, user.access_hash)
        await client.send_message(receiver, message, parse_mode='html')
    except Exception as e:
        print(f"Error: {e}")
    await client.disconnect()

async def scrape_amazon(url, sidel, sideh, tabl, tabh, number):
    
    global stop_flag
    api_id = '25126202'
    api_hash = '51bb6b6de4f0faec05fba079ee976bba'
    
    sideval_low_notified = False
    sideval_high_notified = False
    tabval_low_notified = False
    tabval_high_notified = False
    
    if (sidel is None ) and \
        (sideh is None ) and \
        (tabl is None ) and \
        (tabh is None ):
        stop_flag = True
        sideval, tabval = await checking(url)
        message = f"The current Gold Spot  value is $ {sideval} and Gold (999) value is Rs: {tabval/10}"
        await send_notification(api_id, api_hash, number, message)
        return

    while stop_flag== False:
        sideval, tabval = await checking(url)
        

        if not sideval_low_notified and sidel is not None and math.trunc(sideval) <= sidel:
            message = f'Gold Spot  $ : {sideval} 📉.'
            await send_notification(api_id, api_hash, number, message)
            sideval_low_notified = True

        if not sideval_high_notified and sideh is not None and math.trunc(sideval) >= sideh:
            message = f'Gold Spot  $ : {sideval} 📈 '
            await send_notification(api_id, api_hash, number, message)
            sideval_high_notified = True

        if not tabval_low_notified and tabl is not None and math.trunc(tabval) <= tabl:
            message = f'Gold (999) Rs: {tabval/10} 📉 '
            await send_notification(api_id, api_hash, number, message)
            tabval_low_notified = True

        if not tabval_high_notified and tabh is not None and math.trunc(tabval) >= tabh:
            message = f'Gold (999) Rs: {tabval/10} 📈 '
            await send_notification(api_id, api_hash, number, message)
            tabval_high_notified = True

        # Stop the loop only if all conditions for notifications have been met
        if (sidel is None or sideval_low_notified) and \
           (sideh is None or sideval_high_notified) and \
           (tabl is None or tabval_low_notified) and \
           (tabh is None or tabval_high_notified):
            stop_flag = True  # Stop the loop when all relevant notifications have been sent
            break

        await asyncio.sleep(1)  # Wait before checking again to prevent spamming

    message = "Scraping stopped. All conditions have been met."
    await send_notification(api_id, api_hash, number, message)

def start_scraping(side_low, side_high, table_low, table_high, phone_number):
    
    api_id = '25126202'
    api_hash = '51bb6b6de4f0faec05fba079ee976bba'
    base_message=f'Given values are :\n Gold Spot  $  low: {side_low} \nGold Spot  $ high: {side_high}\nGold (999) low Rs: {table_low} \nGold (999) high Rs: {table_high}'
    asyncio.run(send_notification(api_id, api_hash, phone_number , base_message))
    global stop_flag
    stop_flag = False
    url = "http://www.ambicaaspot.com/liverate.html"
    
    # Multiply table low and high by 10 inside the function
    table_low = table_low * 10 if table_low else None
    table_high = table_high * 10 if table_high else None

    thread = threading.Thread(target=lambda: asyncio.run(scrape_amazon(
        url, 
        float(side_low) if side_low else None, 
        float(side_high) if side_high else None, 
        table_low if table_low else None, 
        table_high if table_high else None, 
        phone_number
    )))
    thread.start()
    if phone_number=="":
        stop_flag = True
        return "Kindly enter your Phone number"

    return "Scraping started. You'll be notified when conditions are met."

def stop_scraping(phone_number):
    global stop_flag
    stop_flag = True
    api_id = '25126202'
    api_hash = '51bb6b6de4f0faec05fba079ee976bba'
    stop_message = "You have manually stopped scraping"
    asyncio.run(send_notification(api_id, api_hash, phone_number , stop_message))
    return "Scraping stopped."

with gr.Blocks() as interface:
    with gr.Row():
        gr.Markdown("# GOLD WATCH")
        gr.Markdown("Kindly enter your required target values and phone number(for notification) and leave the blocks blank if not required ")
    
    with gr.Row():
        with gr.Column():
            side_low = gr.Number(label="Gold Spot  $ Low", value=None)
            side_high = gr.Number(label="Gold Spot  $ High",value=None)
            table_low = gr.Number(label="Gold (999) Rs Low",value=None)
            table_high = gr.Number(label="Gold (999) Rs High",value=None)
            phone_number = gr.Textbox(label="Phone Number (with '+')",value=None)
            start_button = gr.Button("Start Scraping")
            stop_button = gr.Button("Stop Scraping")
        
    output = gr.Textbox(label="Status", lines=4)

    start_button.click(start_scraping, inputs=[side_low, side_high, table_low, table_high, phone_number], outputs=output)
    stop_button.click(stop_scraping, inputs=[phone_number], outputs=output)

interface.launch()
