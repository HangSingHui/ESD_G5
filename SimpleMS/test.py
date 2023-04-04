
import calendar
import datetime
 
date = datetime.datetime.utcnow()
utc_time = calendar.timegm(date.utctimetuple())
print(utc_time)