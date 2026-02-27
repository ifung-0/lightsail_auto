#!/usr/bin/env python3
"""
LightSail Automation - Enhanced Configuration Module
Pydantic-based configuration with validation and multi-profile support
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, ValidationError
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class NotificationType(str, Enum):
    DISCORD = "discord"
    TELEGRAM = "telegram"
    EMAIL = "email"


class NotificationConfig(BaseModel):
    """Configuration for notifications"""
    enabled: bool = Field(default=False, description="Enable notifications")
    type: NotificationType = Field(default=NotificationType.DISCORD, description="Notification type")
    webhook_url: Optional[str] = Field(default=None, description="Webhook URL for Discord/Telegram")
    bot_token: Optional[str] = Field(default=None, description="Telegram bot token")
    chat_id: Optional[str] = Field(default=None, description="Telegram chat ID")
    notify_on_complete: bool = Field(default=True, description="Notify on session completion")
    notify_on_error: bool = Field(default=True, description="Notify on errors")
    notify_on_question: bool = Field(default=False, description="Notify when questions need review")


class ScheduleConfig(BaseModel):
    """Configuration for scheduled runs"""
    enabled: bool = Field(default=False, description="Enable scheduled runs")
    start_time: Optional[str] = Field(default=None, description="Start time in HH:MM format")
    end_time: Optional[str] = Field(default=None, description="End time in HH:MM format")
    days_of_week: List[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4], description="Days 0=Monday to 6=Sunday")
    duration_minutes: int = Field(default=60, description="Session duration in minutes")


class ProfileConfig(BaseModel):
    """Configuration for a single user profile"""
    name: str = Field(default="default", description="Profile name")
    username: str = Field(default="", description="LightSail username")
    password: str = Field(default="", description="LightSail password")
    preferred_books: List[str] = Field(default_factory=list, description="List of preferred book titles")
    reading_goals: Dict[str, int] = Field(default_factory=lambda: {"daily_minutes": 30, "weekly_books": 3})


class DetectionEvasionConfig(BaseModel):
    """Configuration for detection evasion features"""
    randomize_timing: bool = Field(default=True, description="Add jitter to page flip intervals")
    timing_jitter_percent: float = Field(default=15.0, description="Percentage of jitter (e.g., 15 = ±15%)")
    human_mouse: bool = Field(default=True, description="Use curved mouse trajectories")
    random_scroll: bool = Field(default=True, description="Add random scroll behavior")
    reading_pauses: bool = Field(default=True, description="Add occasional longer pauses")
    pause_probability: float = Field(default=0.2, description="Probability of extra pause (0.0-1.0)")
    min_pause_seconds: int = Field(default=5, description="Minimum extra pause duration")
    max_pause_seconds: int = Field(default=30, description="Maximum extra pause duration")


class AIConfig(BaseModel):
    """Configuration for AI answering"""
    use_ai: bool = Field(default=True, description="Enable AI answering")
    use_openrouter: bool = Field(default=False, description="Use OpenRouter API")
    openrouter_api_key: Optional[str] = Field(default=None, description="OpenRouter API key")
    openrouter_model: str = Field(default="google/gemma-3-27b-it:free", description="OpenRouter model")
    openrouter_api_base: str = Field(default="https://api.openrouter.ai/v1", description="OpenRouter API base")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model")
    huggingface_api_key: Optional[str] = Field(default=None, description="Hugging Face API key")
    include_book_context: bool = Field(default=True, description="Include book title and context in AI prompts")
    max_context_pages: int = Field(default=3, description="Number of recent pages to include in context")


class LearningConfig(BaseModel):
    """Configuration for learning from mistakes"""
    enabled: bool = Field(default=True, description="Enable learning from wrong answers")
    store_wrong_answers: bool = Field(default=True, description="Store incorrect answers")
    max_stored_answers: int = Field(default=100, description="Maximum wrong answers to store")
    adjust_pattern_matching: bool = Field(default=True, description="Adjust pattern matching based on mistakes")


class ExportConfig(BaseModel):
    """Configuration for data export"""
    auto_export: bool = Field(default=False, description="Auto-export session data")
    export_format: str = Field(default="csv", description="Export format: csv, json, pdf")
    export_directory: str = Field(default="exports", description="Directory for exported files")


class WebDashboardConfig(BaseModel):
    """Configuration for web dashboard"""
    enabled: bool = Field(default=False, description="Enable web dashboard")
    port: int = Field(default=8765, description="Dashboard port")
    host: str = Field(default="127.0.0.1", description="Dashboard host")
    auto_open: bool = Field(default=True, description="Auto-open browser on start")


class LightSailConfig(BaseModel):
    """Main configuration model for LightSail Bot"""
    
    # Profile settings
    active_profile: str = Field(default="default", description="Active profile name")
    profiles: Dict[str, ProfileConfig] = Field(default_factory=dict, description="User profiles")
    
    # Bot behavior
    headless: bool = Field(default=False, description="Run browser in headless mode")
    page_flip_interval: int = Field(default=40, description="Base interval between page flips (seconds)")
    auto_answer_questions: bool = Field(default=True, description="Automatically answer questions")
    screenshot_on_question: bool = Field(default=True, description="Take screenshots of questions")
    screenshot_on_error: bool = Field(default=True, description="Take screenshots on errors")
    
    # Reading settings
    reading_speed_wpm: int = Field(default=200, description="Reading speed in words per minute")
    speed_reading_mode: bool = Field(default=False, description="Fast page flips for farming minutes")
    speed_flip_interval: int = Field(default=15, description="Interval in speed reading mode (seconds)")
    
    # AI and learning
    ai: AIConfig = Field(default_factory=AIConfig)
    learning: LearningConfig = Field(default_factory=LearningConfig)
    
    # Detection evasion
    evasion: DetectionEvasionConfig = Field(default_factory=DetectionEvasionConfig)
    
    # Notifications
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    
    # Scheduling
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    
    # Export and dashboard
    export: ExportConfig = Field(default_factory=ExportConfig)
    dashboard: WebDashboardConfig = Field(default_factory=WebDashboardConfig)
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    log_directory: str = Field(default="logs", description="Directory for log files")
    
    # Paths
    config_directory: str = Field(default=".", description="Directory for config and data files")
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('page_flip_interval')
    def validate_flip_interval(cls, v):
        if v < 5:
            raise ValueError("Page flip interval must be at least 5 seconds")
        if v > 300:
            raise ValueError("Page flip interval must be at most 300 seconds")
        return v

    @validator('reading_speed_wpm')
    def validate_wpm(cls, v):
        if v < 50:
            raise ValueError("Reading speed must be at least 50 WPM")
        if v > 1000:
            raise ValueError("Reading speed must be at most 1000 WPM")
        return v

    @classmethod
    def load(cls, config_path: str = "config.json") -> "LightSailConfig":
        """Load configuration from JSON file"""
        if not os.path.exists(config_path):
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle legacy config format migration
            data = cls._migrate_legacy_config(data)
            
            return cls(**data)
        except ValidationError as e:
            print(f"Configuration validation error: {e}")
            return cls()
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            return cls()

    @staticmethod
    def _migrate_legacy_config(data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate legacy config format to new structure"""
        migrated = {}
        
        # Map legacy fields to new structure
        field_mapping = {
            'username': ('profiles', 'default', 'username'),
            'password': ('profiles', 'default', 'password'),
            'preferred_book_title': ('profiles', 'default', 'preferred_books'),
            'openai_api_key': ('ai', 'openai_api_key'),
            'huggingface_api_key': ('ai', 'huggingface_api_key'),
            'use_openrouter': ('ai', 'use_openrouter'),
            'openrouter_api_key': ('ai', 'openrouter_api_key'),
            'openrouter_model': ('ai', 'openrouter_model'),
        }
        
        for old_key, new_path in field_mapping.items():
            if old_key in data:
                value = data[old_key]
                # Handle special case for preferred_book_title -> preferred_books list
                if old_key == 'preferred_book_title' and isinstance(value, str) and value:
                    value = [value]
                
                # Navigate to nested location
                target = migrated
                for key in new_path[:-1]:
                    if key not in target:
                        target[key] = {}
                    target = target[key]
                target[new_path[-1]] = value
        
        # Copy direct mappings
        direct_fields = ['headless', 'page_flip_interval', 'auto_answer_questions',
                        'screenshot_on_question', 'reading_speed_wpm', 'log_level']
        for field in direct_fields:
            if field in data:
                migrated[field] = data[field]
        
        # Merge with remaining data (for any new fields already in correct format)
        migrated.update(data)
        
        return migrated

    def save(self, config_path: str = "config.json") -> bool:
        """Save configuration to JSON file"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.dict(exclude_none=True), f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_active_profile(self) -> ProfileConfig:
        """Get the active user profile"""
        if self.active_profile not in self.profiles:
            self.profiles[self.active_profile] = ProfileConfig(name=self.active_profile)
        return self.profiles[self.active_profile]

    def get_effective_flip_interval(self) -> float:
        """Get page flip interval with evasion jitter applied"""
        import random
        base_interval = self.page_flip_interval
        
        if self.speed_reading_mode:
            base_interval = self.speed_flip_interval
        
        if self.evasion.randomize_timing:
            jitter = base_interval * (self.evasion.timing_jitter_percent / 100.0)
            return base_interval + random.uniform(-jitter, jitter)
        
        return base_interval


class ConfigWizard:
    """Interactive setup wizard for configuration"""
    
    def __init__(self):
        self.config = LightSailConfig()
    
    def run(self) -> LightSailConfig:
        """Run the interactive setup wizard"""
        print("\n" + "=" * 60)
        print("  LightSail Automation - Setup Wizard")
        print("=" * 60 + "\n")
        
        self._setup_profile()
        self._setup_bot_behavior()
        self._setup_ai()
        self._setup_evasion()
        self._setup_notifications()
        self._confirm_and_save()
        
        return self.config
    
    def _input_with_default(self, prompt: str, default: Any) -> str:
        """Get user input with a default value"""
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            return value if value else str(default)
        except EOFError:
            return str(default)
    
    def _setup_profile(self):
        """Setup user profile"""
        print("\n--- Profile Setup ---\n")
        
        profile_name = self._input_with_default("Profile name", "default")
        self.config.active_profile = profile_name
        
        if profile_name not in self.config.profiles:
            self.config.profiles[profile_name] = ProfileConfig(name=profile_name)
        
        profile = self.config.profiles[profile_name]
        
        print("\nLightSail Login:")
        print("  (Leave username/password blank for manual Google OAuth login)")
        profile.username = self._input_with_default("  Username", profile.username or "")
        profile.password = self._input_with_default("  Password", "********")
        if profile.password == "********":
            profile.password = ""  # Keep existing if not changed
        
        books = self._input_with_default("Preferred book titles (comma-separated)", "")
        if books:
            profile.preferred_books = [b.strip() for b in books.split(",")]
        
        daily_mins = int(self._input_with_default("Daily reading goal (minutes)", 30))
        profile.reading_goals["daily_minutes"] = daily_mins
    
    def _setup_bot_behavior(self):
        """Setup bot behavior settings"""
        print("\n--- Bot Behavior ---\n")
        
        self.config.headless = self._input_with_default(
            "Run in headless mode (no browser window) (true/false)", 
            str(self.config.headless).lower()
        ).lower() == "true"
        
        flip_interval = int(self._input_with_default(
            "Page flip interval (seconds, 5-300)", 
            self.config.page_flip_interval
        ))
        self.config.page_flip_interval = max(5, min(300, flip_interval))
        
        self.config.auto_answer_questions = self._input_with_default(
            "Auto-answer questions (true/false)", 
            str(self.config.auto_answer_questions).lower()
        ).lower() == "true"
        
        self.config.screenshot_on_question = self._input_with_default(
            "Take screenshots of questions (true/false)", 
            str(self.config.screenshot_on_question).lower()
        ).lower() == "true"
    
    def _setup_ai(self):
        """Setup AI configuration"""
        print("\n--- AI Configuration ---\n")
        
        self.config.ai.use_ai = self._input_with_default(
            "Enable AI answering (true/false)", 
            str(self.config.ai.use_ai).lower()
        ).lower() == "true"
        
        if self.config.ai.use_ai:
            print("\nAI Backend Options:")
            print("  1. OpenRouter (Free models available)")
            print("  2. OpenAI GPT (Requires API key)")
            print("  3. Pattern matching only (No API key)")
            
            choice = self._input_with_default("Select backend (1/2/3)", "1")
            
            if choice == "1":
                self.config.ai.use_openrouter = True
                api_key = self._input_with_default("OpenRouter API key (leave blank for free models)", "")
                if api_key:
                    self.config.ai.openrouter_api_key = api_key
                model = self._input_with_default("Model", self.config.ai.openrouter_model)
                self.config.ai.openrouter_model = model
                
            elif choice == "2":
                self.config.ai.use_openrouter = False
                api_key = self._input_with_default("OpenAI API key", "")
                if api_key:
                    self.config.ai.openai_api_key = api_key
                    
            # else: pattern matching only
    
    def _setup_evasion(self):
        """Setup detection evasion"""
        print("\n--- Detection Evasion ---\n")
        
        print("Based on LightSail's inferred tracking model:")
        print("- Randomizes timing to avoid predictable patterns")
        print("- Simulates human-like mouse movements")
        print("- Adds random scrolling behavior")
        print("- Includes occasional reading pauses\n")
        
        self.config.evasion.randomize_timing = self._input_with_default(
            "Randomize timing (true/false)", 
            str(self.config.evasion.randomize_timing).lower()
        ).lower() == "true"
        
        self.config.evasion.human_mouse = self._input_with_default(
            "Human-like mouse movements (true/false)", 
            str(self.config.evasion.human_mouse).lower()
        ).lower() == "true"
        
        self.config.evasion.reading_pauses = self._input_with_default(
            "Add reading pauses (true/false)", 
            str(self.config.evasion.reading_pauses).lower()
        ).lower() == "true"
    
    def _setup_notifications(self):
        """Setup notifications"""
        print("\n--- Notifications ---\n")
        
        enabled = self._input_with_default(
            "Enable notifications (true/false)", 
            str(self.config.notifications.enabled).lower()
        ).lower() == "true"
        
        if enabled:
            self.config.notifications.enabled = True
            print("\nNotification type:")
            print("  1. Discord webhook")
            print("  2. Telegram bot")
            
            choice = self._input_with_default("Select type (1/2)", "1")
            
            if choice == "1":
                self.config.notifications.type = NotificationType.DISCORD
                webhook = self._input_with_default("Discord webhook URL", "")
                self.config.notifications.webhook_url = webhook
            else:
                self.config.notifications.type = NotificationType.TELEGRAM
                token = self._input_with_default("Telegram bot token", "")
                chat_id = self._input_with_default("Telegram chat ID", "")
                self.config.notifications.bot_token = token
                self.config.notifications.chat_id = chat_id
    
    def _confirm_and_save(self):
        """Confirm settings and save"""
        print("\n" + "=" * 60)
        print("  Configuration Summary")
        print("=" * 60)
        
        profile = self.config.get_active_profile()
        print(f"\nProfile: {self.config.active_profile}")
        print(f"Username: {profile.username or '(manual login)'}")
        print(f"Headless: {self.config.headless}")
        print(f"Flip interval: {self.config.page_flip_interval}s")
        print(f"AI enabled: {self.config.ai.use_ai}")
        print(f"Notifications: {self.config.notifications.enabled}")
        
        save = self._input_with_default("\nSave configuration? (true/false)", "true")
        if save.lower() == "true":
            if self.config.save():
                print("\n[OK] Configuration saved to config.json")
            else:
                print("\n[ERROR] Failed to save configuration")
        else:
            print("\nConfiguration not saved")


def create_default_config() -> LightSailConfig:
    """Create a default configuration"""
    return LightSailConfig()


if __name__ == "__main__":
    wizard = ConfigWizard()
    wizard.run()
