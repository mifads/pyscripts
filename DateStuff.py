#!/usr/bin/env python3
# from http://stackoverflow.com/questions/620305/convert-year-month-day-to-day-of-year-in-python
# for avoiding daytime

def is_leap_year(year):
    """ if year is a leap year return True
        else return False """
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0

# nb Datetime way:
# dy= (t2-datetime.datetime(2012,1,1,1)).days + 1
# or 
# yday = int(period_end.strftime('%j'))
# yday = period_end.toordinal() - date(period_end.year, 1, 1).toordinal() + 1
# yday = (period_end - date(period_end.year, 1, 1)).days + 1
# yday = period_end.timetuple().tm_yday

def doy(Y,M,D):
    """ given year, month, day return day of year
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return N

def ymd(Y,N):
    """ given year = Y and day of year = N, return year, month, day
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """    
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    M = int((9 * (K + N)) / 275.0 + 0.98)
    if N < 32:
        M = 1
    D = N - int((275 * M) / 9.0) + K * int((M + 9) / 12.0) + 30
    return Y, M, D
