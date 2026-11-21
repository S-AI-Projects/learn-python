"""Multiple Inheritance

@see: https://docs.python.org/3/tutorial/classes.html#multiple-inheritance

Some classes may derive from multiple classes. This means that the derived class would have
its attributes, along with the attributes of all the classes that it was derived from.

Worked Example & Decisive MRO Dispatch:
---------------------------------------
In a multiple-inheritance hierarchy such as `class CalendarClock(Clock, Calendar)`:
1. Dispatch Order: Python constructs the Method Resolution Order (C3 Linearization):
   `CalendarClock -> Clock -> Calendar -> object`.
2. Decisive State Transition:
   - Calling `get_time()`: lookup checks `CalendarClock` (absent), advances to `Clock` (found),
     binding `Clock.get_time` and returning `Clock.time` ('11:23 PM').
   - Calling `get_date()`: lookup checks `CalendarClock` (absent), checks `Clock` (absent),
     advances along the MRO to `Calendar` (found), returning `Calendar.date` ('12/08/2018').
3. Neighboring Input:
   - Overriding instance attributes (`time = '11:24 PM'`, `date = '12/09/2018'`) dynamically
     resolves through the same dispatch pathway to the new values.
"""


def test_multiple_inheritance():
    """Multiple Inheritance"""

    # pylint: disable=too-few-public-methods
    class Clock:
        """Clock class"""

        time = '11:23 PM'

        def get_time(self):
            """Get current time

            Method is hardcoded just for multiple inheritance illustration.
            """
            return self.time

    # pylint: disable=too-few-public-methods
    class Calendar:
        """Calendar class"""

        date = '12/08/2018'

        def get_date(self):
            """Get current date

            Method is hardcoded just for multiple inheritance illustration.
            """
            return self.date

    # Python supports a form of multiple inheritance as well. A class definition with multiple
    # base classes looks like this.
    class CalendarClock(Clock, Calendar):
        """Class that uses multiple inheritance."""

    calendar_clock = CalendarClock()

    assert calendar_clock.get_date() == '12/08/2018'
    assert calendar_clock.get_time() == '11:23 PM'


def test_multiple_inheritance_worked_example():
    """Execute the documented worked example verifying decisive MRO resolution.

    Source anchors:
    - line 67: assert calendar_clock.get_date() == '12/08/2018'
    - line 68: assert calendar_clock.get_time() == '11:23 PM'

    Neighboring supported input:
    - neighboring instance with time='11:24 PM' and date='12/09/2018'
    """
    class Clock:
        time = '11:23 PM'

        def get_time(self):
            return self.time

    class Calendar:
        date = '12/08/2018'

        def get_date(self):
            return self.date

    class CalendarClock(Clock, Calendar):
        pass

    # 1. Assert MRO order (decisive dispatch linearization)
    mro_names = [cls.__name__ for cls in CalendarClock.__mro__]
    assert mro_names == ['CalendarClock', 'Clock', 'Calendar', 'object']

    # 2. Assert baseline documentation example outputs
    example_instance = CalendarClock()
    date_result = example_instance.get_date()
    time_result = example_instance.get_time()

    assert date_result == '12/08/2018'
    assert time_result == '11:23 PM'
    print(f"Documentation example outputs: date={date_result!r}, time={time_result!r}")

    # 3. Assert neighboring input
    neighbor_instance = CalendarClock()
    neighbor_instance.date = '12/09/2018'
    neighbor_instance.time = '11:24 PM'

    neighbor_date = neighbor_instance.get_date()
    neighbor_time = neighbor_instance.get_time()

    assert neighbor_date == '12/09/2018'
    assert neighbor_time == '11:24 PM'
    print(f"Neighboring inputs: date={neighbor_date!r}, time={neighbor_time!r}")
