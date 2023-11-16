from fastapi import FastAPI, Request
import asyncio
from playwright.async_api import async_playwright 


app = FastAPI()

global_a1 = ""

stealth_js_path = "stealth.min.js"
browser_context = None 
context_page = None

async def get_context_page(instance, stealth_js_path):
    chromium = instance.chromium
    browser = await chromium.launch(headless=True)
    context = await browser.new_context()
    await context.add_init_script(path=stealth_js_path)
    page = await context.new_page()
    return context, page



async def sign(uri, data, a1, web_session):
    global global_a1
    # if a1 != global_a1:
    #     browser_context.add_cookies([
    #         {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}
    #     ])
    #     context_page.reload()
    #     time.sleep(1)
    #     global_a1 = a1
    encrypt_params = await context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
    return {
        "x-s": encrypt_params["X-s"],
        "x-t": str(encrypt_params["X-t"])
    }

async def global_setup():
    global global_a1, browser_context, context_page
    async with async_playwright() as p:
        browser_context, context_page = await get_context_page(p, stealth_js_path)
        await context_page.goto("https://www.xiaohongshu.com")
        # Replace time.sleep with asyncio.sleep in async context
        await asyncio.sleep(5)
        await context_page.reload()
        await asyncio.sleep(1)
        cookies = await browser_context.cookies()
        for cookie in cookies:
            if cookie["name"] == "a1":
                global_a1 = cookie["value"]
                print(f"当前浏览器中 a1 值为：{global_a1}，请将您的 cookie 中的 a1 也设置成一样，方可签名成功")


@app.on_event("startup")
async def startup_event():
    await global_setup()

@app.post("/sign")
async def hello_world(request: Request):
    json = await request.json()
    uri = json["uri"]
    data = json["data"]
    a1 = json["a1"]
    web_session = json["web_session"]
    return await sign(uri, data, a1, web_session)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app="app-f:app", host="0.0.0.0", port=5005, loop="uvloop", workers=1)
