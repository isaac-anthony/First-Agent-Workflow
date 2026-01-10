#!/usr/bin/env python3
"""
Gmail Rate Limiter
Tracks email sending to prevent Gmail account locks and rate limiting.
"""

import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

class GmailRateLimiter:
    """Tracks email sending to prevent Gmail account locks."""
    
    def __init__(self):
        self.data_dir = Path("knowledge_base")
        self.data_dir.mkdir(exist_ok=True)
        self.stats_file = self.data_dir / "gmail_sending_stats.json"
        self.stats = self._load_stats()
        
        # Gmail limits (conservative to prevent blocking)
        self.DAILY_LIMIT = 400  # Conservative daily limit (under 500 to avoid issues)
        self.HOURLY_LIMIT = 50  # Conservative hourly limit (prevents throttling)
        self.MIN_DELAY_SECONDS = 10  # Minimum delay between emails (increased to prevent blocking)
        self.MAX_DELAY_SECONDS = 20  # Maximum delay for randomization
        
    def _load_stats(self):
        """Load sending statistics from file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "daily_count": 0,
            "hourly_count": 0,
            "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
            "last_reset_hour": datetime.now().strftime("%Y-%m-%d-%H"),
            "last_send_time": None
        }
    
    def _save_stats(self):
        """Save sending statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save Gmail stats: {e}")
    
    def _reset_if_needed(self):
        """Reset counters if day/hour has changed."""
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_hour = now.strftime("%Y-%m-%d-%H")
        
        # Reset daily count if new day
        if self.stats["last_reset_date"] != current_date:
            self.stats["daily_count"] = 0
            self.stats["last_reset_date"] = current_date
        
        # Reset hourly count if new hour
        if self.stats["last_reset_hour"] != current_hour:
            self.stats["hourly_count"] = 0
            self.stats["last_reset_hour"] = current_hour
    
    def can_send(self) -> tuple[bool, str]:
        """
        Check if we can send an email.
        Returns (can_send, reason_if_not)
        """
        self._reset_if_needed()
        
        # Check daily limit
        if self.stats["daily_count"] >= self.DAILY_LIMIT:
            remaining = 24 - (datetime.now() - datetime.strptime(self.stats["last_reset_date"], "%Y-%m-%d")).total_seconds() / 3600
            return False, f"Daily limit reached ({self.DAILY_LIMIT} emails/day). Reset in ~{remaining:.1f} hours."
        
        # Check hourly limit
        if self.stats["hourly_count"] >= self.HOURLY_LIMIT:
            remaining = 60 - (datetime.now() - datetime.strptime(self.stats["last_reset_hour"], "%Y-%m-%d-%H")).total_seconds() / 60
            return False, f"Hourly limit reached ({self.HOURLY_LIMIT} emails/hour). Reset in ~{remaining:.1f} minutes."
        
        return True, "OK"
    
    def record_send(self, success: bool = True):
        """Record that an email was sent."""
        self._reset_if_needed()
        
        if success:
            self.stats["daily_count"] += 1
            self.stats["hourly_count"] += 1
            self.stats["last_send_time"] = datetime.now().isoformat()
            self._save_stats()
    
    def get_delay_seconds(self) -> float:
        """Calculate delay needed before next send with randomization."""
        if not self.stats["last_send_time"]:
            # Randomize initial delay to avoid patterns
            return random.uniform(self.MIN_DELAY_SECONDS, self.MAX_DELAY_SECONDS)
        
        last_send = datetime.fromisoformat(self.stats["last_send_time"])
        elapsed = (datetime.now() - last_send).total_seconds()
        
        # If we've waited long enough, use randomized delay
        if elapsed >= self.MIN_DELAY_SECONDS:
            # Randomize delay to avoid detection patterns (10-20 seconds)
            return random.uniform(self.MIN_DELAY_SECONDS, self.MAX_DELAY_SECONDS)
        
        # Otherwise, wait the remaining time plus some randomization
        remaining = max(0, self.MIN_DELAY_SECONDS - elapsed)
        return remaining + random.uniform(0, 3)  # Add 0-3 seconds randomization
    
    def get_status(self) -> dict:
        """Get current sending status."""
        self._reset_if_needed()
        return {
            "daily_count": self.stats["daily_count"],
            "daily_limit": self.DAILY_LIMIT,
            "daily_remaining": self.DAILY_LIMIT - self.stats["daily_count"],
            "hourly_count": self.stats["hourly_count"],
            "hourly_limit": self.HOURLY_LIMIT,
            "hourly_remaining": self.HOURLY_LIMIT - self.stats["hourly_count"],
            "can_send": self.can_send()[0]
        }

