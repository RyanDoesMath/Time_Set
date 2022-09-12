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

    def test_is_mutually_disjoint(self):
        """Test the is_mutally_disjoint() method."""
        # totally disjoint.
        self.assertTrue(Time_Set([tr1, tr4]).is_mutually_disjoint())
        # share endpoint, but are disjoint.
        self.assertTrue(Time_Set([tr1, tr3]).is_mutually_disjoint())
        # overlapping intervals.
        self.assertFalse(Time_Set([tr1, tr2]).is_mutually_disjoint())
        # nested intervals.
        self.assertFalse(Time_Set([tr4, tr5]).is_mutually_disjoint())
        # nested, but first interval is disjoint with the rest.
        self.assertFalse(Time_Set([tr1, tr4, tr5]).is_mutually_disjoint())

    def test_intersection(self):
        """Tests the intersection computation."""
        # standard intersection.
        self.assertEqual(
            Time_Set([tr1, tr2]).intersection,
            Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 9:00"),
        )
        # no intersection
        self.assertIsNone(Time_Set([tr1, tr3]).intersection)
        # Nested Time Intervals
        self.assertEqual(
            Time_Set([tr5, tr4]).intersection,
            Time_Interval.from_strings("8/1/2022 10:30", "8/1/2022 11:30"),
        )
        # Two layers of mutual nesting.
        self.assertEqual(
            Time_Set([tr4, tr5, tr6]).intersection,
            Time_Interval.from_strings("8/1/2022 10:45", "8/1/2022 11:15"),
        )
        # One layer of nesting with non-disjoint time-intervals inside.
        self.assertEqual(
            Time_Set([tr1, tr2, tr11]).intersection,
            Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 9:00"),
        )
        # One layer of nesting with disjoint time intervals inside.
        self.assertIsNone(Time_Set([tr1, tr3, tr12]).intersection)

    def test_union(self):
        # standard, non-disjoint, non-nested case.
        self.assertEqual(
            Time_Set([tr1, tr2]).union,
            Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 10:00"),
        )
        # disjoint, but share borders, so they union to one time interval.
        self.assertEqual(
            Time_Set([tr1, tr2, tr4]).union,
            Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 12:00"),
        )
        # Time interval equal to tr4 since tr5 is nested.
        self.assertEqual(
            Time_Set([tr4, tr5]).union,
            Time_Interval.from_strings("8/1/2022 10:00", "8/1/2022 12:00"),
        )
        # Totally disjoint, so the result is a time set.
        self.assertEqual(Time_Set([tr1, tr4]).union, Time_Set([tr1, tr4]))
        # One time interval is mutually disjoint with all, but two are not disjoint.
        self.assertEqual(
            Time_Set([tr1, tr2, tr5]).union,
            Time_Set(
                [Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 10:00"), tr5]
            ),
        )

    def test_has_touching_boundaries(self):
        """Tests the has_touching_boundaries() method."""
        # False by definition
        self.assertFalse(Time_Set([]).has_touching_boundaries())
        self.assertFalse(Time_Set([tr1]).has_touching_boundaries())
        # False because intersection is not empty.
        self.assertFalse(Time_Set([tr1, tr2]).has_touching_boundaries())
        # False because disjoint and don't share boundary.
        self.assertFalse(Time_Set([tr1, tr4]).has_touching_boundaries())
        # True because all time intervals have touching boundaries.
        self.assertTrue(Time_Set([tr1, tr13, tr4]).has_touching_boundaries())
        # True because it has one touching boundary.
        self.assertTrue(Time_Set([tr1, tr2, tr4]).has_touching_boundaries())

