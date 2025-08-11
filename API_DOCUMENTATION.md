# Lolalytics API Documentation

A Python library for scraping League of Legends statistics from lolalytics.com with both async and sync support.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Async Client](#async-client)
  - [Sync Functions](#sync-functions)
  - [Helper Functions](#helper-functions)
  - [Exceptions](#exceptions)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Installation

```bash
pip install lolalytics-api
```

## Quick Start

### Async Usage (Recommended)

```python
import asyncio
from lolalytics_api import LolalyticsClient

async def main():
    async with LolalyticsClient() as client:
        # Get top 5 champions in the tierlist
        tierlist = await client.get_tierlist(5)
        print(tierlist)

asyncio.run(main())
```

### Sync Usage

```python
from lolalytics_api import get_tierlist, get_counters, get_champion_data

# Get top 10 champions for top lane in diamond+
tierlist = get_tierlist(10, lane="top", rank="diamond+")
print(tierlist)
```

## API Reference

### Async Client

#### `LolalyticsClient`

The main async client for interacting with lolalytics.com.

**Constructor Parameters:**
- `base_url` (str, optional): Base URL for lolalytics. Default: "https://lolalytics.com/"
- `session` (aiohttp.ClientSession, optional): Custom aiohttp session
- `request_timeout` (int, optional): Request timeout in seconds. Default: 30
- `headers` (Dict[str, str], optional): Custom HTTP headers

**Usage:**
```python
async with LolalyticsClient() as client:
    # Use client methods here
    pass
```

#### `get_tierlist(n=10, *, lane="", rank="")`

Get the champion tier list.

**Parameters:**
- `n` (int): Number of champions to retrieve (default: 10)
- `lane` (str, optional): Lane filter (see [Lane Values](#lane-values))
- `rank` (str, optional): Rank filter (see [Rank Values](#rank-values))

**Returns:**
```python
List[Dict[str, str]]  # List of champion data
```

**Example Response:**
```python
[
    {
        "rank": "1",
        "champion": "Yasuo",
        "tier": "S+",
        "winrate": "52.3%"
    },
    # ... more champions
]
```

#### `get_counters(*, n=10, champion, rank="")`

Get counters for a specific champion.

**Parameters:**
- `n` (int): Number of counters to retrieve (default: 10)
- `champion` (str): Champion name (required)
- `rank` (str, optional): Rank filter (see [Rank Values](#rank-values))

**Returns:**
```python
List[Dict[str, str]]  # List of counter champions
```

**Example Response:**
```python
[
    {
        "champion": "Malphite",
        "winrate": "58.2"
    },
    # ... more counters
]
```

#### `get_champion_data(*, champion, lane="", rank="")`

Get detailed statistics for a specific champion.

**Parameters:**
- `champion` (str): Champion name (required)
- `lane` (str, optional): Lane filter (see [Lane Values](#lane-values))
- `rank` (str, optional): Rank filter (see [Rank Values](#rank-values))

**Returns:**
```python
Dict[str, str]  # Champion statistics
```

**Example Response:**
```python
{
    "winrate": "52.3%",
    "wr_delta": "+1.2%",
    "game_avg_wr": "51.1%",
    "pickrate": "8.4%",
    "tier": "S",
    "rank": "3",
    "banrate": "12.1%",
    "games": "45,231"
}
```

#### `matchup(*, champion1, champion2, lane="", rank="")`

Get matchup data between two champions.

**Parameters:**
- `champion1` (str): First champion name (required)
- `champion2` (str): Second champion name (required)
- `lane` (str, optional): Lane filter (see [Lane Values](#lane-values))
- `rank` (str, optional): Rank filter (see [Rank Values](#rank-values))

**Returns:**
```python
Dict[str, str]  # Matchup statistics
```

**Example Response:**
```python
{
    "winrate": "47.8",
    "number_of_games": "1,234"
}
```

#### `patch_notes(*, category, rank="")`

Get patch notes data for champions.

**Parameters:**
- `category` (str): Category filter - one of "all", "buffed", "nerfed", "adjusted" (required)
- `rank` (str, optional): Rank filter (see [Rank Values](#rank-values))

**Returns:**
```python
Dict[str, Any]  # Patch notes data
```

**Example Response:**
```python
{
    "buffed": {
        0: {
            "champion": "Yasuo",
            "winrate": "52.3%",
            "pickrate": "8.4%",
            "banrate": "12.1%"
        }
        # ... more champions
    },
    "nerfed": { ... },
    "adjusted": { ... }
}
```

### Sync Functions

Convenience functions that wrap the async client for synchronous usage.

#### `get_tierlist(*args, **kwargs)`

Sync wrapper for [`LolalyticsClient.get_tierlist()`](#get_tierlistn10--lane-rank).

#### `get_counters(*, n=10, champion, rank="")`

Sync wrapper for [`LolalyticsClient.get_counters()`](#get_counters-n10-champion-rank).

#### `get_champion_data(*, champion, lane="", rank="")`

Sync wrapper for [`LolalyticsClient.get_champion_data()`](#get_champion_data-champion-lane-rank).

#### `matchup(*, champion1, champion2, lane="", rank="")`

Sync wrapper for [`LolalyticsClient.matchup()`](#matchup-champion1-champion2-lane-rank).

#### `patch_notes(*, category, rank="")`

Sync wrapper for [`LolalyticsClient.patch_notes()`](#patch_notes-category-rank).

### Helper Functions

#### `display_lanes(display=True)`

Display available lane values and their shortcuts.

**Parameters:**
- `display` (bool): Whether to print the mappings (default: True)

**Returns:**
```python
Dict[str, str]  # Lane mappings
```

#### `display_ranks(display=True)`

Display available rank values and their shortcuts.

**Parameters:**
- `display` (bool): Whether to print the mappings (default: True)

**Returns:**
```python
Dict[str, str]  # Rank mappings
```

### Lane Values

Valid lane values and their shortcuts:

| Input | Mapped Value |
|-------|-------------|
| `"top"` | `"top"` |
| `"jg"`, `"jng"`, `"jungle"` | `"jungle"` |
| `"mid"`, `"middle"` | `"middle"` |
| `"bot"`, `"bottom"`, `"adc"` | `"bottom"` |
| `"support"`, `"supp"`, `"sup"` | `"support"` |

### Rank Values

Valid rank values and their shortcuts:

| Input | Mapped Value |
|-------|-------------|
| `"challenger"`, `"chall"`, `"c"` | `"challenger"` |
| `"grandmaster_plus"`, `"grandmaster+"`, `"gm+"` | `"grandmaster_plus"` |
| `"grandmaster"`, `"grandm"`, `"gm"` | `"grandmaster"` |
| `"master_plus"`, `"master+"`, `"mast+"`, `"m+"` | `"master_plus"` |
| `"master"`, `"mast"`, `"m"` | `"master"` |
| `"diamond_plus"`, `"diamond+"`, `"diam+"`, `"dia+"`, `"d+"` | `"diamond_plus"` |
| `"diamond"`, `"diam"`, `"dia"`, `"d"` | `"diamond"` |
| `"emerald"`, `"eme"`, `"em"`, `"e"` | `"emerald"` |
| `"platinum+"`, `"plat+"`, `"pl+"`, `"p+"` | `"platinum_plus"` |
| `"platinum"`, `"plat"`, `"pl"`, `"p"` | `"platinum"` |
| `"gold_plus"`, `"gold+"`, `"g+"` | `"gold_plus"` |
| `"gold"`, `"g"` | `"gold"` |
| `"silver"`, `"silv"`, `"s"` | `"silver"` |
| `"bronze"`, `"br"`, `"b"` | `"bronze"` |
| `"iron"`, `"i"` | `"iron"` |
| `"unranked"`, `"unrank"`, `"unr"`, `"un"`, `"none"`, `"null"`, `"-"` | `"unranked"` |
| `"all"` | `"all"` |
| `"otp"`, `"1trick"`, `"1-trick"`, `"1trickpony"`, `"onetrickpony"`, `"onetrick"` | `"1trick"` |

### Exceptions

#### `InvalidLane`

Raised when an invalid lane value is provided.

```python
from lolalytics_api.errors import InvalidLane

try:
    await client.get_tierlist(lane="invalid_lane")
except InvalidLane as e:
    print(f"Error: {e}")
    # Error: Invalid lane 'invalid_lane'. See valid lanes with `display_lanes()`.
```

#### `InvalidRank`

Raised when an invalid rank value is provided.

```python
from lolalytics_api.errors import InvalidRank

try:
    await client.get_tierlist(rank="invalid_rank")
except InvalidRank as e:
    print(f"Error: {e}")
    # Error: Invalid rank 'invalid_rank'. See valid ranks with `display_ranks()`.
```

## Examples

### Get Top Lane Tier List

```python
import asyncio
from lolalytics_api import LolalyticsClient

async def get_top_tierlist():
    async with LolalyticsClient() as client:
        tierlist = await client.get_tierlist(10, lane="top", rank="diamond+")
        
        print("Top 10 Top Lane Champions (Diamond+):")
        for champion in tierlist:
            print(f"{champion['rank']}. {champion['champion']} - {champion['tier']} ({champion['winrate']})")

asyncio.run(get_top_tierlist())
```

### Find Champion Counters

```python
import asyncio
from lolalytics_api import LolalyticsClient

async def find_yasuo_counters():
    async with LolalyticsClient() as client:
        counters = await client.get_counters(n=5, champion="yasuo", rank="master+")
        
        print("Top 5 Yasuo Counters (Master+):")
        for counter in counters:
            print(f"{counter['champion']}: {counter['winrate']}% winrate")

asyncio.run(find_yasuo_counters())
```

### Analyze Champion Performance

```python
import asyncio
from lolalytics_api import LolalyticsClient

async def analyze_champion():
    async with LolalyticsClient() as client:
        data = await client.get_champion_data(champion="jax", lane="top", rank="all")
        
        print(f"Jax Top Lane Statistics:")
        print(f"Win Rate: {data['winrate']}")
        print(f"Pick Rate: {data['pickrate']}")
        print(f"Ban Rate: {data['banrate']}")
        print(f"Tier: {data['tier']}")

asyncio.run(analyze_champion())
```

### Compare Matchups

```python
import asyncio
from lolalytics_api import LolalyticsClient

async def compare_matchup():
    async with LolalyticsClient() as client:
        matchup_data = await client.matchup(
            champion1="jax", 
            champion2="fiora", 
            lane="top", 
            rank="diamond+"
        )
        
        print(f"Jax vs Fiora (Top Lane, Diamond+):")
        print(f"Jax Win Rate: {matchup_data['winrate']}%")
        print(f"Games Analyzed: {matchup_data['number_of_games']}")

asyncio.run(compare_matchup())
```

### Check Patch Notes

```python
import asyncio
from lolalytics_api import LolalyticsClient

async def check_patch_changes():
    async with LolalyticsClient() as client:
        patch_data = await client.patch_notes(category="buffed", rank="all")
        
        print("Recently Buffed Champions:")
        for idx, champion_data in patch_data["buffed"].items():
            print(f"{champion_data['champion']}: {champion_data['winrate']} WR, {champion_data['pickrate']} PR")

asyncio.run(check_patch_changes())
```

### Using Sync Functions

```python
from lolalytics_api import get_tierlist, get_counters, display_lanes, display_ranks

# Display available options
display_lanes()
display_ranks()

# Get data synchronously
tierlist = get_tierlist(5, lane="mid", rank="master+")
counters = get_counters(n=3, champion="zed", rank="diamond+")

print("Mid Lane Tier List:", tierlist)
print("Zed Counters:", counters)
```

## Error Handling

The API provides comprehensive error handling:

```python
import asyncio
from lolalytics_api import LolalyticsClient
from lolalytics_api.errors import InvalidLane, InvalidRank

async def safe_api_call():
    async with LolalyticsClient() as client:
        try:
            # This will raise InvalidLane
            await client.get_tierlist(lane="invalid")
        except InvalidLane as e:
            print(f"Lane error: {e}")
        
        try:
            # This will raise InvalidRank
            await client.get_tierlist(rank="invalid")
        except InvalidRank as e:
            print(f"Rank error: {e}")
        
        try:
            # This will raise ValueError
            await client.get_counters(champion="")
        except ValueError as e:
            print(f"Value error: {e}")

asyncio.run(safe_api_call())
```

## Version Information

- **Version**: 0.0.6
- **Author**: xPerSki
- **License**: See LICENSE file