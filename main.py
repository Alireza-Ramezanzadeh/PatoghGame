import os
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="PatoghGame Vice City API", version="2.0.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "store.json")
ADMIN_SECRET = os.getenv("ADMIN_KEY", "patogh2026")

os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "templates"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# GTA VI Vice City Themed Seed Data
DEFAULT_DATA = {
    "broadcast": "📻 رادیو وایس‌سیتی (Vice FM 98.5): پلیس لئونیدا اعلام کرد مسابقات شبانه پاتوق در بلوار Ocean Drive آزاد و رایگان است! از سرعت مجاز لذت ببرید.",
    "servers": [
        {
            "id": "mc-malibu",
            "venue_name": "کلوب مالیبو (The Malibu Club)",
            "city_zone": "منطقه ساحلی Ocean Beach",
            "name": "سرور ماینکرفت پاتوق (سوروایول و تجارت شهر)",
            "game": "Minecraft 1.20+",
            "ip": "play.patoghgame.ir",
            "port": "25565",
            "status": "online",
            "players": 28,
            "max_players": 120,
            "ping": "21ms",
            "version": "Java & Bedrock (رسمی و کرک)",
            "wanted_level": 2,
            "description": "پاتوق اصلی گیمرهای شهر در قلب وایس‌سیتی. ساخت و ساز آزاد، تجارت کالا با دیگر بازیکنان و رویدادهای شبانه با پینگ فوق‌العاده پایین."
        },
        {
            "id": "mc-bedwars-arena",
            "venue_name": "آرنای مسابقات زیرزمینی (Vice Underground)",
            "city_zone": "اسکله پاتوق سیتی - Dock 9",
            "name": "میدان مسابقات بدوارز (Bedwars Street Cup)",
            "game": "Minecraft Bedwars",
            "ip": "event.patoghgame.ir",
            "port": "25565",
            "status": "online",
            "players": 14,
            "max_players": 32,
            "ping": "18ms",
            "version": "1.8.9 - 1.20+",
            "wanted_level": 4,
            "description": "نبردهای حذفی و پر سرعت بر سر تخت‌های محافظت شده. مسابقه تیمی بدون تقلب با سیستم ضد چیت مدرن لئونیدا."
        },
        {
            "id": "cs2-docks",
            "venue_name": "انبار کانتینری وایس‌پورت (Vice Port Docks)",
            "city_zone": "منطقه صنعتی Vice Port Industrial",
            "name": "سرور تاکتیکال ۵v5 کانتر ۲ (CS2 Shootout)",
            "game": "Counter-Strike 2",
            "ip": "cs2.patoghgame.ir",
            "port": "27015",
            "status": "online",
            "players": 10,
            "max_players": 10,
            "ping": "24ms",
            "version": "128 Tickrate / Matchmaking",
            "wanted_level": 5,
            "description": "میدان آتش و رویارویی مسلحانه تیم‌های خلافکار شهر بر روی مپ‌های Mirage و Inferno با لیدربرد هفتگی."
        }
    ],
    "events": [
        {
            "id": "ev-bedwars-heist",
            "title": "سرقت بزرگ بدوارز ۴v4 (Heist of Vice City)",
            "tag": "مسابقه خیابانی",
            "game": "ماینکرفت",
            "date": "جمعه ۲ آذر - ساعت ۲۰:۰۰",
            "prize": "۵۰۰,۰۰۰ تومان وجه نقد در چمدان + رول Kingpin",
            "capacity": 32,
            "registered": 19,
            "status": "active",
            "wanted_level": 5,
            "description": "چهار راند حذفی تا فینال بزرگ. تیم‌های ۴ نفره برای تصاحب منابع الماس و تخریب پایگاه حریفان با گزارش زنده و استریم در دیسکورد."
        },
        {
            "id": "ev-cs2-shootout",
            "title": "جنگ خیابانی ۵v5 کانتر ۲ (Turf War)",
            "tag": "نبرد تیمی",
            "game": "CS2",
            "date": "پنج‌شنبه ۸ آذر - ساعت ۲۱:۰۰",
            "prize": "۱,۰۰۰,۰۰۰ تومان نقد برای تیم برنده",
            "capacity": 16,
            "registered": 12,
            "status": "active",
            "wanted_level": 5,
            "description": "ثبت‌نام کاپ تیم‌های مسلح وایس‌سیتی بر سر قلمرو با سرور اختصاصی پینگ پایین و داوری آنلاین."
        },
        {
            "id": "ev-amongus-night",
            "title": "پارتی شبانه امانگ آس (Among Us Vice Lounge)",
            "tag": "دورهمی شبانه",
            "game": "Among Us",
            "date": "سه‌شنبه ۶ آذر - ساعت ۲۱:۳۰",
            "prize": "گیفت کارت و اشتراک Nitro دیسکورد",
            "capacity": 30,
            "registered": 26,
            "status": "active",
            "wanted_level": 1,
            "description": "پیدا کردن ایمپاسترهای سطح شهر در یک شب‌نشینی صمیمی داخل ویس چت با چالش‌های طنز و بدون استرس."
        }
    ],
    "most_wanted": [
        {
            "rank": "01",
            "name": "Arman_Drifter",
            "bounty": "۲,۴۵۰,۰۰۰ XP",
            "game": "CS2 MVP",
            "status": "تحت تعقیب شدید"
        },
        {
            "rank": "02",
            "name": "ViceVoxel",
            "bounty": "۱,۹۲۰,۰۰۰ XP",
            "game": "Bedwars Champion",
            "status": "خطرناک"
        },
        {
            "rank": "03",
            "name": "Kiarash_Leonida",
            "bounty": "۱,۵۰۰,۰۰۰ XP",
            "game": "Survival King",
            "status": "مسلح"
        }
    ],
    "registrations": [
        {
            "id": "reg-1",
            "event_id": "ev-bedwars-heist",
            "player_name": "آرش",
            "gamertag": "Tommy_Vercetti_IR",
            "discord": "arash_gg#1234",
            "phone": "0912***4567",
            "created_at": "2026-11-24 12:30"
        },
        {
            "id": "reg-2",
            "event_id": "ev-bedwars-heist",
            "player_name": "سهراب",
            "gamertag": "Lucia_Vice",
            "discord": "sohrab_vx",
            "phone": "0935***8899",
            "created_at": "2026-11-24 13:15"
        }
    ]
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_DATA.copy()

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

class RegisterRequest(BaseModel):
    event_id: str
    player_name: str
    gamertag: str
    discord: str
    phone: Optional[str] = ""

class EventCreateRequest(BaseModel):
    title: str
    game: str
    date: str
    prize: str
    capacity: int
    description: str

class BroadcastRequest(BaseModel):
    message: str

class ServerUpdateRequest(BaseModel):
    id: str
    status: str
    players: int
    max_players: int
    ping: str

def verify_admin(admin_key: Optional[str] = Header(None, alias="X-Admin-Key")):
    if admin_key != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="کد عبور افسر ارشد پاتوق نامعتبر است.")
    return True

