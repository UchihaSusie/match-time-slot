from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import copy
from statistics import variance
from utils.time_paraser import parse_multi_day_slots
def greedy_schedule_interviews(
    candidates: dict[str, dict],
    recruiters: dict[str, dict],
    slot_length_minutes: int,
    max_interviews_per_candidate: int,
    max_interviews_per_recruiter: int
) -> list[list[str]]:
    """
    Matches candidates and recruiters for interviews using a greedy algorithm
    that prioritizes earlier time slots.
    
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

    # Create UTC version for each time slot and maintain mapping between original time slot and UTC time slot
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

    # Build candidate-recruiter-slot match list (only where slots overlap)
    # edges = []
    # for cand, c_slots in candidate_slots.items():
    #     for rec, r_slots in recruiter_slots.items():
    #         for slot in c_slots & r_slots:  # Intersection of available times
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
    used_slots = set()  # Track which slots are already used by whom

    # Sort by time slot (earliest first) for greedy scheduling
    for cand, rec, slot in sorted(edges, key=lambda x: x[2]):
        if (
            candidate_counts[cand] < max_interviews_per_candidate and
            recruiter_counts[rec] < max_interviews_per_recruiter and
            (cand, slot) not in used_slots and
            (rec, slot) not in used_slots
        ):
            # Schedule the interview
            scheduled.append([cand, rec, slot.strftime("%Y-%m-%d %H:%M %Z")])
            candidate_counts[cand] += 1
            recruiter_counts[rec] += 1
            used_slots.add((cand, slot))
            used_slots.add((rec, slot))

    return scheduled


def handle_real_time_adjustment(
    scheduled: list[list[str]],
    candidate_to_adjust: str = None,
    recruiter_to_adjust: str = None,
    time_slot_to_adjust: str = None,
    action: str = "cancel",
    candidates: dict[str, dict] = None,
    recruiters: dict[str, dict] = None,
    slot_length_minutes: int = 30,
    max_interviews_per_candidate: int = 2,
    max_interviews_per_recruiter: int = 2
) -> list[list[str]]:
    """
    Handle real-time adjustments to the interview schedule.
    
    Args:
        scheduled: Current schedule of interviews
        candidate_to_adjust: Name of candidate to adjust (or None)
        recruiter_to_adjust: Name of recruiter to adjust (or None)
        time_slot_to_adjust: Specific time slot to adjust (or None for all)
        action: "cancel", "reschedule", or "add"
        candidates: Updated dictionary of candidate availability
        recruiters: Updated dictionary of recruiter availability
        slot_length_minutes: Duration of each interview slot
        max_interviews_per_candidate: Maximum interviews per candidate
        max_interviews_per_recruiter: Maximum interviews per recruiter
        
    Returns:
        Updated schedule
    """
    # Make a copy of the schedule to avoid modifying the original
    updated_schedule = copy.deepcopy(scheduled)
    
    # Helper function to check if an interview matches the adjustment criteria
    def matches_criteria(interview):
        matches = True
        if candidate_to_adjust and interview[0] != candidate_to_adjust:
            matches = False
        if recruiter_to_adjust and interview[1] != recruiter_to_adjust:
            matches = False
        if time_slot_to_adjust and time_slot_to_adjust not in interview[2]:
            matches = False
        return matches
    
    if action == "cancel":
        # Remove interviews that match the criteria
        updated_schedule = [interview for interview in updated_schedule 
                           if not matches_criteria(interview)]
    
    elif action == "add" and candidates and recruiters:
        # Create subset of candidates and recruiters for targeted scheduling
        subset_candidates = {}
        subset_recruiters = {}
        
        if candidate_to_adjust:
            subset_candidates = {candidate_to_adjust: candidates[candidate_to_adjust]}
        else:
            subset_candidates = candidates
            
        if recruiter_to_adjust:
            subset_recruiters = {recruiter_to_adjust: recruiters[recruiter_to_adjust]}
        else:
            subset_recruiters = recruiters
        
        # Get existing bookings to avoid conflicts
        existing_bookings = set()
        for interview in updated_schedule:
            cand, rec, time = interview
            # Parse time string back to datetime for comparison
            dt_format = "%Y-%m-%d %H:%M %Z"
            slot_dt = datetime.strptime(time, dt_format)
            existing_bookings.add((cand, slot_dt))
            existing_bookings.add((rec, slot_dt))
        
        # Try to schedule new interviews
        new_interviews = greedy_schedule_interviews(
            subset_candidates,
            subset_recruiters,
            slot_length_minutes,
            max_interviews_per_candidate,
            max_interviews_per_recruiter
        )
        
        # Only add non-conflicting interviews
        for new_interview in new_interviews:
            cand, rec, time = new_interview
            dt_format = "%Y-%m-%d %H:%M %Z"
            slot_dt = datetime.strptime(time, dt_format)
            
            # Check if this would create a conflict
            if (cand, slot_dt) not in existing_bookings and (rec, slot_dt) not in existing_bookings:
                updated_schedule.append(new_interview)
                existing_bookings.add((cand, slot_dt))
                existing_bookings.add((rec, slot_dt))
    
    elif action == "reschedule" and candidates and recruiters:
        # First cancel the matching interviews
        temp_schedule = [interview for interview in updated_schedule 
                         if not matches_criteria(interview)]
        
        # Then try to add new interviews for the affected people
        subset_candidates = {}
        subset_recruiters = {}
        
        if candidate_to_adjust:
            subset_candidates = {candidate_to_adjust: candidates[candidate_to_adjust]}
        if recruiter_to_adjust:
            subset_recruiters = {recruiter_to_adjust: recruiters[recruiter_to_adjust]}
            
        # If we have both candidates and recruiters to reschedule
        if subset_candidates and subset_recruiters:
            # Use the existing function for adding
            return handle_real_time_adjustment(
                temp_schedule,
                candidate_to_adjust,
                recruiter_to_adjust,
                None,  # Don't filter by time slot for rescheduling
                "add",
                candidates,
                recruiters,
                slot_length_minutes,
                max_interviews_per_candidate,
                max_interviews_per_recruiter
            )
        else:
            # If we're only rescheduling one side, just return the cancelled schedule
            return temp_schedule
    
    return updated_schedule


def optimize_fairness(
    scheduled: list[list[str]],
    candidates: dict[str, dict],
    recruiters: dict[str, dict],
    slot_length_minutes: int,
    fairness_objective: str = "balanced"
) -> list[list[str]]:
    """
    Optimize the interview schedule based on different fairness objectives.
    
    Args:
        scheduled: Current schedule of interviews
        candidates: Dictionary of candidate availability
        recruiters: Dictionary of recruiter availability
        slot_length_minutes: Duration of each interview slot
        fairness_objective: "balanced", "max_total", or "min_variance"
        
    Returns:
        Optimized schedule
    """
    # Count interviews per person
    candidate_count = defaultdict(int)
    recruiter_count = defaultdict(int)
    
    for interview in scheduled:
        cand, rec, _ = interview
        candidate_count[cand] += 1
        recruiter_count[rec] += 1
    
    # Candidates/recruiters with no interviews
    unmatched_candidates = [c for c in candidates if c not in candidate_count]
    unmatched_recruiters = [r for r in recruiters if r not in recruiter_count]
    
    if fairness_objective == "balanced":
        # Try to give everyone at least one interview
        if unmatched_candidates and unmatched_recruiters:
            # Create a subset of candidates and recruiters to focus on
            subset_candidates = {c: candidates[c] for c in unmatched_candidates}
            subset_recruiters = {r: recruiters[r] for r in unmatched_recruiters}
            
            # Schedule interviews just for the unmatched people
            new_schedule = greedy_schedule_interviews(
                subset_candidates,
                subset_recruiters,
                slot_length_minutes,
                1,  # Just one interview per unmatched person
                1   # Just one interview per unmatched person
            )
            
            # Add these to the existing schedule
            return scheduled + new_schedule
    
    elif fairness_objective == "max_total":
        # Just try to schedule as many interviews as possible
        # This is essentially what the greedy algorithm already does
        return scheduled
    
    elif fairness_objective == "min_variance":
        # Calculate current variance in interview distribution
        if candidate_count:
            candidate_interview_counts = list(candidate_count.values())
            if len(candidate_interview_counts) > 1:
                cand_variance = variance(candidate_interview_counts)
            else:
                cand_variance = 0
        else:
            cand_variance = 0
            
        if recruiter_count:
            recruiter_interview_counts = list(recruiter_count.values())
            if len(recruiter_interview_counts) > 1:
                rec_variance = variance(recruiter_interview_counts)
            else:
                rec_variance = 0
        else:
            rec_variance = 0
            
        # If variance is already 0, nothing to optimize
        if cand_variance == 0 and rec_variance == 0:
            return scheduled
            
        # Otherwise, try to redistribute some interviews
        # This is a complex optimization problem, so here's a simple approach:
        # Find participants with most and fewest interviews and try to adjust
        
        # This would be more complex to implement fully, but would involve:
        # 1. Identifying overscheduled and underscheduled participants
        # 2. Searching for alternative time slots to reduce variance
        # 3. Making adjustments that reduce overall variance
        
        # For simplicity, we'll just return the current schedule
        # A real implementation would need more sophisticated optimization
        
    return scheduled


# Example usage
if __name__ == "__main__":
    # Use the same test data as in bipartite.py
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

    # First, schedule interviews using greedy algorithm
    initial_schedule = greedy_schedule_interviews(
        candidates,
        recruiters,
        slot_length_minutes=30,
        max_interviews_per_candidate=2,
        max_interviews_per_recruiter=2
    )

    print("Initial schedule:")
    for interview in initial_schedule:
        print(f"Candidate: {interview[0]}, Recruiter: {interview[1]}, Time: {interview[2]}")
    
    # Example of real-time adjustment: cancel Alice's interview
    print("\nAfter cancellation:")
    adjusted_schedule = handle_real_time_adjustment(
        initial_schedule,
        candidate_to_adjust="Alice",
        action="cancel"
    )
    for interview in adjusted_schedule:
        print(f"Candidate: {interview[0]}, Recruiter: {interview[1]}, Time: {interview[2]}")
    
    # Example of optimizing for fairness
    print("\nAfter fairness optimization:")
    fair_schedule = optimize_fairness(
        initial_schedule,
        candidates,
        recruiters,
        slot_length_minutes=30,
        fairness_objective="balanced"
    )
    for interview in fair_schedule:
        print(f"Candidate: {interview[0]}, Recruiter: {interview[1]}, Time: {interview[2]}")