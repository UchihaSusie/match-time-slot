import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Use built-in zoneinfo instead of pytz
import logging
from typing import Dict, List, Tuple, Optional, Any, Set

class MessageParser:
    """Parse interview messages and extract key information"""
    
    def __init__(self, debug=False):
        """Initialize the parser"""
        # Set up logging
        self.debug = debug
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        self.logger = logging.getLogger("MessageParser")
        
        # Initialize timezone mappings
        self.timezone_mappings = {
            # North American timezone abbreviations
            "EST": "America/New_York",
            "EDT": "America/New_York",
            "CST": "America/Chicago",
            "CDT": "America/Chicago",
            "MST": "America/Denver",
            "MDT": "America/Denver",
            "PST": "America/Los_Angeles",
            "PDT": "America/Los_Angeles",
        }
        
        # Location to timezone mapping
        self.location_timezone_map = {
            "New York": "America/New_York",
            "Boston": "America/New_York",
            "Philadelphia": "America/New_York",
            "Atlanta": "America/New_York",
            "Chicago": "America/Chicago",
            "Dallas": "America/Chicago",
            "Houston": "America/Chicago",
            "Austin": "America/Chicago",
            "Denver": "America/Denver",
            "Phoenix": "America/Phoenix",
            "Salt Lake City": "America/Denver",
            "Albuquerque": "America/Denver",
            "San Francisco": "America/Los_Angeles",
            "Los Angeles": "America/Los_Angeles",
            "Seattle": "America/Los_Angeles",
            "Portland": "America/Los_Angeles"
        }
        
        # Regular expression patterns - simplified and matched with generator
        
        # Name patterns
        self.name_patterns = [
            r"My name is ([A-Z][a-z]+(?: [A-Z][a-z]+)+)",
            r"name:?\s*([A-Z][a-z]+(?: [A-Z][a-z]+)+)",
            r"Regards,\s*([A-Z][a-z]+(?: [A-Z][a-z]+)+)",
            r"Thank you,\s*([A-Z][a-z]+(?: [A-Z][a-z]+)+)",
            r"Best regards,\s*([A-Z][a-z]+(?: [A-Z][a-z]+)+)"
        ]
        
        # Email patterns
        self.email_patterns = [
            r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            r"Email:?\s*([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
            r"contact:.*?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        ]
        
        # Phone patterns
        self.phone_patterns = [
            r"(\+\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4})",
            r"Phone:?\s*(\+\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4})",
            r"contact:.*?(\+\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4})"
        ]
        
        # Role/position patterns
        self.role_patterns = [
            r"the ([A-Za-z]+(?: [A-Za-z]+){0,4}) position",
            r"for the ([A-Za-z]+(?: [A-Za-z]+){0,4}) position",
            r"Role:?\s*([A-Za-z]+(?: [A-Za-z]+){0,4})"
        ]
        
        # Company patterns
        self.company_patterns = [
            r"from ([A-Za-z0-9]+(?: [A-Za-z0-9]+){0,3})\.",
            r"from ([A-Za-z0-9]+(?: [A-Za-z0-9]+){0,3})\s",
            r"Company:?\s*([A-Za-z0-9]+(?: [A-Za-z0-9]+){0,3})",
            r"([A-Za-z0-9]+(?: [A-Za-z0-9]+){0,3})$"
        ]
        
        # Location patterns - updated to match generator format
        self.location_patterns = [
            r"Location:?\s*([A-Za-z\s,]+)",
            r"office is in ([A-Za-z\s,]+)",
            r"based in ([A-Za-z\s,]+)",
            r"located in ([A-Za-z\s,]+)(?:\s+\([A-Z]{3}\))?"
        ]
        
        # Timezone patterns - exact match with generator format
        self.timezone_patterns = [
            r"All times are in ([A-Z]{3})",
            r"My timezone is ([A-Z]{3})",
            r"Times listed are in ([A-Z]{3})",
            r"Located in .+? \(([A-Z]{3})\)"
        ]
        
        # Date-time patterns - simplified to support only generator format
        self.datetime_patterns = [
            # ISO format: 2023-06-15 10:00-11:00
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})-(\d{2}:\d{2})"
        ]
        
        # List item patterns
        self.list_item_patterns = [
            r"[-•*]\s+(.+)$",  # Bullet points
            r"\d+\.\s+(.+)$"   # Numbered items
        ]
    
    def parse_message(self, message: str) -> Dict[str, Any]:
        """Parse message to extract all relevant scheduling information"""
        # Save original message
        self.original_message = message
        
        # Initialize result dictionary
        result = {
            "name": None,
            "email": None,
            "phone": None,
            "role": None,
            "company": None,
            "education": None,
            "location": None,
            "timezone": None,
            "available_slots": [],
            "original_slots": [],
            "is_candidate": None,
            "raw_availability": []
        }
        
        # Clean message
        clean_message = self._clean_message(message)
        
        # Extract basic information
        result["name"] = self._extract_pattern(clean_message, self.name_patterns)
        result["email"] = self._extract_pattern(clean_message, self.email_patterns)
        result["phone"] = self._extract_pattern(clean_message, self.phone_patterns)
        result["role"] = self._extract_pattern(clean_message, self.role_patterns)
        result["company"] = self._extract_pattern(clean_message, self.company_patterns)
        result["location"] = self._extract_pattern(clean_message, self.location_patterns)
        
        # Extract timezone - directly use matching patterns
        timezone_match = self._extract_pattern(clean_message, self.timezone_patterns)
        
        # Normalize timezone
        if timezone_match:
            result["timezone"] = self._normalize_timezone(timezone_match)
        elif result["location"]:
            # Infer timezone from location
            result["timezone"] = self._infer_timezone_from_location(result["location"])
        else:
            # Default timezone
            result["timezone"] = "America/New_York"
            self.logger.warning("No timezone information found, defaulting to America/New_York")
        
        # Determine if this is a candidate or recruiter
        result["is_candidate"] = self._determine_is_candidate(result, clean_message)
        
        # Extract availability
        result["raw_availability"] = self._extract_availability(clean_message)
        
        # Parse datetime objects
        if result["timezone"] and result["raw_availability"]:
            result["available_slots"] = self._parse_datetime_slots(result["raw_availability"], result["timezone"])
            result["original_slots"] = [slot_str for slot_str in result["raw_availability"]]
        
        # Log debug information
        if self.debug:
            self.logger.debug(f"Parsing result: {result}")
        
        return result
    
    def _clean_message(self, message: str) -> str:
        """Clean message for parsing"""
        # Remove common email markers
        cleaned = message
        
        # Remove email subject
        if cleaned.startswith("Subject:"):
            lines = cleaned.split("\n", 2)
            if len(lines) >= 3:
                cleaned = lines[2]
        
        # Remove signatures and similar content
        cleaned = re.sub(r"^--+\s*\n.*", "", cleaned, flags=re.MULTILINE | re.DOTALL)
        
        # Replace multiple whitespace with single space
        cleaned = re.sub(r"\s+", " ", cleaned)
        
        return cleaned
    
    def _extract_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract information using regex patterns"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Return first non-empty match
                    if isinstance(match, tuple):
                        # If match is a tuple (from capture groups), join them
                        return ' '.join(m for m in match if m).strip()
                    elif match:
                        return match.strip()
        return None
    
    def _extract_availability(self, text: str) -> List[str]:
        """Extract availability information"""
        availability = []
        lines = text.split('\n')
        
        # Look for time in bullet points or numbered lists
        for line in lines:
            line = line.strip()
            if line.startswith('-'):
                # Exact match with generator format: - 2023-06-15 10:00-11:00
                match = re.search(r'- (\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}-\d{2}:\d{2})', line)
                if match:
                    availability.append(match.group(1))
                else:
                    # Try more relaxed matching
                    match = re.search(r'- (\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}-\d{2}:\d{2})', line)
                    if match:
                        availability.append(match.group(1))
                    else:
                        # Try simplest matching method
                        match = re.search(r'- (.*)', line)
                        if match and '-' in match.group(1) and re.search(r'\d{4}-\d{2}-\d{2}', match.group(1)):
                            availability.append(match.group(1))
        
        # If not enough time ranges found in the list, directly search for matching format
        if len(availability) == 0:
            pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}-\d{2}:\d{2})'
            matches = re.findall(pattern, text)
            if matches:
                availability.extend(matches)
        
        return availability
    
    def _normalize_timezone(self, timezone_str: str) -> str:
        """Normalize timezone string"""
        # Clean timezone string
        tz_clean = timezone_str.strip().upper()
        
        # Check direct mapping
        if tz_clean in self.timezone_mappings:
            return self.timezone_mappings[tz_clean]
        
        # If no match found, default to Eastern Time
        self.logger.warning(f"Could not parse timezone: {timezone_str}, defaulting to America/New_York")
        return "America/New_York"
    
    def _determine_is_candidate(self, parsed_data: Dict[str, Any], message: str) -> bool:
        """Determine if message is from candidate or recruiter"""
        # Simple rule - having company information more likely indicates recruiter
        if parsed_data["company"]:
            return False
        return True
    
    def _parse_datetime_slots(self, slot_strings: List[str], timezone: str) -> List[Tuple[datetime, datetime]]:
        """Parse datetime strings into datetime objects"""
        result = []
        
        for slot_str in slot_strings:
            try:
                # Parse different datetime formats
                datetime_tuple = self._parse_datetime_range(slot_str, timezone)
                if datetime_tuple:
                    result.append(datetime_tuple)
            except Exception as e:
                self.logger.warning(f"Error parsing datetime: {slot_str} - {e}")
        
        return result
    
    def _parse_datetime_range(self, slot_str: str, timezone: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse datetime range string into datetime object tuple"""
        # Match format: 2023-06-15 10:00-11:00
        match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})-(\d{2}:\d{2})', slot_str)
        
        if match:
            try:
                # Get timezone object
                tz_info = ZoneInfo(timezone)
                
                # Parse start time
                start_str = match.group(1)
                start_date = datetime.strptime(start_str, '%Y-%m-%d %H:%M').replace(tzinfo=tz_info)
                
                # Parse end time
                end_str = match.group(2)
                end_time = datetime.strptime(end_str, '%H:%M').time()
                end_date = datetime.combine(start_date.date(), end_time).replace(tzinfo=tz_info)
                
                return start_date, end_date
            except Exception as e:
                self.logger.warning(f"Failed to parse date range: {slot_str} - {e}")
        
        return None
    
    def _infer_timezone_from_location(self, location: str) -> str:
        """Infer timezone from location"""
        if not location:
            return "America/New_York"
        
        # Direct match
        if location in self.location_timezone_map:
            return self.location_timezone_map[location]
        
        # Partial match
        for loc, tz in self.location_timezone_map.items():
            if loc in location:
                return tz
        
        # Default timezone
        return "America/New_York"
    
    def print_parsed_data(self, parsed_data: Dict[str, Any]) -> None:
        """Print parsed data for debugging"""
        print("\n=== Parsed Message Data ===")
        print(f"Name: {parsed_data['name']}")
        print(f"Email: {parsed_data['email']}")
        print(f"Phone: {parsed_data['phone']}")
        print(f"Role: {parsed_data['role']}")
        print(f"Company: {parsed_data['company']}")
        print(f"Location: {parsed_data['location']}")
        print(f"Timezone: {parsed_data['timezone']}")
        print(f"Type: {'Candidate' if parsed_data['is_candidate'] else 'Recruiter'}")
        
        print("\nAvailable Time Slots:")
        if parsed_data['available_slots']:
            for i, (start, end) in enumerate(parsed_data['available_slots']):
                print(f"  {i+1}. {start.strftime('%Y-%m-%d %H:%M %Z')} - {end.strftime('%H:%M %Z')}")
                print(f"     Original: {parsed_data['original_slots'][i] if i < len(parsed_data['original_slots']) else 'N/A'}")
        else:
            print("  None detected")
        
        print("===========================\n")

def test_parser_with_generator(num_test_cases=5, with_noise=True):
    """Test parser integration with random generator"""
    # Import message generator
    from utils.message_generator import RandomMessageGenerator
    
    # Create instances
    generator = RandomMessageGenerator()
    parser = MessageParser(debug=True)
    
    # Generate and parse candidate messages
    print("\n=== Testing Candidate Messages ===\n")
    for i in range(num_test_cases):
        print(f"\n--- Test Case {i+1} ---")
        user_profile = generator.generate_user_profile(is_candidate=True)
        message_data = generator.generate_random_message(user_profile, with_noise)
        
        # Print original message
        print("\nOriginal Message:")
        print("----------------")
        print(message_data["message"])
        
        # Parse message
        parsed_data = parser.parse_message(message_data["message"])
        
        # Print parsed data
        parser.print_parsed_data(parsed_data)
        
        # Validation
        print("\nValidation Results:")
        print("-----------")
        correct_name = parsed_data["name"] == user_profile["name"] if parsed_data["name"] else False
        correct_email = parsed_data["email"] == user_profile["email"] if parsed_data["email"] else False
        correct_location = parsed_data["location"] == user_profile["location"] if parsed_data["location"] else False
        expected_timezone = parser._normalize_timezone(user_profile["timezone"])
        correct_timezone = parsed_data["timezone"] == expected_timezone if parsed_data["timezone"] else False
        
        print(f"Name correct: {correct_name}")
        print(f"Email correct: {correct_email}")
        print(f"Location correct: {correct_location}")
        print(f"Timezone correct: {correct_timezone}")
        print(f"  - Expected timezone: {expected_timezone}")
        print(f"  - Parsed timezone: {parsed_data['timezone']}")
        print(f"  - Location: {parsed_data['location']}")

# Example usage
if __name__ == "__main__":
    test_parser_with_generator(num_test_cases=3, with_noise=True)