@app.get("/health")
def health_check():
    return {"status": "ok", "theme": "gta6_vice_city", "app": "PatoghGame", "time": datetime.utcnow().isoformat()}

@app.get("/", response_class=HTMLResponse)
def index_page(request: Request):
    data = load_data()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "broadcast": data.get("broadcast", ""),
            "servers": data.get("servers", []),
            "events": data.get("events", []),
            "most_wanted": data.get("most_wanted", [])
        }
    )

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    data = load_data()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "broadcast": data.get("broadcast", ""),
            "servers": data.get("servers", []),
            "events": data.get("events", []),
            "registrations": data.get("registrations", []),
            "admin_key": ADMIN_SECRET
        }
    )

@app.get("/api/status")
def get_system_status():
    data = load_data()
    total_players = sum(s.get("players", 0) for s in data.get("servers", []))
    total_events = len(data.get("events", []))
    total_registered = len(data.get("registrations", []))
    return {
        "status": "online",
        "city": "Vice City / Leonida",
        "total_players": total_players,
        "total_events": total_events,
        "total_registered": total_registered,
        "servers": data.get("servers", []),
        "broadcast": data.get("broadcast", "")
    }

@app.get("/api/events")
def get_events():
    data = load_data()
    return data.get("events", [])

@app.post("/api/register")
def register_for_event(req: RegisterRequest):
    data = load_data()
    event = next((e for e in data.get("events", []) if e["id"] == req.event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="رویداد شهری مورد نظر یافت نشد.")

    if event.get("registered", 0) >= event.get("capacity", 32):
        raise HTTPException(status_code=400, detail="ظرفیت این مسابقه تکمیل شده است.")

    new_reg = {
        "id": f"reg-{uuid.uuid4().hex[:6]}",
        "event_id": req.event_id,
        "event_title": event.get("title", ""),
        "player_name": req.player_name,
        "gamertag": req.gamertag,
        "discord": req.discord,
        "phone": req.phone,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    event["registered"] = event.get("registered", 0) + 1
    data.setdefault("registrations", []).append(new_reg)
    save_data(data)

    return {
        "success": True,
        "message": f"قرارداد شما برای «{event['title']}» ثبت شد! بیلبوردها و فرکانس دیسکورد را چک کنید.",
        "registration": new_reg
    }

@app.post("/api/admin/broadcast")
def update_broadcast(req: BroadcastRequest, _auth: bool = Depends(verify_admin)):
    data = load_data()
    data["broadcast"] = req.message
    save_data(data)
    return {"success": True, "message": "بیسیم پلیس و تیکر شهری به‌روز شد."}

@app.post("/api/admin/events")
def create_event(req: EventCreateRequest, _auth: bool = Depends(verify_admin)):
    data = load_data()
    new_event = {
        "id": f"ev-{uuid.uuid4().hex[:6]}",
        "title": req.title,
        "tag": "مسابقه خیابانی",
        "game": req.game,
        "date": req.date,
        "prize": req.prize,
        "capacity": req.capacity,
        "registered": 0,
        "status": "active",
        "wanted_level": 4,
        "description": req.description
    }
    data.setdefault("events", []).append(new_event)
    save_data(data)
    return {"success": True, "event": new_event}

@app.delete("/api/admin/events/{event_id}")
def delete_event(event_id: str, _auth: bool = Depends(verify_admin)):
    data = load_data()
    data["events"] = [e for e in data.get("events", []) if e["id"] != event_id]
    save_data(data)
    return {"success": True, "message": "قرارداد رویداد باطل شد."}

@app.post("/api/admin/servers")
def update_server(req: ServerUpdateRequest, _auth: bool = Depends(verify_admin)):
    data = load_data()
    server = next((s for s in data.get("servers", []) if s["id"] == req.id), None)
    if not server:
        raise HTTPException(status_code=404, detail="مکان سرور یافت نشد.")
    server["status"] = req.status
    server["players"] = req.players
    server["max_players"] = req.max_players
    server["ping"] = req.ping
    save_data(data)
    return {"success": True, "server": server}

@app.get("/api/admin/registrations")
def get_all_registrations(_auth: bool = Depends(verify_admin)):
    data = load_data()
    return data.get("registrations", [])
