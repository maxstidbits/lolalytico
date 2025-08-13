import asyncio
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urljoin

import aiohttp
from lxml import html

from lolalytico.errors import InvalidLane, InvalidRank


# ---- Public convenience helpers (legacy compatibility) ----
def display_ranks(display: bool = True) -> Dict[str, str]:
    rank_mappings = {
        "": "",
        "challenger": "challenger",
        "chall": "challenger",
        "c": "challenger",
        "grandmaster_plus": "grandmaster_plus",
        "grandmaster+": "grandmaster_plus",
        "gm+": "grandmaster_plus",
        "grandmaster": "grandmaster",
        "grandm": "grandmaster",
        "gm": "grandmaster",
        "master_plus": "master_plus",
        "master+": "master_plus",
        "mast+": "master_plus",
        "m+": "master_plus",
        "master": "master",
        "mast": "master",
        "m": "master",
        "diamond_plus": "diamond_plus",
        "diamond+": "diamond_plus",
        "diam+": "diamond_plus",
        "dia+": "diamond_plus",
        "d+": "diamond_plus",
        "diamond": "diamond",
        "diam": "diamond",
        "dia": "diamond",
        "d": "diamond",
        "emerald": "emerald",
        "eme": "emerald",
        "em": "emerald",
        "e": "emerald",
        "platinum+": "platinum_plus",
        "plat+": "platinum_plus",
        "pl+": "platinum_plus",
        "p+": "platinum_plus",
        "platinum": "platinum",
        "plat": "platinum",
        "pl": "platinum",
        "p": "platinum",
        "gold_plus": "gold_plus",
        "gold+": "gold_plus",
        "g+": "gold_plus",
        "gold": "gold",
        "g": "gold",
        "silver": "silver",
        "silv": "silver",
        "s": "silver",
        "bronze": "bronze",
        "br": "bronze",
        "b": "bronze",
        "iron": "iron",
        "i": "iron",
        "unranked": "unranked",
        "unrank": "unranked",
        "unr": "unranked",
        "un": "unranked",
        "none": "unranked",
        "null": "unranked",
        "-": "unranked",
        "all": "all",
        "otp": "1trick",
        "1trick": "1trick",
        "1-trick": "1trick",
        "1trickpony": "1trick",
        "onetrickpony": "1trick",
        "onetrick": "1trick",
    }
    if display:
        print("Available ranks and their shortcuts:")
        for rank, shortcut in rank_mappings.items():
            print(f"{rank}: {shortcut}")
    return rank_mappings


def display_lanes(display: bool = True) -> Dict[str, str]:
    lane_mappings = {
        "": "",
        "top": "top",
        "jg": "jungle",
        "jng": "jungle",
        "jungle": "jungle",
        "mid": "middle",
        "middle": "middle",
        "bottom": "bottom",
        "bot": "bottom",
        "adc": "bottom",
        "support": "support",
        "supp": "support",
        "sup": "support",
    }
    if display:
        print("Available lanes and their shortcuts:")
        for lane, shortcut in lane_mappings.items():
            print(f"{lane}: {shortcut}")
    return lane_mappings


