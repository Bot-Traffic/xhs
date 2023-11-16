from fastapi import FastAPI, Request
from playwright.sync_api import sync_playwright
import time


app = FastAPI()

global_a1 = ""

stealth_js_path = "stealth.min.js"

def get_context_page(instance, stealth_js_path):
    chromium = instance.chromium
    browser = chromium.launch(headless=True)
    context = browser.new_context()
    context.add_init_script(path=stealth_js_path)
    page = context.new_page()
    return context, page


print("正在启动 playwright")
playwright = sync_playwright().start()

browser_context, context_page = get_context_page(playwright, stealth_js_path)
context_page.goto("https://www.xiaohongshu.com")
print("正在跳转至小红书首页")
time.sleep(5)

context_page.reload()
time.sleep(1)

cookies = browser_context.cookies()
for cookie in cookies:
    if cookie["name"] == "a1":
        global_a1 = cookie["value"]
        print("当前浏览器中 a1 值为：" + global_a1 + "，请将您的 cookie 中的 a1 也设置成一样，方可签名成功")
print("跳转小红书首页成功，等待调用")


def sign(uri, data, a1, web_session):
    global global_a1
    # if a1 != global_a1:
    #     browser_context.add_cookies([
    #         {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}
    #     ])
    #     context_page.reload()
    #     time.sleep(1)
    #     global_a1 = a1
    encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
    return {
        "x-s": encrypt_params["X-s"],
        "x-t": str(encrypt_params["X-t"])
    }


@app.post("/sign")
async def hello_world(request: Request):
    json = await request.json()
    uri = json["uri"]
    data = json["data"]
    a1 = json["a1"]
    web_session = json["web_session"]
    return sign(uri, data, a1, web_session)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
