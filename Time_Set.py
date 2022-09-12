from datetime import datetime
import pandas as pd


class Time_Set:
    """A collection of zero or more time intervals."""

    def __init__(self, time_intervals: list):
        """Constructs a Time_Set from Time_Interval objects."""
        self.validate_list_of_time_intervals(time_intervals)

        self.time_intervals = sorted(time_intervals)
        self.intersection = self.compute_intersection()
        self.union = self.compute_union()

    @classmethod
    def from_dataframe(cls, dataframe: pd.core.frame.DataFrame):
        """Constructs a Time_Set from a pandas dataframe."""
        pass

    def __eq__(self, other):
        """Determines if this Time_Set is equal to another."""
        return True if self.time_intervals == other.time_intervals else False

    def __str__(self):
        """Returns a string representation of a Time_Set."""
        ret_str = "-" * 71 + "\n"
        for ix, interval in enumerate(self.time_intervals):
            ret_str += "Time Interval " + str(ix) + " - " + str(interval) + "\n"
        ret_str += "-" * 71
        return ret_str

    def append(self, time_interval):
        """Appends a time interval(s) to the Time_Set."""
        if isinstance(time_interval, list):
            return Time_Set(self.time_intervals + time_interval)
        elif isinstance(time_interval, Time_Interval):
            temp = self.time_intervals
            temp.append(time_interval)
            return Time_Set(temp)

    def validate_list_of_time_intervals(self, time_intervals: list):
        """Returns true if the passed list is all of type Time_Interval."""
        for time_interval in time_intervals:
            if not isinstance(time_interval, Time_Interval):
                raise TypeError(
                    str(type(time_interval))
                    + " type found in the passed list is not of type Time_Interval."
                )

    def compute_intersection(self):
        """Sets the intersection of this Time_Set."""
        if len(self.time_intervals) == 0:
            return None

        intersection = self.time_intervals[0]
        for i in self.time_intervals:
            intersection = intersection.intersection(i)
            if intersection is None:
                return None
        return intersection

    def compute_union(self):
        """Sets the union of this Time_Set."""
        if self.is_mutually_disjoint() and not self.has_touching_boundaries():
            return self.time_intervals

        union = self.time_intervals.copy()
        for ix, i in enumerate(union[1:]):
            if (
                not union[0].is_disjoint_with(i)
                or (union[0].end == i.start)
                or (i.end == union[0].start)
            ):
                earliest_start = min(union[0].start, i.start)
                latest_end = max(union[0].end, i.end)
                union = list(
                    union[1 : ix + 1]
                    + union[ix + 2 :]
                    + [Time_Interval(earliest_start, latest_end)]
                ).copy()
            union = union[1:] + [union[0]]
        union = Time_Set(union)
        return union.union

    def has_touching_boundaries(self):
        """Determines if the set has intervals that share boundaries, but don't overlap.
        
        This is mainly a helper method for compute_union.
        """
        for ix, i in enumerate(self.time_intervals):
            for j in self.time_intervals[0:ix] + self.time_intervals[ix + 1 :]:
                if i.start == j.end or j.start == i.end:
                    return True
        return False

    def is_mutually_disjoint(self) -> bool:
        """Tells if the Time_Intervals in this Time_Set are mutually disjoint."""
        for ix, i in enumerate(self.time_intervals):
            for j in self.time_intervals[ix + 1 :]:
                if not i.is_disjoint_with(j):
                    return False
        return True


