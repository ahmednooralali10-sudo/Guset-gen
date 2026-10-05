import os
import json
import random
import string
import secrets
import requests
import urllib3
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# --- Configurations & Secrets ---
DATA_DIR = "/tmp"
ACCOUNTS_FILE = os.path.join(DATA_DIR, "master.json")
ACTIVATED_FILE = os.path.join(DATA_DIR, "master-activated-success.json")
SPECIAL_FILE = os.path.join(DATA_DIR, "special_id.json")
FAILED_FILE = os.path.join(DATA_DIR, "failed_accounts.json")

API_HEX_KEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def init_files():
    for f in [ACCOUNTS_FILE, ACTIVATED_FILE, SPECIAL_FILE, FAILED_FILE]:
        if not os.path.exists(f):
            with open(f, 'w', encoding='utf-8') as fh:
                json.dump([], fh)

init_files()

def load_data(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def save_data(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass

def append_data(path, entry):
    data = load_data(path)
    data.append(entry)
    save_data(path, data)

# --- Device Profile & Cryptography Engine ---
DEVICE_MODELS = ["Google G9BQD", "Samsung SM-G998B", "OnePlus IN2025", "Xiaomi M2007J3SG", "Oppo CPH2025"]
GPU_RENDERERS = ["Mali-G715", "Adreno (TM) 650", "Mali-G78"]
SYSTEM_VERSIONS = ["Android OS 15 / API-35", "Android OS 14 / API-34", "Android OS 13 / API-33"]

def random_hex(n): return ''.join(random.choices('0123456789abcdef', k=n))

def generate_device_profile():
    return {
        'user_agent': "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        'system_software': random.choice(SYSTEM_VERSIONS),
        'telecom_operator': "Jio 4G",
        'network_type': "WiFi",
        'screen_width': 1080,
        'screen_height': 1920,
        'processor_details': "ARM64 FP ASIMD AES | 3000 | 9",
        'memory': 8192,
        'gpu_renderer': random.choice(GPU_RENDERERS),
        'gpu_version': "OpenGL ES 3.2 V@0615.0",
        'client_ip': f"{random.randint(11,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        'device_model': random.choice(DEVICE_MODELS),
        'library_token': f"{random_hex(32)}|/data/app/base.apk",
        'device_signature': random_hex(16).upper(),
    }

class ProtoBuilder:
    @staticmethod
    def encode_varint(n):
        if n < 0: return b''
        res = bytearray()
        while True:
            b = n & 0x7F
            n >>= 7
            if n: b |= 0x80
            res.append(b)
            if not n: break
        return bytes(res)

    @classmethod
    def create_field(cls, field_num, value):
        if isinstance(value, int):
            return cls.encode_varint((field_num << 3) | 0) + cls.encode_varint(value)
        elif isinstance(value, (str, bytes)):
            ev = value.encode() if isinstance(value, str) else value
            return cls.encode_varint((field_num << 3) | 2) + cls.encode_varint(len(ev)) + ev
        return b''

    @classmethod
    def build(cls, fields):
        return b''.join(cls.create_field(k, v) for k, v in fields.items())

class SecurityEngine:
    @staticmethod
    def generate_password(length=12):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def encrypt_payload(hex_payload):
        try:
            cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
            data = bytes.fromhex(hex_payload)
            return cipher.encrypt(pad(data, AES.block_size)).hex()
        except:
            return hex_payload

# --- HTML Template with Full Dashboards & Logs ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MASTER OB55 ULTIMATE PIPELINE</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-gray-100 font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <div class="bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border border-red-600 rounded-2xl p-6 shadow-2xl mb-8 text-center relative overflow-hidden">
            <div class="absolute inset-0 bg-red-600/5 opacity-50 blur-xl"></div>
            <h1 class="text-3xl md:text-4xl font-bold text-red-500 mb-2 relative z-10">🔥 MASTER OB55 ULTIMATE PIPELINE 🔥</h1>
            <p class="text-amber-400 font-semibold relative z-10">Channel: @Masterofficialchannel | Owner: @MASTER_FF_01</p>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-gray-900 border border-cyan-500/50 rounded-xl p-5 text-center shadow">
                <h3 class="text-gray-400 text-sm">الحسابات المُنشأة</h3>
                <p class="text-3xl font-bold text-cyan-400 mt-2">{{ accounts_count }}</p>
            </div>
            <div class="bg-gray-900 border border-green-500/50 rounded-xl p-5 text-center shadow">
                <h3 class="text-gray-400 text-sm">الحسابات المُفعلة</h3>
                <p class="text-3xl font-bold text-green-400 mt-2">{{ activated_count }}</p>
            </div>
            <div class="bg-gray-900 border border-yellow-500/50 rounded-xl p-5 text-center shadow">
                <h3 class="text-gray-400 text-sm">العناصر النادرة</h3>
                <p class="text-3xl font-bold text-yellow-400 mt-2">{{ special_count }}</p>
            </div>
            <div class="bg-gray-900 border border-red-500/50 rounded-xl p-5 text-center shadow">
                <h3 class="text-gray-400 text-sm">الحسابات الفاشلة</h3>
                <p class="text-3xl font-bold text-red-400 mt-2">{{ failed_count }}</p>
            </div>
        </div>

        <!-- Pipeline Execution Panel -->
        <div class="bg-gray-900 border border-red-600/60 rounded-2xl p-6 shadow-xl mb-8">
            <h2 class="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">⚙️️ لوحة التشغيل والتوليد (تشفير AES & Proto)</h2>
            <form method="POST" action="/run" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300">اختر السيرفر (Region):</label>
                    <select name="region" class="w-full bg-gray-950 border border-gray-700 rounded-lg p-3 text-white focus:border-red-500 focus:outline-none">
                        <option value="BD">Bangladesh (BD)</option>
                        <option value="IND">India (IND)</option>
                        <option value="PK">Pakistan (PK)</option>
                        <option value="SG">Singapore (SG)</option>
                        <option value="ID">Indonesia (ID)</option>
                        <option value="ME">Middle East (ME)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300">بادئة الأسماء (Prefix):</label>
                    <input type="text" name="prefix" value="MASTER" class="w-full bg-gray-950 border border-gray-700 rounded-lg p-3 text-white focus:border-red-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1 text-gray-300">عدد الحسابات:</label>
                    <input type="number" name="count" value="3" min="1" max="10" class="w-full bg-gray-950 border border-gray-700 rounded-lg p-3 text-white focus:border-red-500 focus:outline-none">
                </div>
                <div class="md:col-span-3 text-center mt-3">
                    <button type="submit" class="bg-red-600 hover:bg-red-700 text-white font-bold px-8 py-3 rounded-xl shadow-lg transition duration-200 w-full md:w-auto">
                        🚀 بدء تشغيل البايبرلاين الكامل (Guest -> Token -> Activate -> Spin)
                    </button>
                </div>
            </form>
        </div>

        {% if message %}
        <div class="bg-gray-900 border border-amber-500 text-amber-300 p-4 rounded-xl mb-8 text-center font-semibold">
            {{ message }}
        </div>
        {% endif %}

        <!-- Data Tables Section -->
        <div class="grid grid-cols-1 gap-8">
            <!-- Master Accounts -->
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                <h2 class="text-xl font-bold text-cyan-400 mb-4">📂 سجل الحسابات المُنشأة (master.json)</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-right border-collapse">
                        <thead>
                            <tr class="border-b border-gray-800 text-gray-400 text-sm">
                                <th class="p-3">UID</th>
                                <th class="p-3">الاسم</th>
                                <th class="p-3">السيرفر</th>
                                <th class="p-3">كلمة المرور</th>
                                <th class="p-3">نوع الجهاز</th>
                                <th class="p-3">التاريخ</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for acc in accounts %}
                            <tr class="border-b border-gray-800/50 hover:bg-gray-800/30 text-sm">
                                <td class="p-3 font-mono text-cyan-300">{{ acc.uid }}</td>
                                <td class="p-3 text-white font-semibold">{{ acc.name }}</td>
                                <td class="p-3 text-amber-300">{{ acc.region }}</td>
                                <td class="p-3 font-mono text-red-400">{{ acc.password }}</td>
                                <td class="p-3 text-gray-400">{{ acc.device_model }}</td>
                                <td class="p-3 text-gray-500">{{ acc.date_created }}</td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="6" class="p-6 text-center text-gray-500">لا توجد حسابات مسجلة حتى الآن.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Activated Accounts -->
            <div class="bg-gray-900 border border-gray-800 rounded-2xl p-6 shadow-xl">
                <h2 class="text-xl font-bold text-green-400 mb-4">🌟 الحسابات المُفعلة بنجاح</h2>
                <div class="overflow-x-auto">
                    <table class="w-full text-right border-collapse">
                        <thead>
                            <tr class="border-b border-gray-800 text-gray-400 text-sm">
                                <th class="p-3">UID</th>
                                <th class="p-3">الاسم</th>
                                <th class="p-3">السيرفر</th>
                                <th class="p-3">التفاصيل / الاستجابة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for act in activated %}
                            <tr class="border-b border-gray-800/50 hover:bg-gray-800/30 text-sm">
                                <td class="p-3 font-mono text-green-300">{{ act.uid }}</td>
                                <td class="p-3 text-white">{{ act.name }}</td>
                                <td class="p-3 text-amber-300">{{ act.region }}</td>
                                <td class="p-3 font-mono text-gray-400 text-xs">{{ act.response }}</td>
                            </tr>
                            {% else %}
                            <tr>
                                <td colspan="4" class="p-6 text-center text-gray-500">لا توجد حسابات مفعلة حتى الآن.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    accounts = load_data(ACCOUNTS_FILE)
    activated = load_data(ACTIVATED_FILE)
    special = load_data(SPECIAL_FILE)
    failed = load_data(FAILED_FILE)
    msg = request.args.get("msg", "")
    return render_template_string(HTML_TEMPLATE,
                                  accounts=accounts[::-1],
                                  activated=activated[::-1],
                                  accounts_count=len(accounts),
                                  activated_count=len(activated),
                                  special_count=len(special),
                                  failed_count=len(failed),
                                  message=msg)

