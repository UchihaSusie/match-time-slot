import sys
import os
# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Use built-in zoneinfo instead of pytz
from typing import Dict, List, Tuple
import time
from collections import defaultdict

# Import the three scheduling algorithms
from algos.networkflow import schedule_interviews as networkflow_schedule
from algos.bipartite import schedule_interviews as bipartite_schedule
from algos.greedy import greedy_schedule_interviews as greedy_schedule

class TestCaseGenerator:
    def __init__(self):
        self.timezone_map = {
            "PST": "America/Los_Angeles",
            "EST": "America/New_York",
            "CST": "America/Chicago",
            "MST": "America/Denver"
        }
        self.candidate_names = [
            "Alice", "Bob", "Charlie", "David", "Emma", 
            "Frank", "Grace", "Henry", "Ivy", "Jack",
            "Kelly", "Liam", "Mia", "Noah", "Olivia"
        ]
        self.recruiter_names = [
            "R1", "R2", "R3", "R4", "R5",
            "R6", "R7", "R8", "R9", "R10"
        ]

    def generate_random_time_slot(self, date: datetime) -> str:
        """Generate a random time slot within business hours (9:00-18:00)"""
        start_hour = random.randint(9, 16)  # Latest start time is 16:00 to ensure at least 1 hour for interview
        start_minute = random.choice([0, 30])  # Only generate slots starting at the hour or half-hour
        duration_hours = random.randint(1, min(3, 18 - start_hour))  # 1-3 hour time slots
        
        start_time = date.replace(hour=start_hour, minute=start_minute)
        end_time = start_time + timedelta(hours=duration_hours)
        
        return f"{date.strftime('%Y-%m-%d')} {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"

    def generate_availability(self, num_days: int, slots_per_day: int) -> List[str]:
        """Generate availability slots for the specified number of days"""
        availability = []
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        base_date += timedelta(days=(7 - base_date.weekday()) % 7)  # Start from next Monday
        
        for day in range(num_days):
            current_date = base_date + timedelta(days=day)
            if current_date.weekday() < 5:  # Only generate slots on weekdays
                for _ in range(slots_per_day):
                    time_slot = self.generate_random_time_slot(current_date)
                    availability.append(time_slot)
        
        return sorted(availability)

    def generate_test_case(self, 
                          num_candidates: int = 5,
                          num_recruiters: int = 3,
                          num_days: int = 5,
                          max_slots_per_day: int = 2,
                          slot_length_minutes: int = 30,
                          max_interviews_per_candidate: int = 2,
                          max_interviews_per_recruiter: int = 3) -> Tuple[Dict, Dict, int, int, int]:
        """Generate a complete test case with all required parameters"""
        
        # Generate candidate data
        candidates = {}
        for i in range(num_candidates):
            candidate = f"Candidate{i+1}"
            slots_per_day = random.randint(1, max_slots_per_day)
            candidates[candidate] = {
                "availability": self.generate_availability(num_days, slots_per_day),
                "timezone": random.choice(list(self.timezone_map.keys()))
            }
        
        # Generate recruiter data
        recruiters = {}
        for i in range(num_recruiters):
            recruiter = f"Recruiter{i+1}"
            slots_per_day = random.randint(1, max_slots_per_day)
            recruiters[recruiter] = {
                "availability": self.generate_availability(num_days, slots_per_day),
                "timezone": random.choice(list(self.timezone_map.keys()))
            }
        
        return (
            candidates,
            recruiters,
            slot_length_minutes,
            max_interviews_per_candidate,
            max_interviews_per_recruiter
        )

def run_and_compare_algorithms(test_case, sample_display=10):
    """Run and compare the three algorithms with customizable result sample size"""
    methods = {
        "Network Flow": networkflow_schedule,
        "Bipartite": bipartite_schedule,
        "Greedy": greedy_schedule
    }
    
    results = {}
    execution_times = {}
    
    # Print test case information
    print(f"Number of candidates: {len(test_case[0])}")
    print(f"Number of recruiters: {len(test_case[1])}")
    print(f"Interview duration: {test_case[2]} minutes")
    print(f"Maximum interviews per candidate: {test_case[3]}")
    print(f"Maximum interviews per recruiter: {test_case[4]}")
    
    # Run each algorithm
    for method_name, schedule_func in methods.items():
        print(f"\n{method_name} Method:")
        try:
            start_time = time.time()
            result = schedule_func(*test_case)
            end_time = time.time()
            execution_time = end_time - start_time
            
            results[method_name] = result
            execution_times[method_name] = execution_time
            
            print(f"Number of scheduled interviews: {len(result)}")
            print(f"Execution time: {execution_time:.4f} seconds")
            
            # Check if constraints are satisfied
            candidate_count = defaultdict(int)
            recruiter_count = defaultdict(int)
            for cand, rec, _ in result:
                candidate_count[cand] += 1
                recruiter_count[rec] += 1
            
            max_cand_interviews = max(candidate_count.values()) if candidate_count else 0
            max_rec_interviews = max(recruiter_count.values()) if recruiter_count else 0
            
            print(f"Maximum interviews per candidate: {max_cand_interviews}/{test_case[3]}")
            print(f"Maximum interviews per recruiter: {max_rec_interviews}/{test_case[4]}")
            
            # Print a sample of matching results (up to sample_display)
            sample_results = result[:sample_display] if len(result) > sample_display else result
            print(f"Interview scheduling sample (max {sample_display}):")
            for cand, rec, time_slot in sample_results:
                print(f"  - {cand} with {rec} at {time_slot}")
            
            if len(result) > sample_display:
                print(f"  ... and {len(result) - sample_display} more matches")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            results[method_name] = []
            execution_times[method_name] = 0
    
    # Compare results
    print("\nResults Comparison:")
    for method_name, result in results.items():
        print(f"{method_name}: {len(result)} interviews, {execution_times[method_name]:.4f} seconds")
    
    return results, execution_times

