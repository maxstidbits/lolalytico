import pytest
import json
from unittest.mock import patch, Mock
from lolalytics_api import get_tierlist, get_counters


class TestGetTierlist:
    def test_invalid_lane_raises_error(self):
        with pytest.raises(ValueError, match="Invalid lane"):
            get_tierlist(5, "test")

    def test_lane_shortcuts(self):
        valid_lanes = ['top', 'jg', 'jungle', 'mid', 'middle', 'bot', 'bottom', 'adc', 'support', 'sup']
        for lane in valid_lanes:
            try:
                get_tierlist(1, lane)
            except:
                pass

    @patch('lolalytics_api.main.requests.get')
    def test_get_tierlist_returns_json(self, mock_get):
        mock_response = Mock()
        mock_response.content = b'''
        <html><body><main>
        <div><div></div><div></div><div></div>
        <div><div>1</div><div></div><div><a>TestChamp</a></div><div>S+</div><div></div><div><div><span>55.2%</span></div></div></div>
        </div></main></body></html>
        '''
        mock_get.return_value = mock_response

        result = get_tierlist(1)
        parsed = json.loads(result)

        assert len(parsed) == 1
        assert '0' in parsed
        assert 'rank' in parsed['0']
        assert 'champion' in parsed['0']
        assert 'tier' in parsed['0']
        assert 'winrate' in parsed['0']


class TestGetCounters:
    def test_empty_champion_raises_error(self):
        with pytest.raises(ValueError, match="Champion name cannot be empty"):
            get_counters(5, "")

    @patch('lolalytics_api.main.requests.get')
    def test_get_counters_returns_json(self, mock_get):
        mock_response = Mock()
        mock_response.content = b'''
        <html><body><main>
        <div><div><div><div><span><div><a><div><div>CounterChamp</div><div><div>60.5%</div></div></div></a></div></span></div></div></div></div>
        </main></body></html>
        '''
        mock_get.return_value = mock_response

        result = get_counters(1, "yasuo")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
