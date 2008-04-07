#!/usr/bin/python2.4
#
# -*- coding: utf-8 -*-
# Copyright 2008 Yongjian Xu
#
###############################################################
# Copyright 2007 Google Inc.
#
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
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
###############################################################

from distutils.core import setup

setup(name='formattime',
    version='0.5',
    description='Python API for date/time formatting',
    long_description='formattime supports more than 30 different time-like' \
                     ' strings and format them into standard internet time' \
                     ' strings according to RFC 3339 and ISO 8601',
    license='LGPL',
    url='http://code.google.com/p/formattime/',
    keywords=['date', 'time', 'datetime', 'strftime', 'Python', 'formattime'],
    author = 'Yongjian (Jim) Xu',
    author_email = 'i3dmaster@gmail.com',
    py_modules=['formattime', 'formattime_test'],)
