import random
import uuid
from datetime import datetime, timedelta
import re
from typing import Dict, List, Any, Tuple, Optional

class RandomMessageGenerator:
    """
    Generates realistic interview messages, ensuring compatibility with the parser
    """
    
    def __init__(self):
        # Basic North American timezone mapping
        self.timezone_location_map = {
            "EST": ["New York", "Boston", "Philadelphia", "Atlanta"],
            "PST": ["San Francisco", "Los Angeles", "Seattle", "Portland"],
            "CST": ["Chicago", "Dallas", "Houston", "Austin"],
            "MST": ["Denver", "Phoenix", "Salt Lake City", "Albuquerque"]
        }
        
        # List of timezones
        self.timezones = list(self.timezone_location_map.keys())
        
        # Simplified timezone expressions - using formats that are easiest to parse
        self.timezone_expressions = [
            "All times are in {tz}",
            "My timezone is {tz}",
            "Times listed are in {tz}",
            "Located in {location} ({tz})"
        ]
        
        # Company names
        self.companies = [
            "Google", "Amazon", "Microsoft", "Apple", "Meta", 
            "Netflix", "Uber", "Airbnb", "Salesforce", "Adobe"
        ]
        
        # University names
        self.universities = [
            "MIT", "Stanford", "UC Berkeley", "CMU", "University of Washington",
            "Georgia Tech", "University of Illinois", "Harvard", "Caltech"
        ]
        
        # Majors
        self.majors = [
            "Computer Science", "Electrical Engineering", "Computer Engineering",
            "Software Engineering", "AI", "Machine Learning", "Data Science"
        ]
        
        # Candidate job titles
        self.candidate_roles = [
            "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
            "Frontend Engineer", "Backend Engineer", "Data Scientist", "Machine Learning Engineer"
        ]
        
        # Recruiter job titles
        self.recruiter_roles = [
            "Technical Recruiter", "HR Specialist", "Talent Acquisition Manager",
            "Engineering Manager", "Senior Engineer", "Lead Developer"
        ]
        
        # Common email domains
        self.email_domains = [
            "gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "icloud.com"
        ]
        
        # Locations directly associated with timezones
        self.locations = []
        for locations in self.timezone_location_map.values():
            self.locations.extend(locations)
        
        # Names
        self.first_names = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard",
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Susan", "Jessica",
            "Wei", "Yan", "Juan", "Priya", "Raj", "Jose", "Carlos", "Maria", "Yuki"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Rodriguez", "Martinez", "Lee", "Wang", "Kim", "Park", "Singh", "Kumar"
        ]
        
    def generate_user_profile(self, is_candidate=True):
        """Generate a user profile"""
        # First select a timezone, then choose a corresponding location
        timezone = random.choice(self.timezones)
        locations = self.timezone_location_map.get(timezone, ["Unknown Location"])
        location = random.choice(locations)
        
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate a unique ID
        user_id = str(uuid.uuid4())[:8]
        
        # Generate email
        domain = random.choice(self.email_domains)
        email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
        
        # Generate phone number
        area_code = random.randint(201, 989)
        mid = random.randint(100, 999)
        end = random.randint(1000, 9999)
        phone = f"+1 ({area_code}) {mid}-{end}"
        
        # Basic profile
        profile = {
            "id": user_id,
            "name": full_name,
            "email": email,
            "phone": phone,
            "location": location,
            "timezone": timezone,
            "is_candidate": is_candidate
        }
        
        # Role-specific information
        if is_candidate:
            # Candidate information
            role = random.choice(self.candidate_roles)
            university = random.choice(self.universities)
            major = random.choice(self.majors)
            degree = random.choice(["BS", "MS", "PhD"])
            
            profile.update({
                "role": role,
                "education": {
                    "university": university,
                    "degree": degree,
                    "major": major
                }
            })
        else:
            # Recruiter information
            company = random.choice(self.companies)
            role = random.choice(self.recruiter_roles)
            
            profile.update({
                "company": company,
                "role": role
            })
        
        return profile
    
    def generate_date_range(self, num_slots=3, days_ahead=14):
        """Generate date-time ranges, ensuring format fully matches parser expectations"""
        date_strs = []
        absolute_dates = []
        
        for _ in range(num_slots):
            # Generate random future dates (weekdays only)
            days_offset = random.randint(1, days_ahead)
            date = datetime.now() + timedelta(days=days_offset)
            
            # Adjust to weekdays
            while date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                date += timedelta(days=1)
                
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Generate business hours
            start_hour = random.randint(9, 16)  # 9 AM to 4 PM
            start_minute = random.choice([0, 30])  # Only use hour and half-hour
            
            # Interview duration typically 30 or 60 minutes
            duration_hours = random.choice([0.5, 1.0])
            
            start_time = date.replace(hour=start_hour, minute=start_minute)
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Store absolute date-time
            absolute_dates.append((start_time, end_time))
            
            # Use format that perfectly matches parser expectations: 2023-06-15 10:00-11:00
            date_str = f"{start_time.strftime('%Y-%m-%d %H:%M')}-{end_time.strftime('%H:%M')}"
            date_strs.append(date_str)
        
        return date_strs, absolute_dates
    
    def generate_timezone_expression(self, user_profile):
        """Generate clear timezone expressions, ensuring easy parsing"""
        location = user_profile.get("location", "")
        timezone = user_profile.get("timezone", "EST")
        
        # Choose a simple timezone expression template
        template = random.choice(self.timezone_expressions[:2])  # Only use the two simplest formats
        return template.format(tz=timezone, location=location)
    
    def generate_random_message(self, user_profile=None, with_noise=False):
        """Generate random messages with clear, easy-to-parse format"""
        # Generate user profile (if not provided)
        if user_profile is None:
            is_candidate = random.random() < 0.6  # 60% are candidates
            user_profile = self.generate_user_profile(is_candidate)
        
        is_candidate = user_profile.get("is_candidate", True)
        
        # Candidate template - clearly marking timezone and available times
        if is_candidate:
            templates = [
                "Subject: Interview Availability\n\nHello,\n\nMy name is {name}. I am applying for the {role} position.\n\nHere are my available times:\n\n{dates}\n\n{timezone}\n\nMy contact: {email} or {phone}.\n\nLocation: {location}\n\nThank you,\n{name}"
            ]
        else:
            # Recruiter template - similarly clearly marking timezone and times
            templates = [
                "Subject: Interview Scheduling\n\nHello,\n\nMy name is {name} from {company}. We would like to schedule an interview for the {role} position.\n\nHere are some available slots:\n\n{dates}\n\n{timezone}\n\nOur office is in {location}.\n\nPlease let me know which time works for you.\n\nBest regards,\n{name}\n{company}"
            ]
        
        template = random.choice(templates)
        
        # Generate date-time ranges
        num_slots = random.randint(2, 4)
        date_strs, _ = self.generate_date_range(num_slots)
        
        # Generate clear timezone expression
        timezone_expr = self.generate_timezone_expression(user_profile)
        
        # Prepare template variables
        template_vars = {
            "name": user_profile["name"],
            "email": user_profile["email"],
            "phone": user_profile["phone"],
            "location": user_profile.get("location", ""),
            "dates": "\n".join([f"- {d}" for d in date_strs]),
            "timezone": timezone_expr,
            "role": user_profile.get("role", "Software Engineer"),
            "company": user_profile.get("company", ""),
        }
        
        # Fill in template
        message = template.format(**template_vars)
        
        # Create metadata
        metadata = {
            "user_id": user_profile["id"],
            "name": user_profile["name"],
            "email": user_profile["email"],
            "availability": date_strs,
            "timezone": user_profile.get("timezone", "EST"),
            "location": user_profile.get("location", ""),
            "entity_type": "candidate" if is_candidate else "recruiter"
        }
        
        return {
            "message": message,
            "metadata": metadata,
            "user_profile": user_profile
        }
    
    def generate_test_dataset(self, num_candidates=5, num_recruiters=3, with_noise=False):
        """Generate test dataset"""
        dataset = {
            "candidates": [],
            "recruiters": []
        }
        
        # Generate candidate messages
        for _ in range(num_candidates):
            user_profile = self.generate_user_profile(is_candidate=True)
            dataset["candidates"].append(self.generate_random_message(user_profile, with_noise))
            
        # Generate recruiter messages
        for _ in range(num_recruiters):
            user_profile = self.generate_user_profile(is_candidate=False)
            dataset["recruiters"].append(self.generate_random_message(user_profile, with_noise))
            
        return dataset
    
    def generate_multi_thread_conversation(self, num_messages=5):
        """
        Generate a realistic multi-message conversation thread between a candidate and recruiter
        
        Args:
            num_messages: Number of messages in the conversation
            
        Returns:
            List of message dictionaries in chronological order
        """
        # Create conversation participants
        candidate = self.generate_user_profile(is_candidate=True)
        recruiter = self.generate_user_profile(is_candidate=False)
        
        conversation = []
        
        # Generate initial email (usually from recruiter)
        initial_msg = self.generate_random_message(recruiter, with_noise=True)
        
        # Add email subject
        subject = f"Interview for {candidate['role']} position at {recruiter['company']}"
        initial_msg["message"] = f"Subject: {subject}\n\n{initial_msg['message']}"
        conversation.append(initial_msg)
        
        # Generate subsequent messages
        is_candidate_turn = True
        
        for i in range(1, num_messages):
            if is_candidate_turn:
                msg = self.generate_random_message(candidate, with_noise=True)
                
                # Add references to previous message
                if random.random() < 0.8:
                    references = [
                        f"Re: {subject}\n\n",
                        f"Thanks for reaching out about the interview times. ",
                        f"Regarding the interview schedule you proposed, ",
                        f"Thank you for your email. "
                    ]
                    msg["message"] = random.choice(references) + msg["message"]
            else:
                msg = self.generate_random_message(recruiter, with_noise=True)
                
                # Add references to previous message
                if random.random() < 0.8:
                    references = [
                        f"Re: {subject}\n\n",
                        f"Thank you for your availability. ",
                        f"Based on your preferred times, ",
                        f"Thanks for getting back to me. "
                    ]
                    msg["message"] = random.choice(references) + msg["message"]
            
            conversation.append(msg)
            is_candidate_turn = not is_candidate_turn
        
        return conversation
