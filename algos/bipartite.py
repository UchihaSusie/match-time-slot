from collections import defaultdict
from zoneinfo import ZoneInfo
from utils.time_paraser import parse_multi_day_slots


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

    candidate_slots_utc = {}
    utc_to_original_map = {}
   
    for cand, slots in candidate_slots.items():
       candidate_slots_utc[cand] = set()
       for slot in slots:
           # Convert to UTC time
           slot_utc = slot.astimezone(ZoneInfo("UTC"))
           candidate_slots_utc[cand].add(slot_utc)
           # Record mapping from UTC -> original time
           utc_to_original_map[(cand, slot_utc)] = slot
   
   # Similarly process the recruiter's time slots
    recruiter_slots_utc = {}
    for rec, slots in recruiter_slots.items():
       recruiter_slots_utc[rec] = set()
       for slot in slots:
           slot_utc = slot.astimezone(ZoneInfo("UTC"))
           recruiter_slots_utc[rec].add(slot_utc)

    # # Build candidate-recruiter-slot match list (only where slots overlap)
    # edges = []
    # for cand, c_slots in candidate_slots.items():
    #     for rec, r_slots in recruiter_slots.items():
    #         for slot in c_slots & r_slots:
    #             edges.append((cand, rec, slot))

      # Connect candidates to recruiters in UTC timezone
    edges = []
    for cand, c_slots_utc in candidate_slots_utc.items():
       for rec, r_slots_utc in recruiter_slots_utc.items():
           # Find commonly available times in UTC
           common_slots_utc = c_slots_utc & r_slots_utc
           
           for slot_utc in common_slots_utc:
               # Use candidate's original timezone time as the result
               original_slot = utc_to_original_map[(cand, slot_utc)]
               edges.append((cand, rec, original_slot))

    # Schedule interviews using first-come-first-serve on sorted slots
    scheduled = []
    candidate_counts = defaultdict(int)
    recruiter_counts = defaultdict(int)
    used_slots = set()

    for cand, rec, slot in sorted(edges, key=lambda x: x[2]):
        if (
            candidate_counts[cand] < max_interviews_per_candidate and
            recruiter_counts[rec] < max_interviews_per_recruiter and
            (cand, slot) not in used_slots and
            (rec, slot) not in used_slots
        ):
            scheduled.append([cand, rec, slot.strftime("%Y-%m-%d %H:%M %Z")])
            candidate_counts[cand] += 1
            recruiter_counts[rec] += 1
            used_slots.add((cand, slot))
            used_slots.add((rec, slot))

    return scheduled

# === Example usage ===
if __name__ == "__main__":
    candidates = {
        "Alice": {
            "availability": ["2025-04-01 09:00-10:00", "2025-04-01 13:00-14:00"],
            "timezone": "EST"
        },
        "Bob": {
            "availability": ["2025-04-01 09:30-10:30"],
            "timezone": "EST"
        },
        "Charlie": {
            "availability": ["2025-04-01 13:00-14:00"],
            "timezone": "EST"
        }
    }

    recruiters = {
        "R1": {
            "availability": ["2025-04-01 09:00-10:00"],
            "timezone": "EST"
        },
        "R2": {
            "availability": ["2025-04-01 13:00-14:00", "2025-04-01 09:30-10:30"],
            "timezone": "EST"
        }
    }

    result = schedule_interviews(
        candidates,
        recruiters,
        slot_length_minutes=30,
        max_interviews_per_candidate=2,
        max_interviews_per_recruiter=2
    )

    print("Scheduled interviews:")
    for interview in result:
        print(interview)