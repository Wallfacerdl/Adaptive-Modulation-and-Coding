import unittest
from unittest.mock import patch

from config.strategy import LinkAdaptationStrategy
from models.link_adaptation import LinkAdaptation


class StubUser:
    def __init__(self, cqi: int = 10, snr: float = 15.0):
        self.cqi = cqi
        self.snr = snr


class TestLinkAdaptationIntegration(unittest.TestCase):
    def test_table_lookup_returns_valid_mcs_mapping(self):
        la = LinkAdaptation(strategy=LinkAdaptationStrategy.TABLE_LOOKUP)
        user = StubUser(cqi=10)

        mcs = la.select_mcs(user)

        self.assertIn("index", mcs)
        self.assertIn("modulation", mcs)
        self.assertGreaterEqual(mcs["index"], 0)

    def test_dnn_strategy_uses_selector_output(self):
        with patch("models.link_adaptation.DNNSelectionStrategy") as mock_dnn_cls:
            mock_instance = mock_dnn_cls.return_value
            mock_instance.select_index.return_value = 7

            la = LinkAdaptation(strategy=LinkAdaptationStrategy.DNN)
            user = StubUser(snr=12.3)
            mcs = la.select_mcs(user)

            self.assertEqual(mcs["index"], 7)
            mock_instance.select_index.assert_called_once_with(user)


if __name__ == "__main__":
    unittest.main()
