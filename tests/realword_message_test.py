import sys
import os
# Add project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any
import random

# Import message generator and parser
from utils.message_generator import RandomMessageGenerator
from utils.message_parser import MessageParser

# Import three scheduling algorithms
from algos.networkflow import schedule_interviews as networkflow_schedule
from algos.bipartite import schedule_interviews as bipartite_schedule
from algos.greedy import greedy_schedule_interviews as greedy_schedule

def parse_messages_to_scheduling_data(messages_data):
    """
    Parse messages into the data format required for scheduling algorithms
    
    Args:
        messages_data: Dictionary containing candidate and recruiter messages
        
    Returns:
        Tuple of (candidates_dict, recruiters_dict) ready for scheduling algorithms
    """
    parser = MessageParser(debug=False)
    
    candidates = {}
    recruiters = {}
    
    # Parse candidate messages
    for candidate_data in messages_data["candidates"]:
        message = candidate_data["message"]
        parsed_data = parser.parse_message(message)
        
        if parsed_data["name"] and parsed_data["available_slots"]:
            # Format availability for scheduling algorithms
            availability = []
            for start, end in parsed_data["available_slots"]:
                slot = f"{start.strftime('%Y-%m-%d %H:%M')}-{end.strftime('%H:%M')}"
                availability.append(slot)
            
            candidates[parsed_data["name"]] = {
                "availability": availability,
                "timezone": parsed_data["timezone"]
            }
    
    # Parse recruiter messages
    for recruiter_data in messages_data["recruiters"]:
        message = recruiter_data["message"]
        parsed_data = parser.parse_message(message)
        
        if parsed_data["name"] and parsed_data["available_slots"]:
            availability = []
            for start, end in parsed_data["available_slots"]:
                slot = f"{start.strftime('%Y-%m-%d %H:%M')}-{end.strftime('%H:%M')}"
                availability.append(slot)
            
            recruiters[parsed_data["name"]] = {
                "availability": availability,
                "timezone": parsed_data["timezone"]
            }
    
    return candidates, recruiters

def run_scheduling_algorithms(candidates, recruiters, slot_length=30, 
                             max_cand_interviews=2, max_rec_interviews=3):
    """
    Run and compare the three scheduling algorithms
    
    Args:
        candidates: Dictionary of candidates with availability
        recruiters: Dictionary of recruiters with availability
        slot_length: Length of interview slot in minutes
        max_cand_interviews: Maximum interviews per candidate
        max_rec_interviews: Maximum interviews per recruiter
        
    Returns:
        Dictionary of results from each algorithm
    """
    methods = {
        "Network Flow": networkflow_schedule,
        "Bipartite": bipartite_schedule,
        "Greedy": greedy_schedule
    }
    
    results = {}
    execution_times = {}
    
    # Print scheduling parameters
    print(f"\n=== Scheduling Parameters ===")
    print(f"Number of candidates: {len(candidates)}")
    print(f"Number of recruiters: {len(recruiters)}")
    print(f"Interview duration: {slot_length} minutes")
    print(f"Maximum interviews per candidate: {max_cand_interviews}")
    print(f"Maximum interviews per recruiter: {max_rec_interviews}")
    
    # Run each algorithm
    for method_name, schedule_func in methods.items():
        print(f"\n{method_name} Method:")
        try:
            start_time = time.time()
            result = schedule_func(candidates, recruiters, slot_length, 
                                 max_cand_interviews, max_rec_interviews)
            end_time = time.time()
            execution_time = end_time - start_time
            
            results[method_name] = result
            execution_times[method_name] = execution_time
            
            print(f"Number of scheduled interviews: {len(result)}")
            print(f"Execution time: {execution_time:.4f} seconds")
            
            # Print all matches
            print("Interview scheduling details:")
            for cand, rec, time_slot in sorted(result):
                print(f"  - {cand} with {rec} at {time_slot}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            results[method_name] = []
            execution_times[method_name] = 0
    
    # Compare results
    print("\n=== Results Comparison ===")
    for method_name, result in results.items():
        print(f"{method_name}: {len(result)} interviews, {execution_times[method_name]:.4f} seconds")
    
    return results

def run_test(num_candidates=3, num_recruiters=2, use_random_params=True):
    """
    Run a complete test with random scheduling parameters
    
    Args:
        num_candidates: Number of candidates to generate
        num_recruiters: Number of recruiters to generate
        use_random_params: Whether to use randomly generated scheduling parameters
    """
    print("\n=== Starting Email Simulation Test ===")
    print(f"Generating {num_candidates} candidates and {num_recruiters} recruiters")
    
    # Generate test data
    generator = RandomMessageGenerator()
    messages = generator.generate_test_dataset(num_candidates, num_recruiters, with_noise=False)
    
    # Print generated messages
    print("\n=== Generated Candidate Messages ===")
    for i, candidate in enumerate(messages["candidates"]):
        print(f"\n--- Candidate {i+1} ---")
        print(candidate["message"])
    
    print("\n=== Generated Recruiter Messages ===")
    for i, recruiter in enumerate(messages["recruiters"]):
        print(f"\n--- Recruiter {i+1} ---")
        print(recruiter["message"])
    
    # Parse messages
    candidates, recruiters = parse_messages_to_scheduling_data(messages)
    
    print(f"\nSuccessfully parsed {len(candidates)}/{len(messages['candidates'])} candidate data")
    print(f"Successfully parsed {len(recruiters)}/{len(messages['recruiters'])} recruiter data")
    
    # Generate random scheduling parameters
    if use_random_params:
        # Randomly select interview duration (10/15/20/30/45/60 minutes)
        slot_length = random.choice([10, 15, 20, 30, 45, 60])
        
        # Randomly select maximum interviews per candidate (1-5)
        max_cand_interviews = random.randint(1, 5)
        
        # Randomly select maximum interviews per recruiter (1-5)
        max_rec_interviews = random.randint(1, 5)
        
        print("\n=== Randomly Generated Scheduling Parameters ===")
        print(f"Interview duration: {slot_length} minutes")
        print(f"Maximum interviews per candidate: {max_cand_interviews}")
        print(f"Maximum interviews per recruiter: {max_rec_interviews}")
    else:
        # Use default parameters
        slot_length = 30
        max_cand_interviews = 2
        max_rec_interviews = 3
    
    # Run scheduling algorithms
    if len(candidates) > 0 and len(recruiters) > 0:
        run_scheduling_algorithms(candidates, recruiters, 
                                 slot_length, max_cand_interviews, max_rec_interviews)
    else:
        print("Insufficient parsed data to run scheduling algorithms")

def main():
    """Main function with interactive parameter setting"""
    print("Starting message parsing and interview scheduling test...")
    
    # Get user input parameters
    try:
        print("\nPlease enter candidate and recruiter counts (press Enter for defaults):")
        num_candidates = int(input("Number of candidates [default:3]: ") or "3")
        num_recruiters = int(input("Number of recruiters [default:2]: ") or "2")
        
        # Ask whether to use random scheduling parameters
        random_params_input = input("Use random scheduling parameters? (y/n) [default:y]: ").lower() or "y"
        use_random_params = (random_params_input == "y")
        
        # Run test
        run_test(
            num_candidates=num_candidates,
            num_recruiters=num_recruiters,
            use_random_params=use_random_params
        )
    except ValueError as e:
        print(f"Input parameter error: {e}")
        print("Running test with default parameters")
        run_test()

if __name__ == "__main__":
    main()