"""
Shared utility functions
Following Clean Code principles: Pure functions, Single Responsibility
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import hashlib

from .constants import TimeConstants


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


def get_unix_timestamp() -> float:
    """Get current Unix timestamp"""
    return time.time()


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < TimeConstants.HOUR:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < TimeConstants.DAY:
        hours = seconds / TimeConstants.HOUR
        return f"{hours:.1f}h"
    else:
        days = seconds / TimeConstants.DAY
        return f"{days:.1f}d"


def calculate_success_rate(successful: int, total: int) -> float:
    """Calculate success rate percentage"""
    if total == 0:
        return 0.0
    return (successful / total) * 100


def generate_batch_id() -> str:
    """Generate unique batch ID based on timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"batch_{timestamp}"


def generate_file_hash(file_path: Path) -> Optional[str]:
    """Generate MD5 hash of file content"""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except Exception:
        return None


def safe_get_file_size(file_path: Path) -> int:
    """Safely get file size, return 0 if error"""
    try:
        return file_path.stat().st_size
    except Exception:
        return 0


def safe_get_file_mtime(file_path: Path) -> float:
    """Safely get file modification time, return 0 if error"""
    try:
        return file_path.stat().st_mtime
    except Exception:
        return 0.0


def create_directory_if_not_exists(directory_path: Path) -> bool:
    """Create directory if it doesn't exist, return success status"""
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def safe_json_load(file_path: Path) -> Optional[Dict[str, Any]]:
    """Safely load JSON file, return None if error"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def safe_json_dump(data: Dict[str, Any], file_path: Path) -> bool:
    """Safely dump data to JSON file, return success status"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to max length with suffix"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters"""
    # Remove or replace invalid characters
    sanitized = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
    # Remove multiple spaces and trim
    sanitized = ' '.join(sanitized.split())
    return sanitized.strip()


def get_file_age_in_hours(file_path: Path) -> float:
    """Get file age in hours"""
    try:
        mtime = file_path.stat().st_mtime
        age_seconds = time.time() - mtime
        return age_seconds / TimeConstants.HOUR
    except Exception:
        return 0.0


def is_file_recent(file_path: Path, max_age_hours: float = 24) -> bool:
    """Check if file was modified within specified hours"""
    return get_file_age_in_hours(file_path) <= max_age_hours


def extract_numbers_from_string(text: str) -> List[float]:
    """Extract all numbers from a string"""
    import re
    number_pattern = r'-?\d+\.?\d*'
    matches = re.findall(number_pattern, text)
    return [float(match) for match in matches if match]


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and lowercasing"""
    if not text:
        return ""
    return ' '.join(text.strip().lower().split())


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with dict2 values taking precedence"""
    result = dict1.copy()
    result.update(dict2)
    return result


def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get nested value from dictionary using dot notation (e.g., 'user.profile.name')"""
    keys = key_path.split('.')
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def clean_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)