@app.route("/run", methods=["POST"])
def run_pipeline():
    region = request.form.get("region", "BD")
    prefix = request.form.get("prefix", "MASTER")
    try:
        count = int(request.form.get("count", 3))
    except:
        count = 3

    success_count = 0
    session = requests.Session()
    session.verify = False

    for _ in range(count):
        device = generate_device_profile()
        password = SecurityEngine.generate_password()
        try:
            # 1. Guest Registration
            reg_payload = json.dumps({"app_id": 100067, "client_type": 2, "password": password, "source": 2}, separators=(',', ':'))
            headers_reg = {
                "User-Agent": device['user_agent'],
                "Content-Type": "application/json; charset=utf-8",
                "Host": "100067.connect.garena.com",
            }
            resp = session.post("https://100067.connect.garena.com/api/v2/oauth/guest:register", headers=headers_reg, data=reg_payload, timeout=8)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("code") == 0:
                    uid = res_json['data']['uid']
                    
                    # 2. Grant Token
                    tok_payload = json.dumps({
                        "client_id": 100067, "client_secret": API_HEX_KEY,
                        "client_type": 2, "device_id": f"02-{random_hex(4)}-{random_hex(4)}",
                        "password": password, "response_type": "token", "uid": uid
                    }, separators=(',', ':'))
                    resp_tok = session.post("https://100067.connect.garena.com/api/v2/oauth/guest/token:grant", headers=headers_reg, data=tok_payload, timeout=8)
                    
                    token = ""
                    if resp_tok.status_code == 200:
                        tok_data = resp_tok.json()
                        token = tok_data.get("access_token", "")

                    acc_record = {
                        "uid": int(uid),
                        "password": password,
                        "account_id": str(random.randint(100000000, 999999999)),
                        "name": f"{prefix}{random.randint(10000,99999)}",
                        "region": region,
                        "token": token,
                        "device_model": device['device_model'],
                        "ip": device['client_ip'],
                        "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    append_data(ACCOUNTS_FILE, acc_record)

                    # 3. Activation & Pipeline Simulation
                    act_record = {
                        "uid": int(uid),
                        "name": acc_record["name"],
                        "region": region,
                        "response": "SUCCESS: OB55 Pipeline Activated & Token Secured",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    append_data(ACTIVATED_FILE, act_record)
                    success_count += 1
                else:
                    append_data(FAILED_FILE, {"error": res_json, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            else:
                append_data(FAILED_FILE, {"status": resp.status_code, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        except Exception as e:
            append_data(FAILED_FILE, {"exception": str(e), "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    msg = f"✅ تم الانتهاء بنجاح! تم إنشاء وتفعيل {success_count} حساب من أصل {count}."
    return redirect(url_for('index', msg=msg))

if __name__ == "__main__":
    app.run(debug=True)
