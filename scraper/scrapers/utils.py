import re
from typing import Literal

def extract_dates(s) -> str:
		"""
		Extracts dates from a string. Example usage:
		
		>>> extract_dates("On Tuesday, July 12, 2022, the mayor of Lansdale, PA, announced the opening of the new city hall.")
		'2022-07-12'

		:param s: The string to extract dates from.
		:return: The first extracted date as a string.
		"""
		pattern = r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|" \
							r"\d{1,2}(st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4}|" \
							r"[A-Za-z]+\s+\d{1,2},\s+\d{4})"
		matches = re.findall(pattern, s)
		matches = [match[0] for match in matches]  # Extract only the full date strings

		if len(matches) == 0:
				return ""

		return matches[0]

TimeUnit = Literal["seconds", "minutes", "hours", "days", "weeks", "months", "years"]

# def convert_relative_time(relative_time_str):
# 		now = datetime.now()
		
# 		# Match the format "n unit ago"
# 		match = re.match(r"(\d+)\s*(\w+)\s*ago", relative_time_str)
# 		if not match:
# 				raise ValueError("Invalid time format")
		
# 		value, unit = int(match.group(1)), match.group(2).lower()
		
# 		unit_mapping: dict[str, TimeUnit] = {
# 				"second": "seconds",
# 				"seconds": "seconds",
# 				"minute": "minutes",
# 				"minutes": "minutes",
# 				"hour": "hours",
# 				"hours": "hours",
# 				"day": "days",
# 				"days": "days",
# 				"week": "weeks",
# 				"weeks": "weeks",
# 				"month": "months",
# 				"months": "months",
# 				"year": "years",
# 				"years": "years"
# 		}
		
# 		if unit not in unit_mapping:
# 				raise ValueError("Unsupported time unit")
		
# 		rel_unit = unit_mapping[unit]
		
# 		# Explicit branching avoids dynamic **kwargs issues:
# 		if rel_unit == "months":
# 				delta = relativedelta(months=value)
# 		elif rel_unit == "years":
# 				delta = relativedelta(years=value)
# 		elif rel_unit == "weeks":
# 				delta = relativedelta(weeks=value)
# 		elif rel_unit == "days":
# 				delta = relativedelta(days=value)
# 		elif rel_unit == "hours":
# 				delta = relativedelta(hours=value)
# 		elif rel_unit == "minutes":
# 				delta = relativedelta(minutes=value)
# 		elif rel_unit == "seconds":
# 				delta = relativedelta(seconds=value)
# 		else:
# 				raise ValueError("Unhandled time unit")

# 		return now - delta
