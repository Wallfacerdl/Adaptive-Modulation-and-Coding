import unittest

from models.olla_policy import DNNOllaPolicy, TableLookupOllaConfig, TableLookupOllaPolicy


class StubUser:
    def __init__(self, bler: float, mcs_index: int, max_mcs_index: int = 28):
        self.bler = bler
        self.mcs_index = mcs_index
        self.max_mcs_index = max_mcs_index
        self.transmission_time = 0
        self.update = False

    def apply_mcs_index(self, new_index: int) -> bool:
        bounded = max(0, min(new_index, self.max_mcs_index))
        changed = bounded != self.mcs_index
        delta = bounded - self.mcs_index
        self.mcs_index = bounded
        if delta < 0:
            # 降低MCS后，BLER应显著下降。
            self.bler = max(0.0, self.bler * 0.2)
        elif delta > 0:
            # 提高MCS后，BLER略有上升。
            self.bler = min(1.0, self.bler * 1.2)
        if changed:
            self.update = True
        return changed


class TestTableLookupOllaPolicy(unittest.TestCase):
    def test_low_bler_jumps_to_max(self):
        policy = TableLookupOllaPolicy(TableLookupOllaConfig(bler_target=0.1, max_mcs_index=28))
        user = StubUser(bler=0.005, mcs_index=10)

        policy.optimize(user)

        self.assertEqual(user.mcs_index, 28)
        self.assertTrue(user.update)
        self.assertGreaterEqual(user.transmission_time, 1)

    def test_high_bler_decreases_index(self):
        policy = TableLookupOllaPolicy(TableLookupOllaConfig(bler_target=0.1, max_mcs_index=28))
        user = StubUser(bler=0.35, mcs_index=10)

        policy.optimize(user)

        self.assertEqual(user.mcs_index, 7)
        self.assertTrue(user.update)
        self.assertEqual(user.transmission_time, 1)


class TestDnnOllaPolicy(unittest.TestCase):
    def test_dnn_soft_decrease(self):
        policy = DNNOllaPolicy(bler_target=0.1, soft_cap=0.2)
        user = StubUser(bler=0.25, mcs_index=5)

        policy.optimize(user)

        self.assertEqual(user.mcs_index, 4)
        self.assertTrue(user.update)
        self.assertEqual(user.transmission_time, 1)

    def test_dnn_no_change_when_bler_ok(self):
        policy = DNNOllaPolicy(bler_target=0.1, soft_cap=0.2)
        user = StubUser(bler=0.05, mcs_index=5)

        policy.optimize(user)

        self.assertEqual(user.mcs_index, 5)
        self.assertFalse(user.update)
        self.assertEqual(user.transmission_time, 0)


if __name__ == "__main__":
    unittest.main()
