from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def parse_multi_day_slots(availability, slot_length_minutes, timezone_str):
   """
   Converts availability ranges into discrete time slots of fixed length,
   filtering out weekends and ensuring the slots fall within 9am-6pm in the local time zone.

   Args:
       availability: list of strings like "2025-04-01 09:00-10:00"
       slot_length_minutes: duration of each interview slot (e.g., 30)
       timezone_str: time zone (e.g., "EST", "PST", "America/New_York")

   Returns:
       A set of timezone-aware datetime objects, each representing a slot start time
   """

   TIMEZONE_MAP = {
       "PST": "America/Los_Angeles",
       "EST": "America/New_York",
       "CST": "America/Chicago",
       "MST": "America/Denver"
   }
   tz = ZoneInfo(TIMEZONE_MAP.get(timezone_str, timezone_str))
   time_slots = set()

   for time_range in availability:
       # Split "2025-04-01 09:00-10:00" into parts
       date_str, time_str = time_range.split()
       start_str, end_str = time_str.split("-")

       # Convert to timezone-aware datetime objects
       start = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)
       end = datetime.strptime(f"{date_str} {end_str}", "%Y-%m-%d %H:%M").replace(tzinfo=tz)

       # Skip weekends
       if start.weekday() >= 5: 
           continue
      
       # Clamp slots to working hours: 9am to 6pm
       work_start = start.replace(hour=9, minute=0)
       work_end = start.replace(hour=18, minute=0)
       start = max(start, work_start)
       end = min(end, work_end)

       # Generate discrete time slots (e.g., every 30 minutes)
       while start + timedelta(minutes=slot_length_minutes) <= end:
           time_slots.add(start)
           start += timedelta(minutes=slot_length_minutes)
  
   return time_slots