class Time_Interval:
    """A class that models time intervals.
    
    Time intervals are interval sets of time, meaning they include all set operations.
    Time intervals are clopen, with the left side being closed (included) and the right side
    being open (excluded). This was chosen because it is what we colloquially mean when
    we reference time intervals. For example: from eight to nine means the 60 minutes from
    8:00 to 8:59, but not the next minute (from 9:00 to 9:01). Thus the intervals are clopen.
    """

    def __init__(self, start: str, end: str):
        """Creates a time interval from datetime objects.
        
        Parameters:
            start : datetime.datetime - start time.
            end : datetime.datetime - end time.
        """
        if start > end:
            raise ValueError("End time is before start time.")
        if start == end:
            raise ValueError("End time is equal to start time.")

        self.start = start
        self.end = end
        self.time_elapsed = end - start

    @classmethod
    def from_strings(cls, start: str, end: str, time_format: str = "%m/%d/%Y %H:%M"):
        """Creates a time interval from strings
        
        Parameters:
            start : str - start time in a time_format for datetime.strptime to parse.
            end : str - end time in a time_format for datetime.strptime to parse.
            time_format : str - the time format for datetime.strptime to parse.
        """
        start_time = datetime.strptime(start, time_format)
        end_time = datetime.strptime(end, time_format)

        return cls(start_time, end_time)

    def __str__(self):
        """Returns a string representation of the time interval."""
        return "Start: " + str(self.start) + " | End: " + str(self.end)

    def __eq__(self, other):
        """Returns if the Time_Intervals start and stop at the same time."""
        return self.start == other.start and self.end == other.end

    def __lt__(self, other):
        """A Time_Interval is less than another if its start is earlier."""
        self.start < other.start

    def __sub__(self, other):
        """Returns the set difference between this time interval and the other.
        
        This method only determines if the two time intervals are nested, not
        nested, or disjoint and offloads the logic of computing the set difference 
        to two other methods: subtract_nested_time_intervals() and 
        subtract_non_nested_time_intervals().
        """
        if other.is_nested(self):
            return self.subtract_nested_time_intervals(other)
        elif self.is_disjoint_with(other):
            return self
        else:
            return self.subtract_non_nested_time_intervals(other)

    def subtract_nested_time_intervals(self, other):
        """A helper function for __sub__() that deals only with the nested case.
        
        Since subtracting a nested time interval from another would result in
        two time intervals, this case will return a Time_Set object.
        """
        earliest_start, earliest_end = (
            min(self.start, other.start),
            min(self.end, other.end),
        )
        latest_start, latest_end = (
            max(self.start, other.start),
            max(self.end, other.end),
        )

        try:
            left_time_interval = Time_Interval(earliest_start, latest_start)
        except:
            left_time_interval = None
        try:
            right_time_interval = Time_Interval(earliest_end, latest_end)
        except:
            right_time_interval = None

        if left_time_interval is None and right_time_interval is None:
            return None
        if left_time_interval is None:
            return right_time_interval
        if right_time_interval is None:
            return left_time_interval
        return Time_Set([left_time_interval, right_time_interval])

    def subtract_non_nested_time_intervals(self, other):
        """A helper function for __sub__ that deals only with the non-nested, non-disjoint case."""
        if self == other:
            return None
        if other.start > self.start:
            return Time_Interval(self.start, other.start)
        if other.end < self.end:
            return Time_Interval(other.end, self.end)

    def intersection(self, other):
        """Returns the intersection of this Time_Interval and another.
        
        The intersection can only ever be a single time interval, or none.
        """
        if other.is_nested(self):
            return other
        elif self.is_nested(other):
            return self
        else:
            return self - (self - other)

    def union(self, other):
        """Returns the intersection of this Time_Interval and another.
        
        Because a union of disjoint time intervals is a list of two time
        intervals, this function returns a Time_Set object for the disjoint
        case.
        """
        earliest_start = min(self.start, other.start)
        latest_end = max(self.end, other.end)
        if self.start == other.end or other.start == self.end:
            return Time_Interval(earliest_start, latest_end)
        if self.is_disjoint_with(other):
            return Time_Set([self, other])
        return Time_Interval(earliest_start, latest_end)

    def is_disjoint_with(self, other) -> bool:
        """Returns True if this time interval is disjoint with the other.
        
        Note that, since time intervals are closed on the left side and
        open on the right side, time intervals that share a start or end
        (ie: 8:00 to 9:00 and 9:00 to 10:00) will be disjoint.
        """
        if self.start < other.start and self.end <= other.start:
            return True
        if other.start < self.start and other.end <= self.start:
            return True
        return False

    def is_nested(self, other) -> bool:
        """Returns True if this time interval is inside the other."""
        if self.start >= other.start and self.end <= other.end:
            return True
        else:
            return False