# ---- Client ----
class LolalyticsClient:
    """Async client for scraping lolalytics.com with a clean, class-based API.

    Notes
    -----
    - Uses `aiohttp` for async HTTP.
    - Returns Python data structures (dicts/lists), not JSON strings.
    - Validates lane/rank via local mappings and raises InvalidLane/InvalidRank.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://lolalytics.com/",
        session: Optional[aiohttp.ClientSession] = None,
        request_timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self._session = session
        self._owns_session = session is None
        self._timeout = aiohttp.ClientTimeout(total=request_timeout)
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0 Safari/537.36"
            )
        }
        if headers:
            self._headers.update(headers)

    async def __aenter__(self) -> "LolalyticsClient":
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self._timeout, headers=self._headers)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._owns_session and self._session:
            await self._session.close()

    # ---- Helpers ----
    @staticmethod
    def _map_rank(rank: str) -> str:
        mapping = display_ranks(display=False)
        try:
            return mapping[rank.lower()]
        except KeyError:
            raise InvalidRank(rank)

    @staticmethod
    def _map_lane(lane: str) -> str:
        mapping = display_lanes(display=False)
        try:
            return mapping[lane.lower()]
        except KeyError:
            raise InvalidLane(lane)

    def _build_url(self, path: str, *, lane: str = "", rank: str = "") -> str:
        params: Dict[str, str] = {}
        if lane:
            params["lane"] = self._map_lane(lane)
        if rank:
            params["tier"] = self._map_rank(rank)
        url = urljoin(self.base_url, path.lstrip("/"))
        if params:
            sep = "&" if ("?" in url) else "?"
            url = f"{url}{sep}{urlencode(params)}"
        return url

    async def _fetch_tree(self, url: str) -> html.HtmlElement:
        assert self._session is not None, "ClientSession not initialized"
        async with self._session.get(url) as resp:
            resp.raise_for_status()
            content = await resp.read()
        return html.fromstring(content)

    # ---- Public API ----
    async def get_tierlist(self, n: int = 10, *, lane: str = "", rank: str = "") -> List[Dict[str, str]]:
        path = "lol/tierlist/"
        url = self._build_url(path, lane=lane, rank=rank)
        tree = await self._fetch_tree(url)

        results: List[Dict[str, str]] = []
        for i in range(3, n + 3):
            rank_xpath = f"/html/body/main/div[6]/div[{i}]/div[1]"
            champion_xpath = f"/html/body/main/div[6]/div[{i}]/div[3]/a"
            tier_xpath = f"/html/body/main/div[6]/div[{i}]/div[4]"
            winrate_xpath = f"/html/body/main/div[6]/div[{i}]/div[6]/div/span[1]"
            # PBI (Pick Ban Influence) appears in the table header as the 8th column.
            # Attempt to extract it; if unavailable, fall back to empty string.
            pbi_xpath = f"/html/body/main/div[6]/div[{i}]/div[8]/div"
            r = tree.xpath(rank_xpath)[0].text_content().strip()
            champion = tree.xpath(champion_xpath)[0].text_content().strip()
            tier = tree.xpath(tier_xpath)[0].text_content().strip()
            winrate = tree.xpath(winrate_xpath)[0].text_content().strip()
            try:
                pbi = tree.xpath(pbi_xpath)[0].text_content().strip()
            except IndexError:
                pbi = ""
            results.append({
                "rank": r,
                "champion": champion,
                "tier": tier,
                "winrate": winrate,
                "pbi": pbi,
            })
        return results

    async def get_counters(self, *, n: int = 10, champion: str, rank: str = "") -> List[Dict[str, str]]:
        if not champion:
            raise ValueError("Champion name cannot be empty")
        champion = champion.lower()
        path = f"lol/{champion}/counters/"
        url = self._build_url(path, rank=rank)
        tree = await self._fetch_tree(url)

        results: List[Dict[str, str]] = []
        for i in range(1, n + 1):
            champion_xpath = f"/html/body/main/div[6]/div[1]/div[2]/span[{i}]/div[1]/a/div/div[1]"
            winrate_xpath = f"/html/body/main/div[6]/div[1]/div[2]/span[{i}]/div[1]/a/div/div[2]/div"
            cname = tree.xpath(champion_xpath)[0].text_content().strip()
            winrate = tree.xpath(winrate_xpath)[0].text_content().strip().split("%")[0]
            results.append({"champion": cname, "winrate": winrate})
        return results

    async def get_champion_data(self, *, champion: str, lane: str = "", rank: str = "") -> Dict[str, str]:
        if not champion:
            raise ValueError("Champion name cannot be empty")
        champion = champion.lower()
        path = f"lol/{champion}/build/"
        url = self._build_url(path, lane=lane, rank=rank)
        tree = await self._fetch_tree(url)
    
        labels = [
            "winrate",
            "wr_delta",
            "game_avg_wr",
            "pickrate",
            "tier",
            "rank",
            "banrate",
            "games",
        ]
        data: Dict[str, str] = {}
        for i in range(1, 9):
            current_xpath = (
                f"/html/body/main/div[5]/div[1]/div[2]/div[2]/div[{(i // 5) + 1}]"
                f"/div[{((i - 1) % 4) + 1}]/div[1]"
            )
            data[labels[i - 1]] = (
                tree.xpath(current_xpath)[0].text_content().strip().split("\n")[0]
            )
    
        # ---- Damage breakdown (Physical / Magic / True / Total) ----
        # Use label-based XPaths to be more resilient to structure changes.
        physical_xpath = "//div[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'physical damage')]/following-sibling::div[1]"
        magic_xpath = "//div[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'magic damage')]/following-sibling::div[1]"
        true_xpath = "//div[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'true damage')]/following-sibling::div[1]"
        total_xpath = "//div[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'total damage')]/following-sibling::div[1]"
    
        def _int_from_xpath(xpath_expr: str) -> int:
            try:
                nodes = tree.xpath(xpath_expr)
                if not nodes:
                    return 0
                node = nodes[0]
                text = node.text_content().strip() if hasattr(node, "text_content") else str(node).strip()
                # Keep digits only from the start (handles "15,708" or "15,708\n18 / 63")
                text = text.split("\n")[0].strip()
                text = text.replace(",", "")
                # Some pages may include non-digit suffixes; take the leading numeric part
                num_str = ""
                for ch in text:
                    if (ch.isdigit() or ch == "."):
                        num_str += ch
                    else:
                        break
                if not num_str:
                    return 0
                # Parse as float then int to be tolerant of decimal formats
                return int(float(num_str))
            except Exception:
                return 0
    
        phys = _int_from_xpath(physical_xpath)
        mag = _int_from_xpath(magic_xpath)
        tru = _int_from_xpath(true_xpath)
        tot = _int_from_xpath(total_xpath) or (phys + mag + tru)
    
        # Compute percentages (rounded to 1 decimal place) and format as strings
        def _pct(part: int, whole: int) -> str:
            try:
                if whole <= 0:
                    return "0%"
                return f"{round(part / whole * 100, 1)}%"
            except Exception:
                return "0%"
    
        damage_info = {
            "physical": str(phys),
            "magic": str(mag),
            "true": str(tru),
            "total": str(tot),
            "physical_pct": _pct(phys, tot),
            "magic_pct": _pct(mag, tot),
            "true_pct": _pct(tru, tot),
        }
    
        data["damage"] = damage_info
        return data

    async def matchup(
        self,
        *,
        champion1: str,
        champion2: str,
        lane: str = "",
        rank: str = "",
    ) -> Dict[str, str]:
        if not champion1 or not champion2:
            raise ValueError("Champion names cannot be empty")
        champion1 = champion1.lower()
        champion2 = champion2.lower()
        path = f"lol/{champion1}/vs/{champion2}/build/"
        url = self._build_url(path, lane=lane, rank=rank)
        tree = await self._fetch_tree(url)

        winrate_xpath = "/html/body/main/div[5]/div[1]/div[2]/div[3]/div/div/div[1]/div[1]"
        nof_games_xpath = "/html/body/main/div[5]/div[1]/div[2]/div[3]/div/div/div[2]/div[1]"
        winrate = tree.xpath(winrate_xpath)[0].text_content().strip().split("%")[0]
        nof_games = tree.xpath(nof_games_xpath)[0].text_content().strip()
        return {"winrate": winrate, "number_of_games": nof_games}

    async def patch_notes(self, *, category: str, rank: str = "") -> Dict[str, Any]:
        if category not in {"all", "buffed", "nerfed", "adjusted"}:
            raise ValueError("category must be one of 'all', 'buffed', 'nerfed', 'adjusted'")

        path = ""
        url = self._build_url(path, rank=rank)
        tree = await self._fetch_tree(url)

        if category == "all":
            result: Dict[str, Any] = {"buffed": {}, "nerfed": {}, "adjusted": {}}
            cats = ("buffed", "nerfed", "adjusted")
        else:
            result = {category: {}}
            cats = (category,)

        def _parse(cat: str) -> None:
            mapping = {"buffed": 1, "nerfed": 2, "adjusted": 3}
            idx = mapping[cat]
            i = 0
            while True:
                i += 1
                base = f"/html/body/main/div[5]/div[4]/div[{idx}]/div/div[{i}]"
                try:
                    champion_name_xpath = f"{base}/div/div[1]/span[1]/a"
                    winrate_xpath = f"{base}/div/div[2]/span"
                    pickrate_xpath = f"{base}/div/div[3]/span[1]"
                    banrate_xpath = f"{base}/div/div[3]/span[2]"
                    result[cat][i - 1] = {
                        "champion": tree.xpath(champion_name_xpath)[0].text_content().strip(),
                        "winrate": tree.xpath(winrate_xpath)[0].text_content().strip(),
                        "pickrate": tree.xpath(pickrate_xpath)[0].text_content().strip(),
                        "banrate": tree.xpath(banrate_xpath)[0].text_content().strip(),
                    }
                except IndexError:
                    break

        for c in cats:
            _parse(c)
        return result


# Optional: simple sync wrappers for convenience
def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def get_event_loop_safe():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def tierlist(*args, **kwargs):
    async def _inner():
        async with LolalyticsClient() as client:
            return await client.get_tierlist(*args, **kwargs)
    return _run(_inner())


def counters(*, n: int = 10, champion: str, rank: str = ""):
    async def _inner():
        async with LolalyticsClient() as client:
            return await client.get_counters(n=n, champion=champion, rank=rank)
    return _run(_inner())


def champion_data(*, champion: str, lane: str = "", rank: str = ""):
    async def _inner():
        async with LolalyticsClient() as client:
            return await client.get_champion_data(champion=champion, lane=lane, rank=rank)
    return _run(_inner())


def matchup(*, champion1: str, champion2: str, lane: str = "", rank: str = ""):
    async def _inner():
        async with LolalyticsClient() as client:
            return await client.matchup(champion1=champion1, champion2=champion2, lane=lane, rank=rank)
    return _run(_inner())


def patch(*, category: str, rank: str = ""):
    async def _inner():
        async with LolalyticsClient() as client:
            return await client.patch_notes(category=category, rank=rank)
    return _run(_inner())
