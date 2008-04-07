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


"""A date/time string formatter.

Accept arbitrary date/time like string and try the best effort to
convert it into RFC 3339(most ISO 8601) compatible time string.

The output time format is a strict internet time format that
compatible with RFC 3339 and ISO8601 (Mostly used in restful data
exchanges such as xml,rss and ical feeds). There is a little difference
between these two standards which is the leap hour/min/second. ISO8601
does not support "24" hour but RFC 3339 does, RFC 3339 supports leap
minutes and seconds but ISO8601 does not. In order to be strict
compatible with both standards, formattime only support timestamp formats
both of these standards support, which means these edge situations will
not be supported.

Detail please see _MatchFullTime pydoc.

Functions:
  _MatchFullTime:   True if the date/time string matches the std format.
  _HandleTime:     Take an arbitrary date/time string and parse into datetime
                  objects.
  _HandleTimeZone: Return offset and offset seconds tuple from the local to utc.
  ToUTC:          Format date/time like string to UTC time string
                  in RFC 3339 format.
  ToLocal         Format date/time like string to Local time string
                  in RFC 3339 format.
"""


__author__ = 'Yongjian (Jim) Xu <i3dmaster@gmail.com>'

__VERSION__ = '0.5'


from datetime import datetime
from datetime import timedelta
from dateutil import parser
import iso8601
import os
import pytz
import re
import time

_DAYS_IN_YEAR = 365
_DAYS_OF_MONTH = 30


def _MatchFullTime(time_str, debug=0):
  """Check whether or not a time string is already formatted well.

  Three compatible time strings are considered formatted well according to
  RFC 3339 and ISO 8601:

  yyyy-mm-ddTHH:MM:SS[.1*digit](+-HH:MM|Z)

  Such as:
  1. yyyy-mm-ddTHH:MM:SS.000Z
  2. yyyy-mm-ddTHH:MM:SS.000-HH:MM
  3. yyyy-mm-ddTHH:MM:SS.nnnnnn
  4. yyyy-mm-ddTHH:MM:SSZ

  Note:
    1. ISO 8601 allows hour to be 24. This implementation follows
       RFC 3339.
    2. Leap seconds are allowed in this implementation but use it
       carefully. In most cases, you shouldn't specify leap seconds.
    3. ISO 8601 doees not allow seconds to be 60.

  Args:
    time_str: the string will be checked on.
    debug: debug level.

  Returns:
    A converted aware datetime object with timzone info.
    None if failed to match.
  """
  # description of the match regex:
  # <4 digit of year><sep -><01-09|10-12 of months><sep ->
  # <01-09|10-29|30-31 of days><sep T><00-19|20-23 of hours><sep :>
  # <00-59 of minutes><sep :><00-59 of seconds>[optional .<6 digits>]
  # <optional either Z|<00-23 of hours><sep :><00-59 of minutes>>

  m = r'^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])' \
      r'T([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(\.[0-9]{1,6}?)?' \
      r'(Z|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))?$'
  if debug: print 'using %s to match %s' % (m, time_str)
  if re.match(m, time_str):
    return iso8601.parse_date(time_str)
  return

def _GetDelimiter(time_str, date_delimiter, time_delimiter):
  """Given a time string, find out the actual delimiter regex format.

  Args:
    time_str: an arbitrary date/time like string.
    date_delimiter: a group of possible date_delimiter
    time_delimiter: ':'

  Returns:
    The date/time delimiter without '?' if it is found in the string,
    otherwise return the original delimiters
  """
  d_search = date_delimiter.replace('?', '')
  t_search = time_delimiter.replace('?', '')

  d_match = re.search(d_search, time_str)
  if d_match and d_match.group():
    date_delimiter = d_search

  t_match = re.search(t_search, time_str)
  if t_match and t_match.group():
    time_delimiter = t_search

  return date_delimiter, time_delimiter


