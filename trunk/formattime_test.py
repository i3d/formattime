#!/usr/bin/python2.4

# Copyright 2007 Yongjian Xu
# Portions Copyright 2007 Google Inc.  All rights reserved.

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA


__author__ = 'Yongjian (Jim) Xu <i3dmaster@gmail.com>'


from datetime import datetime
import re
import os
import pytz
import time
import unittest
import formattime

class FormatTimeTestCase(unittest.TestCase):

  def testMatchFullTimeLeapSeconds(self):
    # by using iso8601. this is no longer a valid time format.
    ft = '1997-07-01T23:59:60Z'
    self.assertFalse(formattime._MatchFullTime(ft))

  def testMatchFullTimeNormalSeconds(self):
    ft = '1997-07-01T23:59:59Z'
    self.assertTrue(formattime._MatchFullTime(ft))

  def testMatchFullTime24Hours(self):
    ft = '1997-07-01T24:00:00Z'
    self.assertFalse(formattime._MatchFullTime(ft))

  def testMatchFullTimeMilSec(self):
    ft = '1997-07-01T23:59:59.999'
    self.assertTrue(formattime._MatchFullTime(ft))

  def testMatchFullTimeOffsetUTC(self):
    ft = '1997-07-01T23:59:60.999999+08:00'
    self.assertFalse(formattime._MatchFullTime(ft))

  def testMatchFullTimeMilSecLongerThan6Digit(self):
    ft = '1997-07-01T23:59:60.9999999'
    self.assertFalse(formattime._MatchFullTime(ft))

  def testMatchFullTimeUTCLocalMix(self):
    ft = '1997-07-01T23:59:60.2344Z-00:20'
    self.assertFalse(formattime._MatchFullTime(ft))

  def testMatchFullTimeToNextYear(self):
    ft = '1997-12-31T23:59:60'
    self.assertFalse(formattime._MatchFullTime(ft))

  def testMatchFullTimeOffsetLessThanHour(self):
    ft = '1937-01-01T12:00:27.87+00:20'
    self.assertTrue(formattime._MatchFullTime(ft))

  def testToUTCXMLTime(self):
    self.assertEqual(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                     formattime.ToUTC('now'))

  def testToLocalXMLTime(self):
    local_time = datetime.now()
    xmltime = local_time.strftime('%Y-%m-%dT%H:%M:%S.000')
    self.assertEqual(xmltime, formattime.ToLocal('now'))

  def testFormatTimeYear(self):
    year = formattime._HandleTime('07-06-29')['year']
    self.assertEqual(7, year)

  def testFormatTimeMonth(self):
    month = formattime._HandleTime('72-12-31')['month']
    self.assertEqual(12, month)

  def testFormatTimeday(self):
    day = formattime._HandleTime(r'12/13\09')['day']
    self.assertEqual(13, day)

  def testFormatTimeYear2(self):
    year = formattime._HandleTime(r'13/11/2222')['year']
    self.assertEqual(2222, year)

  def testFormatTimeYear3(self):
    xmltime = formattime.ToLocal('91-01-01')
    year = xmltime.split('-')[0]
    self.assertEqual(1991, int(year))

  def testFormatDate1(self):
    self.assertEqual(6, formattime._HandleTime('6/24')['month'])

  def testFormatDate2(self):
    self.assertEqual(6, formattime._HandleTime(r'6\24')['month'])

  def testFormatDateError(self):
    self.assertRaises(ValueError, formattime._HandleTime, '60/20')

  def testFormatDay1(self):
    self.assertEqual(20, formattime._HandleTime('20/4')['day'])

  def testFormatDay2(self):
    self.assertEqual(20, formattime._HandleTime(r'20\4')['day'])

  def testFormatDayError(self):
    self.assertRaises(ValueError, formattime._HandleTime, '60/100')

  def testFormatDateTime1(self):
    year = formattime._HandleTime('6/24/07T12:00:00')['year']
    month = formattime._HandleTime('6/24/07T12:00:00')['month']
    day = formattime._HandleTime('6/24/07T12:00:00')['day']
    hour = formattime._HandleTime('6/24/07T12:00:00')['hour']
    minute = formattime._HandleTime('6/24/07T12:00:00')['minute']
    second = formattime._HandleTime('6/24/07T12:00:00')['second']
    self.assertEqual(7, year)
    self.assertEqual(6, month)
    self.assertEqual(24, day)
    self.assertEqual(12, hour)
    self.assertEqual(0, minute)
    self.assertEqual(0, second)

  def testFormatDateTime2(self):
    year = formattime._HandleTime('07/07/07T23:59:59')['year']
    month = formattime._HandleTime('07/07/07T23:59:59')['month']
    day = formattime._HandleTime('07/07/07T23:59:59')['day']
    hour = formattime._HandleTime('07/07/07T23:59:59')['hour']
    minute = formattime._HandleTime('07/07/07T23:59:59')['minute']
    second = formattime._HandleTime('07/07/07T23:59:59')['second']
    self.assertEqual(7, year)
    self.assertEqual(7, month)
    self.assertEqual(7, day)
    self.assertEqual(23, hour)
    self.assertEqual(59, minute)
    self.assertEqual(59, second)

  def testFormatDateTimeError1(self):
    self.assertRaises(ValueError, formattime._HandleTime,
      '10000-01-01 12:00:00')

  def testFormatDateTimeError2(self):
    self.assertRaises(ValueError, formattime._HandleTime,
      '90-00-01 12:00:00')

  def testFormatDateTimeError3(self):
    self.assertRaises(ValueError, formattime._HandleTime,
      '90-10-00 12:00:00')

  def testFormatDateTimeError4(self):
    self.assertRaises(ValueError, formattime._HandleTime,
      '90-10-01 33:00:00')

  def testFormatDateTimeError5(self):
    self.assertRaises(ValueError, formattime._HandleTime,
      '90-10-01 23:660:00')

  def testFormatDateTimeError6(self):
    self.assertRaises(ValueError, formattime._HandleTime,
      '90-10-01 23:60:00')

  def testFormatTimeYearErrorLocal(self):
    self.assertRaises(ValueError, formattime.ToLocal, '10000-01-01')

  def testFormatTimeYearErrorUTC(self):
    self.assertRaises(ValueError, formattime.ToUTC, '10000-01-01')

  def testFormatTimeMonthErrorLocal(self):
    self.assertRaises(ValueError, formattime.ToLocal, '1990-00-01')

  def testFormatTimeMonthErrorUTC(self):
    self.assertRaises(ValueError, formattime.ToUTC, '1990-00-01')

  def testFormatTimeMonthError2(self):
    self.assertRaises(ValueError, formattime.ToLocal, '2007-30-06')

  def testFormatTimeTZ(self):
    if not os.environ.get('TZ'):
      os.environ['TZ'] = 'Europe/Zurich'
      time.tzset()
    there = pytz.timezone(os.environ['TZ'])
    there_time = datetime(2029, 07, 6, tzinfo=there)
    utc_t = there_time.astimezone(pytz.utc)
    del os.environ['TZ']
    time.tzset()
    self.assertFalse(there_time.strftime('%Y-%m-%dT%H:%M:%S.000Z') ==
      formattime.ToLocal('07-06-29'))

  def testGdataQueryFormatTimeToday(self):
    xmltime = formattime.ToLocal('today')
    m = re.search(r'-(?P<d>[^-]*)T', xmltime)
    day = datetime.today().day
    self.assertEqual(day, int(m.group('d')))

  def testFormatTimeDateErrorLocal(self):
    self.assertRaises(ValueError, formattime.ToLocal, '2007-06-900')

  def testFormatTimeDateErrorUTC(self):
    self.assertRaises(ValueError, formattime.ToUTC, '2007-06-900')

  def testFormatTimeDateErrorLocal1(self):
    self.assertRaises(ValueError, formattime.ToLocal, '2007-06-00')

  def testFormatTimeDateErrorUTC1(self):
    self.assertRaises(ValueError, formattime.ToUTC, '2007-06-00')

  def testFormatTimeErrorMonth(self):
    self.assertRaises(ValueError, formattime._HandleTime, '066/25/07')

  def testFormatTimeErrorMonthDate(self):
    self.assertRaises(ValueError, formattime._HandleTime, '60/255/07')

  def testFormatTimeOnlyTimeInfo(self):
    self.assertRaises(ValueError, formattime._HandleTime, '12:13:00')

  def testFormatTimeNotDateTimeString(self):
    self.assertRaises(ValueError, formattime._HandleTime, 'foo bar')

  def testFormatTimeICalTime(self):
    ical_time = '20071130T100000'
    formatted = '2007-11-30T10:00:00.000'
    self.assertEqual(formatted, formattime.ToLocal(ical_time))

  def testFormatTimeNoSeconds(self):
    d_string = '11/30/2007 11:30:00'
    utc = pytz.utc
    tzlocal = pytz.timezone('America/Los_Angeles')
    d = datetime(2007, 11, 30, 11, 30, tzinfo=tzlocal)
    utc_d = d.astimezone(utc)
    self.assertEqual(formattime.ToUTC(d_string),
        utc_d.strftime('%Y-%m-%dT%H:%M:%S.000Z'))

  def testFormatTimeNoSeconds(self):
    d_string = '11/30/2007 11:30'
    utc = pytz.utc
    tzlocal = pytz.timezone('America/Los_Angeles')
    d = datetime(2007, 11, 30, 11, 30, tzinfo=tzlocal)
    utc_d = d.astimezone(utc)
    self.assertEqual(formattime.ToUTC(d_string),
        utc_d.strftime('%Y-%m-%dT%H:%M:%S.000Z'))

  def testFormatTimeToLocal(self):
    time_str = '2007-11-09T07:00:00.000-08:00'
    local = '2007-11-09T07:00:00.000'
    self.assertEqual(local, formattime.ToLocal(time_str))

  def testFormatTimeDiffToLocal(self):
    time_str = '2007-11-09T07:00:00.000-08:00'
    zurich_local = '2007-11-09T16:00:00.000'
    os.environ['TZ'] = 'Europe/Zurich'
    time.tzset()
    self.assertEqual(zurich_local, formattime.ToLocal(time_str))
    del os.environ['TZ']
    time.tzset()

  def testFormatTimeMonthDateWithTime(self):
    time_str = '1/9 10:00'
    utc_t = '2008-01-09T18:00:00.000Z'
    self.assertEqual(utc_t, formattime.ToUTC(time_str))

  def testFormatTimeMonthDateWithTime2(self):
    time_str = '1/9 10:00:11'
    utc_t = '2008-01-09T18:00:11.000Z'
    self.assertEqual(utc_t, formattime.ToUTC(time_str))

  def testFormatTimeDateTimePickerFormat(self):
    t1 = formattime.ToLocal('4/1/2008')
    t2 = formattime.ToLocal('April 1, 2008')
    self.assertEqual(t1, t2)

if __name__ == '__main__':
  unittest.main()
