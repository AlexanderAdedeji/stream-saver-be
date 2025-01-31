
import re

class Utils:
    @staticmethod
    def seconds_to_hms(seconds: int) -> str:
        """Convert seconds to HH:MM:SS format.
        
        Args:
            seconds: Duration in seconds (non-negative integer)
            
        Returns:
            str: Time formatted as HH:MM:SS
            
        Raises:
            ValueError: If input is negative
        """
        if seconds < 0:
            raise ValueError(f"Negative seconds not allowed: {seconds}")
            
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        return re.sub(r'[\\/*?:"<>|]', "", filename).strip()
    

utils = Utils()