def _HandleTime(time_str, debug=0):
  """Function to extract out possible date/time elements from a datetime like
  string.

  Args:
    time_str: a string will be checked on.
    debug: debug level.

  Returns:
    a dictionary containing date/time elements.

  Raises:
    ValueError, when the passed in string isn't a date/time like string.
  """
  match = {}
  my = r'(?P<y>[0-9]{2,4})'               # regex for year
  mm = r'(?P<m>0?[1-9]|1[0-2])'           # regex for month
  md = r'(?P<d>0?[1-9]|[12][0-9]|3[01])'  # regex for day
  mH = r'(?P<H>[01]?[0-9]|2[0-3])'        # regex for hour
  mM = r'(?P<M>[0-5]?[0-9])'              # regex for minutes
  mS = r'(?P<S>[0-5]?[0-9]|60)'           # regex for seconds
  dd = r'[-\\\\/]?'                        # regex for date delimiter
  td = r':?'                               # regex for time delimiter
  other = r'[ Tt]'                         # regex for all other stuff

  dd, td = _GetDelimiter(time_str, dd, td)

  formats = (
    r'^'+mm+dd+md+r'$',                             # (m,d)
    r'^'+my+dd+mm+dd+md+other+mH+td+mM+td+mS+r'$',  # (y,m,d,H,M,S)
    r'^'+mm+dd+md+dd+my+other+mH+td+mM+td+mS+r'$',  # (m,d,y,H,M,S)
    r'^'+my+dd+mm+dd+md+other+mH+td+mM+r'$',        # (y,m,d,H,M)
    r'^'+mm+dd+md+dd+my+other+mH+td+mM+r'$',        # (m,d,y,H,M)
    r'^'+mm+dd+md+other+mH+td+mM+td+mS+r'$',        # (m,d,y,H,M)
    r'^'+mm+dd+md+other+mH+td+mM+r'$',        # (m,d,y,H,M)
    r'^'+my+dd+mm+dd+md+r'$',                       # (y,m,d)
    r'^'+mm+dd+md+dd+my+r'$',                       # (m,d,y)
    r'^'+md+dd+mm+dd+my+r'$',                       # (d,m,y)
    r'^'+md+dd+mm+r'$',                             # (d,m)
    r'^now$',                                       # (local now)
    r'^today$',                                     # (today)
    r'^tomorrow$',                                  # (tomorrow)
    r'^yesterday$',                                 # (yesterday)
    r'^[+-][0-9]+[ymdHMS]$',                        # (plus/substract year,
                                                    # month, day, Hour, Minute,
                                                    # Second)
    #r'^'+my+mm+md+mH+mM+mS+r'$'                    # time stamp
  )

  for v in formats:
    if debug: print 'using u"%s" to match %s' % (v, time_str)
    re.purge()
    m = re.search(v, time_str)
    if m:
      if m.groups():
        try: year = int(m.group('y'))
        except IndexError: pass
        else: match['year'] = int(m.group('y'))

        try: month = int(m.group('m'))
        except IndexError: pass
        else: match['month'] = int(m.group('m'))

        try: day = int(m.group('d'))
        except IndexError: pass
        else: match['day'] = int(m.group('d'))

        try: hour = int(m.group('H'))
        except IndexError: pass
        else: match['hour'] = int(m.group('H'))

        try: minute = int(m.group('M'))
        except IndexError: pass
        else: match['minute'] = int(m.group('M'))

        try: second = int(m.group('S'))
        except IndexError: pass
        else: match['second'] = int(m.group('S'))
        break
      elif m.group():
        if m.group().lower() == 'now':
          match['now'] = True
          break
        elif m.group().lower() == 'today':
          match['today'] = True
          break
        elif m.group().lower() == 'tomorrow':
          match['tomorrow'] = True
          break
        elif m.group().lower() == 'yesterday':
          match['yesterday'] = True
          break
        elif m.group().lower().startswith('-') or \
             m.group().lower().startswith('+'):
          match['delta'] = int(m.group()[:-1])
          match['format'] = m.group()[-1]
          break

  if not match:
    raise ValueError('Can not parse the date/time string')
  else:
    return match


