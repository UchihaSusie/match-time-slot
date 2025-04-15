from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Optional: Map common timezone abbreviations to IANA
TIMEZONE_MAP = {
    "PST": "America/Los_Angeles",
    "EST": "America/New_York",
    "CST": "America/Chicago",
    "MST": "America/Denver"
}

def resolve_timezone(tz_str):
    """
    Resolves a timezone string to a ZoneInfo object.
    Supports common abbreviations by mapping them to full IANA names.
    """
    return ZoneInfo(TIMEZONE_MAP.get(tz_str, tz_str))

def parse_multi_day_slots(availability, slot_length_minutes, timezone_str):
    """
    Converts availability ranges into discrete time slots of fixed length,
    filtering out weekends and ensuring the slots fall within 9am–6pm in the local time zone.

    Args:
        availability: list of strings like "2025-04-01 09:00-10:00"
        slot_length_minutes: duration of each interview slot (e.g., 30)
        timezone_str: time zone (e.g., "EST", "PST", "America/New_York")

    Returns:
        A set of timezone-aware datetime objects, each representing a slot start time
    """
    tz = resolve_timezone(timezone_str)
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

def schedule_interviews(
    candidates: dict[str, dict],
    recruiters: dict[str, dict],
    slot_length_minutes: int,
    max_interviews_per_candidate: int,
    max_interviews_per_recruiter: int
) -> list[list[str]]:
    """
    Matches candidates and recruiters for interviews based on availability.
    Uses first-come-first-serve matching on overlapping time slots.

    Args:
        candidates: dict mapping candidate name to {"availability": [...], "timezone": ...}
        recruiters: dict mapping recruiter name to {"availability": [...], "timezone": ...}
        slot_length_minutes: fixed duration of each interview slot
        max_interviews_per_candidate: maximum interviews allowed per candidate
        max_interviews_per_recruiter: maximum interviews allowed per recruiter

    Returns:
        A list of [candidate, recruiter, time_slot] assignments
    """
    # Parse candidate availability into sets of datetime slots
    candidate_slots = {
        cand: parse_multi_day_slots(data["availability"], slot_length_minutes, data["timezone"])
        for cand, data in candidates.items()
    }

    # Parse recruiter availability into sets of datetime slots
    recruiter_slots = {
        rec: parse_multi_day_slots(data["availability"], slot_length_minutes, data["timezone"])
        for rec, data in recruiters.items()
    }

    slot_key_to_info = {}
    adj = defaultdict(list)
    for rec, r_slots in recruiter_slots.items():
        for slot in r_slots:
            key = f"{rec}_{slot.isoformat()}"
            slot_key_to_info[key] = (rec, slot)

    for cand, c_slots in candidate_slots.items():
        for key, (rec, slot) in slot_key_to_info.items():
            if slot in c_slots:
                adj[cand].append(key)

    def dfs(cand, visited, match):
        for slot_key in adj[cand]:
            if slot_key in visited:
                continue
            visited.add(slot_key)
            if slot_key not in match or dfs(match[slot_key], visited, match):
                match[slot_key] = cand
                return True
        return False

    match = {}
    candidate_match_count = defaultdict(int)
    recruiter_match_count = defaultdict(int)

    for cand in candidates:
        if candidate_match_count[cand] >= max_interviews_per_candidate:
            continue
        success = dfs(cand, set(), match)
        if success:
            candidate_match_count[cand] += 1

    scheduled = []
    for slot_key, cand in match.items():
        rec, slot = slot_key_to_info[slot_key]
        if recruiter_match_count[rec] < max_interviews_per_recruiter:
            slot_str = slot.astimezone(resolve_timezone(recruiters[rec]["timezone"])).strftime("%Y-%m-%d %H:%M %Z")
            scheduled.append([cand, rec, slot_str])
            recruiter_match_count[rec] += 1

    return sorted(scheduled, key=lambda x: x[2])