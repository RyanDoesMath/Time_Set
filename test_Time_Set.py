import unittest
from Time_Set import Time_Set
from Time_Set import Time_Interval

# Sample time ranges to test with.
tr1 = Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 9:00")
tr2 = Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 10:00")
tr3 = Time_Interval.from_strings("8/1/2022 9:00", "8/1/2022 11:00")
tr4 = Time_Interval.from_strings("8/1/2022 10:00", "8/1/2022 12:00")
tr5 = Time_Interval.from_strings("8/1/2022 10:30", "8/1/2022 11:30")
tr6 = Time_Interval.from_strings("8/1/2022 10:45", "8/1/2022 11:15")
tr7 = Time_Interval.from_strings("8/1/2022 10:15", "8/1/2022 10:45")
tr8 = Time_Interval.from_strings("8/1/2022 11:15", "8/1/2022 11:45")
tr9 = Time_Interval.from_strings("8/1/2022 11:30", "8/1/2022 13:00")
tr10 = Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 9:00")
tr11 = Time_Interval.from_strings("8/1/2022 6:00", "8/1/2022 11:00")
tr12 = Time_Interval.from_strings("8/1/2022 6:00", "8/1/2022 12:00")
tr13 = Time_Interval.from_strings("8/1/2022 9:00", "8/1/2022 10:00")


class Test_Time_Set(unittest.TestCase):
    def test_init_good_inputs(self):
        """Tests the constructor with valid inputs."""
        Time_Set([])
        Time_Set([tr1])
        Time_Set([tr1, tr2])

    def test_init_bad_inputs(self):
        """Tests the constructor with bad inputs. Should raise exception."""
        with self.assertRaises(TypeError):
            Time_Set([tr1, tr2, "not a time interval", tr4])
            Time_Set([tr1, 3, tr5])
            Time_Set([None, tr8])

    def test_equals(self):
        """Tests the == overriding."""
        Time_Set_1 = Time_Set([tr1, tr2])
        Time_Set_2 = Time_Set([tr1, tr2])
        Time_Set_3 = Time_Set([tr1, tr3])
        self.assertEqual(Time_Set_1, Time_Set_2)
        self.assertNotEqual(Time_Set_1, Time_Set_3)

    def test_compute_intersection(self):
        """Tests the compute_intersection() method."""
        # standard compute_intersection().
        self.assertEqual(
            Time_Set([tr1, tr2]).compute_intersection(),
            Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 9:00"),
        )
        # no compute_intersection()
        self.assertIsNone(Time_Set([tr1, tr3]).compute_intersection())
        # Nested Time Intervals
        self.assertEqual(
            Time_Set([tr5, tr4]).compute_intersection(),
            Time_Interval.from_strings("8/1/2022 10:30", "8/1/2022 11:30"),
        )
        # Two layers of mutual nesting.
        self.assertEqual(
            Time_Set([tr4, tr5, tr6]).compute_intersection(),
            Time_Interval.from_strings("8/1/2022 10:45", "8/1/2022 11:15"),
        )
        # One layer of nesting with non-disjoint time-intervals inside.
        self.assertEqual(
            Time_Set([tr1, tr2, tr11]).compute_intersection(),
            Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 9:00"),
        )
        # One layer of nesting with disjoint time intervals inside.
        self.assertIsNone(Time_Set([tr1, tr3, tr12]).compute_intersection())

    def test_compute_union(self):
        """Tests the compute_union() method."""
        # standard, non-disjoint, non-nested case.
        self.assertEqual(
            Time_Set([tr1, tr2]).compute_union(),
            Time_Set([Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 10:00")]),
        )
        # disjoint, but share borders, so they compute_union() to one time interval.
        self.assertEqual(
            Time_Set([tr1, tr2, tr4]).compute_union(),
            Time_Set([Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 12:00")]),
        )
        # Time interval equal to tr4 since tr5 is nested.
        self.assertEqual(
            Time_Set([tr4, tr5]).compute_union(),
            Time_Set([Time_Interval.from_strings("8/1/2022 10:00", "8/1/2022 12:00")]),
        )
        # Totally disjoint, so the result is a time set.
        self.assertEqual(Time_Set([tr1, tr4]).compute_union(), Time_Set([tr1, tr4]))
        # One time interval is mutually disjoint with all, but two are not disjoint.
        self.assertEqual(
            Time_Set([tr1, tr2, tr5]).compute_union(),
            Time_Set(
                [Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 10:00"), tr5]
            ),
        )