def run_test_cases(num_test_cases=5, sample_display=10, 
                  min_candidates=10, max_candidates=500,
                  min_recruiters=2, max_recruiters=200):
    """
    Run multiple random test cases with customizable parameters
    
    Args:
        num_test_cases: Number of test cases to run
        sample_display: Number of sample results to display
        min_candidates: Minimum number of candidates per test case
        max_candidates: Maximum number of candidates per test case
        min_recruiters: Minimum number of recruiters per test case
        max_recruiters: Maximum number of recruiters per test case
    """
    generator = TestCaseGenerator()
    
    all_results = []
    all_times = []
    
    print(f"\nRunning {num_test_cases} test cases with:")
    print(f"- Candidates: {min_candidates} to {max_candidates}")
    print(f"- Recruiters: {min_recruiters} to {max_recruiters}")
    print(f"- Sample display size: {sample_display}")
    
    for i in range(num_test_cases):
        print(f"\n=== Test Case {i+1} ===")
        
        # Generate random test case with user-specified ranges
        candidates_count = random.randint(min_candidates, max_candidates)
        recruiters_count = random.randint(min_recruiters, max_recruiters)
        
        print(f"Generating test case with {candidates_count} candidates and {recruiters_count} recruiters...")
        
        test_case = generator.generate_test_case(
            num_candidates=candidates_count,
            num_recruiters=recruiters_count,
            num_days=random.randint(3, 5),
            max_slots_per_day=random.randint(1, 3),
            slot_length_minutes=random.choice([10, 20, 30, 45, 60]),
            max_interviews_per_candidate=random.randint(1, 3),
            max_interviews_per_recruiter=random.randint(2, 10)
        )
        
        # Run and compare algorithms
        results, times = run_and_compare_algorithms(test_case, sample_display)
        all_results.append(results)
        all_times.append(times)
    
    # Print statistics
    print("\n=== Statistics ===")
    methods = ["Network Flow", "Bipartite", "Greedy"]
    for method in methods:
        total_matches = sum(len(r.get(method, [])) for r in all_results)
        avg_matches = total_matches / num_test_cases if num_test_cases > 0 else 0
        
        valid_times = [t.get(method, 0) for t in all_times if t.get(method, 0) > 0]
        avg_time = sum(valid_times) / len(valid_times) if valid_times else 0
        
        print(f"{method}: Average matches={avg_matches:.2f}, Average execution time={avg_time:.4f} seconds")

def main():
    """Main function with user input for test parameters"""
    print("Starting random test case generation and algorithm comparison...")
    
    # Get user input for test parameters
    try:
        print("\nPlease enter test parameters (press Enter for defaults):")
        
        # Number of test cases
        num_test_cases = int(input("Number of test cases [default:3]: ") or "3")
        
        # Candidate range
        min_candidates = int(input("Minimum number of candidates [default:10]: ") or "10")
        max_candidates = int(input("Maximum number of candidates [default:500]: ") or "500")
        
        # Recruiter range
        min_recruiters = int(input("Minimum number of recruiters [default:2]: ") or "2")
        max_recruiters = int(input("Maximum number of recruiters [default:200]: ") or "200")
        
        # Sample display size
        sample_display = int(input("Number of sample results to display [default:10]: ") or "10")
        
        # Validate inputs
        if min_candidates > max_candidates:
            print("Warning: Minimum candidates exceeds maximum. Swapping values.")
            min_candidates, max_candidates = max_candidates, min_candidates
            
        if min_recruiters > max_recruiters:
            print("Warning: Minimum recruiters exceeds maximum. Swapping values.")
            min_recruiters, max_recruiters = max_recruiters, min_recruiters
        
        # Run test cases with user-specified parameters
        run_test_cases(
            num_test_cases=num_test_cases,
            sample_display=sample_display,
            min_candidates=min_candidates,
            max_candidates=max_candidates,
            min_recruiters=min_recruiters,
            max_recruiters=max_recruiters
        )
    except ValueError as e:
        print(f"Input error: {e}")
        print("Running with default parameters")
        run_test_cases(num_test_cases=3, sample_display=10)

if __name__ == "__main__":
    main()
