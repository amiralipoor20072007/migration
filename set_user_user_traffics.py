# Module Imports
import mariadb
from httpx import AsyncClient
import sys
from json import loads as jloads
import asyncio
from time import time
pannel_addr = "https://marz.irankalaalireza.site:2083"         #   "http://{addr}:port/"
pannel_user = "Mahdi"
pannel_pass = "Mahdi651389@"
PANEL_ADDR = pannel_addr
PANEL_USER = pannel_user
PANEL_PASS = pannel_pass
TIME_GET_TOKEN = 0
PANEL_HEADERS = {}

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="db_user",
        password="db_user_passwd",
        host="192.0.2.1",
        port=3306,
        database="employees")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

async def get_panel_token(PANEL_USER, PANEL_PASS, PANEL_DOMAIN) :
    global TIME_GET_TOKEN
    global PANEL_HEADERS
    if (time() - TIME_GET_TOKEN)  > 60:
        PANEL_TOKEN_DATA = {"username" : PANEL_USER , "password" : PANEL_PASS }
        async with AsyncClient(verify=False,timeout=30) as client:
            PANEL_TOKEN = await client.post(url=f"{PANEL_DOMAIN}/api/admin/token",
                                            data=PANEL_TOKEN_DATA)
            if PANEL_TOKEN.status_code == 200 :
                PANEL_TOKEN_BACK = jloads(PANEL_TOKEN.text)
                PANEL_HEADERS = {
                            'accept': 'application/json',
                            'Content-Type': 'application/json',
                            'Authorization': f"Bearer {PANEL_TOKEN_BACK.get('access_token')}"}
                TIME_GET_TOKEN = time()
                return PANEL_HEADERS
            else :
                return False
    else:
        return PANEL_HEADERS

async def get_all_email():
    PANEL_TOKEN = await get_panel_token(PANEL_USER, PANEL_PASS, PANEL_ADDR)
    URL = f"{PANEL_ADDR}/api/users"
    async with AsyncClient(verify=False,timeout=30) as client:
        RESPONCE = await client.get(url=URL,headers=PANEL_TOKEN)
        if RESPONCE.status_code == 200 :
            RESPONCE_DATA = RESPONCE.json()
            return RESPONCE_DATA.get('users', [])
        else :
            return "Can Not Login To Panel"

users = asyncio.run(get_all_email())
for user in users:
    try:
        cur.execute(f"UPDATE `marzneshin`.`users` SET `used_traffic`={user['used_traffic']} WHERE  `username`='{user['username']}';")
    except mariadb.Error as e:
        print(f"Error: {e}")