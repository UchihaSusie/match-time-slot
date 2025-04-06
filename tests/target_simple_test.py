import sys
import os
# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algos.networkflow import schedule_interviews as networkflow_schedule
from algos.bipartite import schedule_interviews as bipartite_schedule
from algos.greedy import greedy_schedule_interviews as greedy_schedule
import time

def run_test(name, candidates, recruiters, slot_length, max_cand_interviews, max_rec_interviews):
    """Run a single test case and compare results from all three methods"""
    print(f"\n=== Test Case: {name} ===")
    print(f"Time slot length: {slot_length} minutes")
    print(f"Maximum interviews per candidate: {max_cand_interviews}")
    print(f"Maximum interviews per recruiter: {max_rec_interviews}")
    
    test_case = (candidates, recruiters, slot_length, max_cand_interviews, max_rec_interviews)
    methods = {
        "Network Flow": networkflow_schedule,
        "Bipartite": bipartite_schedule,
        "Greedy": greedy_schedule
    }
    
    results = {}
    
    for method_name, schedule_func in methods.items():
        print(f"\n{method_name} Method:")
        try:
            start_time = time.time()
            result = schedule_func(*test_case)
            end_time = time.time()
            
            print(f"Number of scheduled interviews: {len(result)}")
            print(f"Execution time: {(end_time - start_time):.4f} seconds")
            
            # Print detailed results
            print("Interview scheduling details:")
            for cand, rec, time_slot in sorted(result):
                print(f"  - {cand} with {rec} at {time_slot}")
            
            results[method_name] = result
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return results

def main():
    # Test Case 1: Basic Matching
    candidates1 = {
   "Alice": {"availability": ["2025-04-01 09:00-10:00", "2025-04-01 13:00-14:00"], "timezone": "EST"},
   "Bob": {"availability": ["2025-04-01 09:30-10:30"], "timezone": "EST"},
}
    recruiters1 = {
   "R1": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "EST"},
   "R2": {"availability": ["2025-04-01 13:00-14:00", "2025-04-01 09:30-10:30"], "timezone": "EST"},
}
    slot_length1 = 30
    max_cand_interviews1 = 2
    max_rec_interviews1 = 2
    
    # Test Case 2: Cross Timezone Matching
    candidates2 = {
   "Charlie": {"availability": ["2025-04-01 12:00-13:00"], "timezone": "EST"},  # 9:00-10:00 PST
   "David": {"availability": ["2025-04-01 14:00-15:00"], "timezone": "EST"},    # 11:00-12:00 PST
}
   
    recruiters2 = {
   "R3": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "PST"},  # 12:00-13:00 EST
   "R4": {"availability": ["2025-04-01 11:00-12:00"], "timezone": "PST"},  # 14:00-15:00 EST
}

    slot_length2 = 30
    max_cand_interviews2 = 1
    max_rec_interviews2 = 1
    
    # Test Case 3: High Competition Scenario
    candidates3 = {
        "Alice": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "EST"},
        "Bob": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "EST"},
        "Charlie": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "EST"},
    }
    recruiters3 = {
        "R1": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "EST"},
        "R2": {"availability": ["2025-04-01 09:00-10:00"], "timezone": "EST"},
    }
    slot_length3 = 30
    max_cand_interviews3 = 1
    max_rec_interviews3 = 2
    
    # Test Case 4: Multi-Date Matching
    candidates4 = {
        "Alice": {
            "availability": [
                "2025-04-01 09:00-10:00", 
                "2025-04-02 14:00-15:00"
            ], 
            "timezone": "EST"
        },
        "Bob": {
            "availability": [
                "2025-04-01 13:00-14:00", 
                "2025-04-03 09:00-10:00"
            ], 
            "timezone": "EST"
        },
    }
    recruiters4 = {
        "R1": {
            "availability": [
                "2025-04-01 09:00-10:00", 
                "2025-04-02 14:00-15:00", 
                "2025-04-03 09:00-10:00"
            ], 
            "timezone": "EST"
        },
    }
    slot_length4 = 30
    max_cand_interviews4 = 2
    max_rec_interviews4 = 3
    
    # Test Case 5: Weekend Filtering
    candidates5 = {
        "Alice": {
            "availability": [
                "2025-04-04 09:00-10:00",  # Friday
                "2025-04-05 09:00-10:00",  # Saturday
                "2025-04-06 09:00-10:00",  # Sunday
                "2025-04-07 09:00-10:00"   # Monday
            ], 
            "timezone": "EST"
        },
    }
    recruiters5 = {
        "R1": {
            "availability": [
                "2025-04-04 09:00-10:00", 
                "2025-04-05 09:00-10:00", 
                "2025-04-06 09:00-10:00", 
                "2025-04-07 09:00-10:00"
            ], 
            "timezone": "EST"
        },
    }
    slot_length5 = 30
    max_cand_interviews5 = 2
    max_rec_interviews5 = 2
    
    # Run all tests
    run_test("Basic Matching", candidates1, recruiters1, slot_length1, max_cand_interviews1, max_rec_interviews1)
    run_test("Cross Timezone Matching", candidates2, recruiters2, slot_length2, max_cand_interviews2, max_rec_interviews2)
    run_test("High Competition Scenario", candidates3, recruiters3, slot_length3, max_cand_interviews3, max_rec_interviews3)
    run_test("Multi-Date Matching", candidates4, recruiters4, slot_length4, max_cand_interviews4, max_rec_interviews4)
    run_test("Weekend Filtering", candidates5, recruiters5, slot_length5, max_cand_interviews5, max_rec_interviews5)

if __name__ == "__main__":
    main()