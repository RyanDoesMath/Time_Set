import unittest
import datetime
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


class Test_Time_Interval(unittest.TestCase):
    def test_init(self):
        """Tests the initializer."""
        # These are okay.
        Time_Interval.from_strings("8/1/2022 0:00", "8/1/2022 1:00")
        Time_Interval(datetime.datetime(2020, 5, 17), datetime.datetime(2022, 5, 17))
        # These are not okay.
        with self.assertRaises(ValueError):
            Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 6:00")
            Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 8:00")

    def test_equals(self):
        """Tests the == operator overriding."""
        self.assertEqual(tr1, tr1)
        self.assertNotEqual(tr1, tr2)

    def test_less_than(self):
        """Tests the < operator overriding."""
        self.assertLess(tr1, tr2)
        self.assertLess(tr4, tr5)

    def test_subtraction(self):
        """Tests the - operator overriding."""
        self.assertEqual(
            tr1 - tr2, Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 8:00")
        )
        self.assertIsNone(tr1 - tr1)
        self.assertEqual(
            tr2 - tr1, Time_Interval.from_strings("8/1/2022 9:00", "8/1/2022 10:00")
        )
        self.assertEqual(tr1 - tr3, tr1)
        # since they are nested, this returns a Time_Set object.
        self.assertEqual(
            tr4 - tr5,
            Time_Set(
                [
                    Time_Interval.from_strings("8/1/2022 10:00", "8/1/2022 10:30"),
                    Time_Interval.from_strings("8/1/2022 11:30", "8/1/2022 12:00"),
                ]
            ),
        )
        # none since tr5 is in tr4
        self.assertIsNone(tr5 - tr4)
        self.assertEqual(
            tr1 - tr10, Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 8:00")
        )
        self.assertEqual(
            tr2 - tr10, Time_Interval.from_strings("8/1/2022 9:00", "8/1/2022 10:00")
        )
        # totally disjoint
        self.assertEqual(tr1 - tr4, tr1)

    def test_is_nested_in(self):
        """Tests the is_nested() method."""
        # totally nested.
        self.assertTrue(tr5.is_nested_in(tr4))
        # nested, but shares right or left borders.
        self.assertTrue(tr10.is_nested_in(tr2))
        self.assertTrue(tr10.is_nested_in(tr1))
        # nested by definition.
        self.assertTrue(tr1.is_nested_in(tr1))

        # not nested in various ways.
        self.assertFalse(tr4.is_nested_in(tr5))
        self.assertFalse(tr1.is_nested_in(tr3))
        self.assertFalse(tr1.is_nested_in(tr2))
        self.assertFalse(tr1.is_nested_in(tr4))

    def test_is_disjoint_with(self):
        """Tests the is_disjoint_with() method."""
        self.assertTrue(tr1.is_disjoint_with(tr4))  # totally disjoint.
        self.assertTrue(tr1.is_disjoint_with(tr3))  # share boundary, but are disjoint.
        self.assertFalse(tr1.is_disjoint_with(tr2))  # not disjoint.
        self.assertFalse(tr5.is_disjoint_with(tr4))  # nested in tr4.
        self.assertFalse(tr4.is_disjoint_with(tr5))  # has tr5 nested in it.

    def test_intersection(self):
        """Tests the intersection method."""
        self.assertEqual(
            tr1.intersection(tr2),
            Time_Interval.from_strings("8/1/2022 8:00", "8/1/2022 9:00"),
        )
        self.assertIsNone(tr1.intersection(tr3))
        self.assertEqual(
            tr4.intersection(tr5),
            Time_Interval.from_strings("8/1/2022 10:30", "8/1/2022 11:30"),
        )
        # reflexive property
        self.assertEqual(tr4.intersection(tr5), tr5.intersection(tr4))
        # intersection of anything with itself is itself.
        self.assertEqual(tr1.intersection(tr1), tr1)

    def test_union(self):
        """Tests the union method."""
        self.assertEqual(
            tr1.union(tr2),
            Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 10:00"),
        )
        self.assertEqual(
            tr1.union(tr3),
            Time_Interval.from_strings("8/1/2022 7:00", "8/1/2022 11:00"),
        )
        # Nested
        self.assertEqual(tr4.union(tr5), tr4)
        # Disjoint, so they form a Time Set
        self.assertEqual(tr1.union(tr4), Time_Set([tr1, tr4]))
