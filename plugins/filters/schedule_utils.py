#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Buøy-Vehn <dbv@redpill-linpro.com>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# https://docs.ansible.com/ansible/latest/dev_guide/developing_plugins.html#developing-filter-plugins

""" Ansible filter for comparing dates with today"""
from datetime import datetime, timedelta
import operator
import unittest
import re


class FilterModule:
    """Ansible Module for adding custom filters."""

    # pylint: disable=R0201
    def get_dates(self, datestring):
        """Return a dictionary with datetime objects.
        Either with or without times. In any case with a date.
        input:
          string: $datestring(YYYY-mm-dd[(T| )HH:MM:SS])

        return:
          dict {
              'now_date': $now(YYYY-mm-dd[ HH:MM:SS],
              'check_date': $datesting(YYYY-mm-dd[ HH:MM:SS])
          }
        """
        dates = {}
        pattern = r"^\d{4}-\d{2}\-\d{2}$"
        if re.match(pattern, datestring):
            dates["now_date"] = datetime.today().date()
            dates["check_date"] = datetime.strptime(
                datestring, "%Y-%m-%d"
            ).date()

        pattern = r"^\d{4}-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2}$"
        if re.match(pattern, datestring):
            dates["now_date"] = datetime.today().replace(microsecond=0)
            dates["check_date"] = datetime.strptime(
                datestring, "%Y-%m-%dT%H:%M:%S"
            )

        pattern = r"^\d{4}-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}$"
        if re.match(pattern, datestring):
            dates["now_date"] = datetime.today().replace(microsecond=0)
            dates["check_date"] = datetime.strptime(
                datestring, "%Y-%m-%d %H:%M:%S"
            )
        return dates

    def is_due(self, datestring, date_operator=None):
        """Checks if a given datestring fulfills the operator
        requirements compared to today
        """
        if not date_operator:
            date_operator = "=="
        ops = {
            "==": operator.eq,
            ">": operator.gt,
            ">=": operator.ge,
            "<=": operator.le,
            "<": operator.lt,
            "!=": operator.ne,
        }
        check_date = self.get_dates(datestring)["check_date"]
        now_date = self.get_dates(datestring)["now_date"]
        return ops[date_operator](now_date, check_date)

    def is_past(self, datestring):
        """Checks if a given datestring lies in the past."""
        check_date = self.get_dates(datestring)["check_date"]
        now_date = self.get_dates(datestring)["now_date"]
        if check_date < now_date:
            return True
        return False

    def is_today_or_past(self, datestring):
        """Checks if a given datestring is either today or lies in the past."""
        check_date = self.get_dates(datestring)["check_date"]
        now_date = self.get_dates(datestring)["now_date"]
        if check_date <= now_date:
            return True
        return False

    def is_future(self, datestring):
        """Checks if a given datestring is in the future."""
        check_date = self.get_dates(datestring)["check_date"]
        now_date = self.get_dates(datestring)["now_date"]
        if check_date > now_date:
            return True
        return False

    def is_today_or_future(self, datestring):
        """Checks if a given datestring is in the future or today."""
        check_date = self.get_dates(datestring)["check_date"]
        now_date = self.get_dates(datestring)["now_date"]
        if check_date >= now_date:
            return True
        return False

    def is_today(self, datestring):
        """Checks if a given datestring is today."""
        check_date = self.get_dates(datestring)["check_date"]
        now_date = self.get_dates(datestring)["now_date"]
        if check_date == now_date:
            return True
        return False

    def filters(self):
        """Ties the filtername to the corresponding method."""
        return {
            "is_due": self.is_due,
            "is_future": self.is_future,
            "is_past": self.is_past,
            "is_today_or_future": self.is_today_or_future,
            "is_today_or_past": self.is_today_or_past,
            "is_today": self.is_today,
        }


# ---


