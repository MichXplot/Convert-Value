from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

curs = {
    "RUB": ["₽", "ru"],
    "USD": ["$", "us"],
    "EUR": ["€", "eu"],
    "CNY": ["¥", "cn"],
    "KZT": ["₸", "kz"],
    "GBP": ["£", "gb"],
    "JPY": ["¥", "jp"],
    "AED": ["د.إ", "ae"],
    "BYN": ["Br", "by"]
}

def get_rate(cur):
    try:
        db = sqlite3.connect('currency.db')
        c = db.cursor()
        c.execute("SELECT rate_to_rub FROM rates WHERE currency_code=?", (cur,))
        res = c.fetchone()
        db.close()
        if res:
            return res[0]
    except:
        pass
    fb = {
        "RUB": 1.0,
        "USD": 95.0,
        "EUR": 105.0,
        "CNY": 13.0,
        "KZT": 0.2,
        "GBP": 125.0,
        "JPY": 0.65,
        "AED": 26.0,
        "BYN": 29.0
    }
    return fb.get(cur, 1.0)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={
        "res": "", "base": "RUB", "target": "USD", "amt": 1000, "curs": curs
    })

@app.post("/convert", response_class=HTMLResponse)
async def convert(request: Request, amt: float = Form(...), base: str = Form(...), target: str = Form(...)):
    r1 = get_rate(base) if base != "RUB" else 1.0
    r2 = get_rate(target) if target != "RUB" else 1.0
    rub = amt / r1
    res = round(rub * r2, 2)
    return templates.TemplateResponse(request=request, name="index.html", context={
        "amt": amt, "base": base, "target": target, "res": res, "curs": curs
    })


@app.get("/multi", response_class=HTMLResponse)
async def multi(request: Request, amt: float = 1000.0, base: str = "RUB"):
    targs = ["USD", "EUR", "CNY", "KZT", "GBP", "JPY", "AED", "BYN", "RUB"]

    if base in targs:
        targs.remove(base)
    r1 = get_rate(base) if base != "RUB" else 1.0
    lst = []
    for t in targs[:8]:
        r2 = get_rate(t) if t != "RUB" else 1.0
        rub = amt / r1
        v = round(rub * r2, 2)
        lst.append({"code": t, "val": v, "flag": curs[t][1]})
    return templates.TemplateResponse(request=request, name="multi.html", context={
        "amt": amt, "base": base, "lst": lst, "curs": curs
    })

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request, currency: str = "USD"):
    rates = []
    for name in ["currencies.db", "currency.db"]:
        try:
            db = sqlite3.connect(name)
            c = db.cursor()
            c.execute("SELECT date, rate, change_value FROM rates WHERE currency=?", (currency,))
            rates = c.fetchall()
            db.close()
            if rates:
                break
        except:
            pass
    if not rates:
        rates = [
            ["25.05.2026", "95.20", "+0.20"],
            ["24.05.2026", "95.00", "-0.15"],
            ["23.05.2026", "95.15", "+0.05"]
        ]
    return templates.TemplateResponse(request=request, name="history.html", context={
        "rates": rates, "currency": currency
    })

@app.get("/chart", response_class=HTMLResponse)
async def chart(request: Request, currency: str = "USD"):
    rows = []
    for name in ["currencies.db", "currency.db"]:
        try:
            db = sqlite3.connect(name)
            c = db.cursor()
            c.execute("SELECT date, rate FROM rates WHERE currency=?", (currency,))
            rows = c.fetchall()
            db.close()
            if rows:
                break
        except:
            pass
    if not rows:
        rows = [
            ["19.05", 94.5], ["20.05", 94.8], ["21.05", 95.0],
            ["22.05", 94.9], ["23.05", 95.15], ["24.05", 95.0], ["25.05", 95.2]
        ]
    dates = [r[0] for r in rows]
    rates = [r[1] for r in rows]
    return templates.TemplateResponse(request=request, name="chart.html", context={
        "dates": dates, "rates": rates, "currency": currency
    })


# 1. Отображение страницы покупки с передачей словаря курсов (GET)
@app.get("/buy", response_class=HTMLResponse)
async def buy_page(request: Request, amt: float = 1000.0, base: str = "RUB"):
    # Собираем все курсы относительно рубля для JS-калькулятора
    all_rates = {c: get_rate(c) if c != "RUB" else 1.0 for c in curs}
    return templates.TemplateResponse(request=request, name="buy.html", context={
        "request": request, "amt": amt, "base": base, "curs": curs, "rates": all_rates, "success": False
    })



@app.post("/buy/confirm", response_class=HTMLResponse)
async def buy_confirm(
        request: Request,
        user_name: str = Form(...),
        user_phone: str = Form(...),
        amt: float = Form(...),
        base: str = Form(...),
        target: str = Form(...)
):
    r1 = get_rate(base) if base != "RUB" else 1.0
    r2 = get_rate(target) if target != "RUB" else 1.0
    rub = amt / r1
    res = round(rub * r2, 2)

    try:
        db = sqlite3.connect('orders.db')
        c = db.cursor()
        c.execute("""
            INSERT INTO purchases (base_currency, target_currency, amount, result_amount, user_name, user_phone, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Новая')
        """, (base, target, amt, res, user_name, user_phone))
        db.commit()
        db.close()
        success = True
    except Exception as e:
        print(f"Ошибка записи в БД заказов: {e}")
        success = False

    all_rates = {c: get_rate(c) if c != "RUB" else 1.0 for c in curs}
    return templates.TemplateResponse(request=request, name="buy.html", context={
        "request": request,
        "success": success,
        "user_name": user_name,
        "amt": amt,
        "base": base,
        "target": target,
        "res": res,
        "curs": curs,
        "rates": all_rates
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)