def _HandleTimeZone(debug=0):
  """Return offset/offsec for local timezone comparing to the utc timezone.

  The method also checks the dst info.

  Args:
    debug: (optional) set debug level.

  Returns:
    a tuple of offset and offsec.
  """
  # handle timezone.
  # check if the current timezone is in dst

  dst = False
  offset = offsec = 0

  utcnow = datetime.utcnow()
  localtime = datetime(*time.localtime()[:-3])
  if debug: print 'The localtime is %s' % localtime
  if time.timezone < 0:
    # in the east side of UTC
    delta = localtime - utcnow
  else:
    delta = utcnow - localtime

  altzone = abs(time.altzone)
  tz = abs(time.timezone)

  if abs(delta.seconds - altzone) < abs(delta.seconds - tz):
    dst = True
  else:
    dst = False

  if dst:
    offset = timedelta(seconds=-time.altzone)
    offsec = abs(time.altzone)
  else:
    offset = timedelta(seconds=-time.timezone)
    offsec = abs(time.timezone)
  if debug: print 'the offset and offsec are %s and %s' % (offset, offsec)
  return (offset, offsec)


def _UpdateDateTime(time_tuple, update_info):
  """Internal function to update the date/time info after matching the input.

  Args:
    time_tuple: The original time tuple
    update_info: dictionary containing new date/time info.

  Returns:
    new time tuple.
  """
  # NOTE: If update_info specify delta year or month, the convert is not
  #       very accurate due to timedelta does not take year and month
  #       arguments. So year will be converted to days using constant 365
  #
  year, month, day, hour, minute, second = time_tuple
  mdata = update_info

  if 'year' in mdata:
    year = mdata['year']
  if 'month' in mdata:
    month = mdata['month']
  if 'day' in mdata:
    day = mdata['day']
  if 'hour' in mdata:
    hour = mdata['hour']
  if 'minute' in mdata:
    minute = mdata['minute']
  if 'second' in mdata:
    second = mdata['second']
  if 'tomorrow' in mdata:
    day += 1
  if 'yesterday' in mdata:
    day -= 1
  if 'now' in mdata:
    hour = datetime.now().hour
    minute = datetime.now().minute
    second = datetime.now().second
  if 'delta' in mdata:
    if mdata['format'] == 'y':
      delta_day = mdata['delta'] * _DAYS_OF_YEAR
      delta_year = timedelta(days=delta_day)
      target = datetime.now() + delta_year
      year = target.year
    elif mdata['format'] == 'm':
      delta_day = mdata['delta'] * _DAYS_OF_MONTH
      delta_month = timedelta(days=delta_day)
      target = datetime.now() + delta_month
      year = target.year
      month = target.month
    elif mdata['format'] == 'd':
      delta_day = timedelta(days=mdata['delta'])
      target = datetime.now() + delta_day
      year = target.year
      month = target.month
      day = target.day
    elif mdata['format'] == 'H':
      delta_hour = timedelta(hours=mdata['delta'])
      target = datetime.now() + delta_hour
      year = target.year
      month = target.month
      day = target.day
      hour = target.hour
    elif mdata['format'] == 'M':
      delta_minute = timedelta(minutes=mdata['delta'])
      target = datetime.now() + delta_minute
      year = target.year
      month = target.month
      day = target.day
      hour = target.hour
      minute = target.minute
    elif mdata['format'] == 'S':
      delta_second = timedelta(seconds=mdata['delta'])
      target = datetime.now() + delta_second
      year = target.year
      month = target.month
      day = target.day
      hour = target.hour
      minute = target.minute
      second = target.second

  return year, month, day, hour, minute, second


