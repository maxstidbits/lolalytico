import json
import pytest

from lolalytico.main import LolalyticsClient, display_lanes, display_ranks
from lolalytico.errors import InvalidLane, InvalidRank

pytestmark = pytest.mark.asyncio


def _check_labels(data, labels):
    for label in labels:
        assert label in data, f"Missing label: {label}"


class TestGetTierlist:
    async def test_invalid_lane_raises_error(self):
        async with LolalyticsClient() as client:
            with pytest.raises(InvalidLane):
                await client.get_tierlist(5, lane="test", rank="gm+")

    async def test_invalid_rank_raises_error(self):
        async with LolalyticsClient() as client:
            with pytest.raises(InvalidRank):
                await client.get_tierlist(5, lane="top", rank="test")

    async def test_lane_shortcuts(self):
        valid_lanes = [
            "top",
            "jg",
            "jng",
            "jungle",
            "mid",
            "middle",
            "bot",
            "bottom",
            "adc",
            "support",
            "supp",
            "sup",
        ]
        async with LolalyticsClient() as client:
            for lane in valid_lanes:
                try:
                    await client.get_tierlist(1, lane=lane)
                except InvalidLane:
                    pytest.fail(f"Valid lane '{lane}' raised InvalidLane error")

    async def test_get_tierlist_returns_sequence(self):
        async with LolalyticsClient() as client:
            result = await client.get_tierlist(1)
        assert isinstance(result, list)
        assert len(result) == 1
        labels = ["rank", "champion", "tier", "winrate", "pbi"]
        _check_labels(result[0], labels)

    async def test_pbi_field_present_and_string(self):
        async with LolalyticsClient() as client:
            result = await client.get_tierlist(1)
        assert "pbi" in result[0]
        assert isinstance(result[0]["pbi"], str)


class TestGetCounters:
    async def test_empty_champion_raises_error(self):
        async with LolalyticsClient() as client:
            with pytest.raises(ValueError, match="Champion name cannot be empty"):
                await client.get_counters(n=5, champion="")

    async def test_get_counters_returns_sequence(self):
        async with LolalyticsClient() as client:
            result = await client.get_counters(n=1, champion="yasuo")
        assert isinstance(result, list)
        assert len(result) == 1
        labels = ["champion", "winrate"]
        _check_labels(result[0], labels)


class TestChampionData:
    async def test_champion_data(self):
        async with LolalyticsClient() as client:
            data = await client.get_champion_data(champion="jax", lane="top", rank="d+")
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
        _check_labels(data, labels)

    async def test_matchup(self):
        async with LolalyticsClient() as client:
            data = await client.matchup(champion1="jax", champion2="vayne", lane="top", rank="master")
        labels = ["winrate", "number_of_games"]
        _check_labels(data, labels)

    async def test_patch_notes(self):
        async with LolalyticsClient() as client:
            data = await client.patch_notes(category="all", rank="g+")
        labels = ["buffed", "nerfed", "adjusted"]
        _check_labels(data, labels)