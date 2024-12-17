import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


def getPhasenWWW(parsedPage):
    for elm in parsedPage.select(
        'select#currentLimiterPhaseSelection>option[selected="selected"]'
    ):
        if elm["id"] == "currentLimiterOnePhase":
            return 1
        elif elm["id"] == "currentLimiterThreePhase":
            return 3
    raise RuntimeError("Unknown Phase")

async def login(ip, user, pwd, nrOfPhases):
        jar = aiohttp.CookieJar(unsafe=True)
        session = aiohttp.ClientSession(cookie_jar=jar)
        # get Session-Cookie
        async with session.get("http://" + ip) as response:
            data = await response.text()
            headers = response.headers

#        filtered = session.cookie_jar.filter_cookies("http://" + ip)

        # Login
        async with session.post(
            "http://" + ip + "/",
            data={
                "username": user,
                "pass": pwd,
                "button_login": "LOG+IN",
            },
        ) as response:
            loggedIn = str(response.url).endswith("/index_main.php")
            if not loggedIn:
                await session.close()
                raise RuntimeError("Login not possible")
            page = await response.text()

            # Get Nr of used Phases
            parsedPage = BeautifulSoup(page, "html.parser")
            print("Used Phases: ", getPhasenWWW(parsedPage))
            if nrOfPhases == None:
                await session.close()
                return
            value = None
            if nrOfPhases == "1":
                value = 0
            elif nrOfPhases == "3":
                value = 1
            else:
                _LOGGER.info(f"Number of Phases illegal {nrOfPhases}")
                raise RuntimeError("Unknown Phase")
            async with session.post(
                "http://" + ip + "/index_main.php",
                data={
                    "currentLimiterPhaseSelection": value,
                    "currentLimiterValue": 32,
                    "button_current_limiter_settings": "Daten+absenden",
                },
            ) as response:
                page = await response.text()
                parsedPage = BeautifulSoup(page, "html.parser")
                print("Changed to: ", getPhasenWWW(parsedPage))
            await session.close()

def run(ip, user, password, phases):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(login(ip, user, password, phases))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip")
    parser.add_argument("user")
    parser.add_argument("password")
    parser.add_argument('phases', nargs='?', default=None)
    args = parser.parse_args()
    print(args.phases)
    run(args.ip, args.user, args.password, args.phases)