def _ContainTimeInfo(datetime_info):
  """Check to see if the updated date/time info containing time info or just
  date info.

  Args:
    datetime_info: a dictionary containg matched date/time info

  Returns:
    boolean: whether the date/time info contains any time objects.
  """
  def any(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    if set1 & set2:
      return True
    else:
      return False

  set_keys = set(datetime_info.keys())
  set_values = set(datetime_info.values())

  if any(['hour', 'minute', 'second', 'H', 'M', 'S', 'now'],
      set_keys|set_values):
    return True
  else:
    return False


def _FormatTime(str_time, debug=0, format='utc'):
  """Convert pass-in date/time string literals to XML compatible
  date/time string.

  Try to make a bulletproof converter no matter what kind of
  strings passed in, it will always try to get a best reply.

  Args:
    str_time: A string literal look like a date/time format.
    debug: whether to output debug info.
    format: the output format. support either 'local' or 'utc'.

  Returns:
    XML format compatible time string with timezone considered.
    If failed, return None.

  Raises:
    ValueError: when giving up to try to parse the string.
  """
  # TODO(jimxu): adding support for detecting time/datetime objects.
  if debug: print 'passed in time is %s' % str_time

  dt = _MatchFullTime(str_time)

  if not dt:
    try: dt = parser.parse(str_time)
    except ValueError: pass
    else: dt = dt.replace(tzinfo=parser.tz.tzlocal())

  if dt:
    if format == 'utc':
      utc = pytz.utc
      dt = dt.astimezone(utc)
      return dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    elif format == 'local':
      if 'TZ' in os.environ and os.environ['TZ']:
        local = pytz.timezone(os.environ['TZ'])
        dt = dt.astimezone(local)
      else:
        dt = dt.astimezone(parser.tz.tzlocal())
      return dt.strftime('%Y-%m-%dT%H:%M:%S.000')

  # preset the time to the localtime of today 0:0:0
  datetime_tuple = (
      year, month, day, hour, minute, second) = \
          datetime.now().year, datetime.now().month, \
              datetime.now().day, 0, 0, 0

  mdata = _HandleTime(str_time)
  if debug: print mdata
  if not mdata: return

  datetime_tuple = _UpdateDateTime(datetime_tuple, mdata)
  year, month, day, hour, minute, second = datetime_tuple

  if 0 <= year <= 38:
    year += 2000
  elif 70 <= year < 100:
    year += 1900
  elif 39 <= year <= 69 or 100 <= year <= 1969 or year >= 2039:
    raise ValueError('Invalid year value. Supported year is'
                       ' from 1970 to 2038 or abbreviated notation.'
                       ' Y2k can be represented as'
                       ' either or 2000, NOT 100.')

  if not _ContainTimeInfo(mdata):
    try:
      t_obj = datetime(year, month, day)
    except ValueError, e:
      print 'Error converting time: %s' % e
      return
    else:
      if debug: print 'In date format, the local time is %s' % str(t_obj)
      if format == 'utc':
        t_obj -= _HandleTimeZone(debug=debug)[0]
        if debug: print 'In date format, the utctime is %s' % str(t_obj)
        return t_obj.strftime('%Y-%m-%dT%H:%M:%S.000Z')
      return t_obj.strftime('%Y-%m-%dT%H:%M:%S.000')
  else:
    try:
      t_obj = datetime(year, month, day, hour, minute, second)
    except ValueError, e:
      print 'Error converting time: %s' % e
      return
    else:
      if debug: print 'In full time format, the local time is %s' % str(t_obj)
      if format == 'utc':
        t_obj -= _HandleTimeZone(debug=debug)[0]
        if debug: print 'In full time format, the utctime is %s' % str(t_obj)
        return t_obj.strftime('%Y-%m-%dT%H:%M:%S.000Z')
      return t_obj.strftime('%Y-%m-%dT%H:%M:%S.000')

def ToLocal(time_string, debug=0):
  """Convert the pass-in time string to local time string format.

  Args:
    time_string: an arbitrary date/time like string
    debug: debug level.

  Returns:
    A well formatted time string using local datetime.
  """
  return _FormatTime(time_string, debug, 'local')


def ToUTC(time_string, debug=0):
  """Convert the pass-in time string to UTC time string format.

  Args:
    time_string: an arbitrary date/time like string
    debug: debug level.

  Returns:
    A well formatted time string using UTC datetime.
  """
  return _FormatTime(time_string, debug, 'utc')

# Vim :set ts=2 sw=2 expandtab
# The End
