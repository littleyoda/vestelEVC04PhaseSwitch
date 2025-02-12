import argparse
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


def saveLogFile(page):
        with open('phaseswitch.log', 'w') as writer:
            writer.write(page)

def getPhasenWWW(parsedPage, page):
    phaseSelector = parsedPage.select(
        'select#currentLimiterPhaseSelection>option[selected="selected"]'
    )

    for elm in phaseSelector:
        if elm["id"] == "currentLimiterOnePhase":
            return 1
        elif elm["id"] == "currentLimiterThreePhase":
            return 3

    try:
        with open('phaseswitch.log', 'w') as writer:
            writer.write(f"Selected-Options: {[elm["id"] for elm in phaseSelector]}\n")
            options = parsedPage.select(
             'select#currentLimiterPhaseSelection>option'
            )
            writer.write(f'Options: {[elm["id"] for elm in options]}\n')

            writer.write(page)
    except Exception:
        pass

    raise RuntimeError(f"Unknown Phase. Logfile phaseswitch.log created! Length: {len(phaseSelector)} Elements: {[elm["id"] for elm in phaseSelector]}")


async def login(ip, user, pwd, nrOfPhases, current):
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
            page = await response.text()

            # Get Nr of used Phases
            parsedPage = BeautifulSoup(page, "html.parser")


            urlCheck = str(response.url).endswith("/index_main.php")
            inputCheck = len(parsedPage.select('input[name="username"]'))

            if not urlCheck or inputCheck > 0:
                await session.close()
                saveLogFile(page)
                raise RuntimeError(f"Login failed! [{response.url},{inputCheck}]")


            print("Used Phases: ", getPhasenWWW(parsedPage, page))
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
                    "currentLimiterValue": current,
                    "button_current_limiter_settings": "Daten+absenden",
                },
            ) as response:
                page = await response.text()
                parsedPage = BeautifulSoup(page, "html.parser")
                print("Changed to: ", getPhasenWWW(parsedPage, page))
            await session.close()

def run(ip, user, password, phases, current):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(login(ip, user, password, phases,current))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip")
    parser.add_argument("user")
    parser.add_argument("password")
    parser.add_argument('phases', nargs='?', default=None)
    parser.add_argument('current', nargs='?', default=32)
    args = parser.parse_args()
    run(args.ip, args.user, args.password, args.phases, args.current)