class TestStringUtlisFunctions(unittest.TestCase):
    """Tests for the ansible plugin."""

    def setUp(self):
        """Setup method to run before each test."""
        self.filter = FilterModule()
        self.date_today = str(datetime.today().date())
        self.date_today_wt = str(datetime.today().now().replace(microsecond=0))
        self.date_yesterday = str(
            (datetime.today() - timedelta(days=1)).date()
        )
        self.date_yesterday_wt = str(
            ((datetime.now() - timedelta(days=1)).replace(microsecond=0))
        )
        self.date_tomorrow = str((datetime.today() + timedelta(days=1)).date())
        self.date_tomorrow_wt = str(
            ((datetime.now() + timedelta(days=1)).replace(microsecond=0))
        )

    def test_get_dates_without_time(self):
        """Return dict with two dates: now and the requested one."""
        result = self.filter.get_dates("1970-01-01")
        self.assertEqual(
            result["check_date"],
            datetime.strptime("1970-01-01", "%Y-%m-%d").date(),
        )
        self.assertEqual(
            result["now_date"],
            datetime.strptime(self.date_today, "%Y-%m-%d").date(),
        )

    def test_get_dates_with_time(self):
        """Return dict with two dates: now and the requested one."""
        # Removing the microseconds from this timestamp.
        time_now = str(datetime.today().replace(microsecond=0))

        # Test with a 'T' instead of a whitespace
        result = self.filter.get_dates("1970-01-01T01:01:01")
        self.assertEqual(
            result["check_date"],
            datetime.strptime("1970-01-01 01:01:01", "%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(
            result["now_date"],
            datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S"),
        )

        # Test with a space instead of a 'T'
        result = self.filter.get_dates("1970-01-01T01:01:01")
        self.assertEqual(
            result["check_date"],
            datetime.strptime("1970-01-01 01:01:01", "%Y-%m-%d %H:%M:%S"),
        )

        self.assertEqual(
            result["now_date"],
            datetime.strptime(time_now, "%Y-%m-%d %H:%M:%S"),
        )

    def test_is_past(self):
        """Verify correct output from is_past"""
        self.assertTrue(self.filter.is_past(self.date_yesterday))
        self.assertFalse(self.filter.is_past(self.date_today))
        self.assertFalse(self.filter.is_past(self.date_tomorrow))

    def test_is_past_wtime(self):
        """Verify correct outout from is_past with time"""
        self.assertFalse(self.filter.is_past(self.date_tomorrow_wt))
        self.assertFalse(self.filter.is_past(self.date_today_wt))
        self.assertTrue(self.filter.is_past(self.date_yesterday_wt))

    def test_is_today_or_past(self):
        """Verify correct output fromn is_today_an_past"""
        self.assertTrue(self.filter.is_today_or_past(self.date_today))
        self.assertTrue(self.filter.is_today_or_past(self.date_yesterday))
        self.assertFalse(self.filter.is_today_or_past(self.date_tomorrow))

    def test_is_today_or_past_wt(self):
        """Verify correct output fromn is_today_an_past"""
        self.assertTrue(self.filter.is_today_or_past(self.date_today_wt))
        self.assertTrue(self.filter.is_today_or_past(self.date_yesterday_wt))
        self.assertFalse(self.filter.is_today_or_past(self.date_tomorrow_wt))

    def test_is_future(self):
        """Verify correct output from future day"""
        self.assertFalse(self.filter.is_future(self.date_today))
        self.assertFalse(self.filter.is_future(self.date_yesterday))
        self.assertTrue(self.filter.is_future(self.date_tomorrow))

    def test_is_today_or_future(self):
        """Verify correct output from today and future"""
        self.assertTrue(self.filter.is_today_or_future(self.date_today))
        self.assertFalse(self.filter.is_today_or_future(self.date_yesterday))
        self.assertTrue(self.filter.is_today_or_future(self.date_tomorrow))

    def test_is_future_wt(self):
        """Verify correct output from future day with time"""
        self.assertFalse(self.filter.is_future(self.date_today_wt))
        self.assertFalse(self.filter.is_future(self.date_yesterday_wt))
        self.assertTrue(self.filter.is_future(self.date_tomorrow_wt))

    def test_is_today(self):
        """Verify correct output from today only"""
        self.assertTrue(self.filter.is_today(self.date_today))
        self.assertFalse(self.filter.is_today(self.date_yesterday))
        self.assertFalse(self.filter.is_today(self.date_tomorrow))

    def test_is_today_wt(self):
        """Verify correct output from today only"""
        self.assertTrue(self.filter.is_today(self.date_today_wt))
        self.assertFalse(self.filter.is_today(self.date_yesterday_wt))
        self.assertFalse(self.filter.is_today(self.date_tomorrow_wt))

    def test_is_due_eq(self):
        """Verify the return for due with todays date."""
        self.assertTrue(
            self.filter.is_due(self.date_today, date_operator="==")
        )
        self.assertFalse(
            self.filter.is_due(self.date_tomorrow, date_operator="==")
        )
        self.assertFalse(
            self.filter.is_due(self.date_yesterday, date_operator="==")
        )

    def test_is_due_gt(self):
        """Verify the return for due with greater than"""
        self.assertFalse(
            self.filter.is_due(self.date_today, date_operator=">")
        )
        self.assertFalse(
            self.filter.is_due(self.date_tomorrow, date_operator=">")
        )
        self.assertTrue(
            self.filter.is_due(self.date_yesterday, date_operator=">")
        )

    def test_is_due_ge(self):
        """Verify the return for due with greater-equal than"""
        self.assertTrue(
            self.filter.is_due(self.date_today, date_operator=">=")
        )
        self.assertFalse(
            self.filter.is_due(self.date_tomorrow, date_operator=">=")
        )
        self.assertTrue(
            self.filter.is_due(self.date_yesterday, date_operator=">=")
        )

    def test_is_due_le(self):
        """Verify the return for due with less-equal than"""
        self.assertTrue(
            self.filter.is_due(self.date_today, date_operator="<=")
        )
        self.assertTrue(
            self.filter.is_due(self.date_tomorrow, date_operator="<=")
        )
        self.assertFalse(
            self.filter.is_due(self.date_yesterday, date_operator="<=")
        )

    def test_is_due_lt(self):
        """Verify the return for due with less than"""
        self.assertFalse(
            self.filter.is_due(self.date_today, date_operator="<")
        )
        self.assertTrue(
            self.filter.is_due(self.date_tomorrow, date_operator="<")
        )
        self.assertFalse(
            self.filter.is_due(self.date_yesterday, date_operator="<")
        )

    def test_is_due_ne(self):
        """Verify the return for due with less than"""
        self.assertFalse(
            self.filter.is_due(self.date_today, date_operator="!=")
        )
        self.assertTrue(
            self.filter.is_due(self.date_tomorrow, date_operator="!=")
        )
        self.assertTrue(
            self.filter.is_due(self.date_yesterday, date_operator="!=")
        )


if __name__ == "__main__":
    unittest.main()
