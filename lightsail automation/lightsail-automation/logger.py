#!/usr/bin/env python3
"""
LightSail Automation - Enhanced Logging Module
Proper logging framework with file rotation, web dashboard integration, and statistics
"""

import logging
import os
import sys
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from collections import deque
import threading
import queue


@dataclass
class SessionStats:
    """Statistics for a reading session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    book_title: str = ""
    pages_read: int = 0
    total_flips: int = 0
    questions_detected: int = 0
    questions_answered: int = 0
    questions_correct: int = 0
    questions_incorrect: int = 0
    wrong_answers: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    reading_time_seconds: float = 0.0
    average_flip_interval: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'book_title': self.book_title,
            'pages_read': self.pages_read,
            'total_flips': self.total_flips,
            'questions_detected': self.questions_detected,
            'questions_answered': self.questions_answered,
            'questions_correct': self.questions_correct,
            'questions_incorrect': self.questions_incorrect,
            'wrong_answers': self.wrong_answers,
            'errors': self.errors,
            'screenshots': self.screenshots,
            'reading_time_seconds': self.reading_time_seconds,
            'average_flip_interval': self.average_flip_interval,
            'accuracy_rate': self.questions_correct / max(1, self.questions_answered) * 100
        }


class StatsCollector:
    """Collects and manages session statistics"""
    
    def __init__(self, log_directory: str = "logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[SessionStats] = None
        self.sessions: List[SessionStats] = []
        self._lock = threading.Lock()
        
        # Real-time stats for dashboard
        self.real_time_stats = {
            'status': 'idle',
            'book': '',
            'pages_read': 0,
            'questions_answered': 0,
            'accuracy': 0.0,
            'session_duration': '0m 0s',
            'last_activity': None
        }
        
        # Load historical sessions
        self._load_historical_sessions()
    
    def start_session(self, session_id: Optional[str] = None) -> SessionStats:
        """Start a new reading session"""
        with self._lock:
            if session_id is None:
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.current_session = SessionStats(
                session_id=session_id,
                start_time=datetime.now()
            )
            
            self.real_time_stats['status'] = 'running'
            self.real_time_stats['last_activity'] = datetime.now().isoformat()
            
            return self.current_session
    
    def end_session(self) -> Optional[SessionStats]:
        """End the current session"""
        with self._lock:
            if self.current_session is None:
                return None
            
            self.current_session.end_time = datetime.now()
            self.current_session.reading_time_seconds = (
                self.current_session.end_time - self.current_session.start_time
            ).total_seconds()
            
            # Calculate average flip interval
            if self.current_session.total_flips > 1:
                self.current_session.average_flip_interval = (
                    self.current_session.reading_time_seconds / self.current_session.total_flips
                )
            
            self.sessions.append(self.current_session)
            self.real_time_stats['status'] = 'stopped'
            
            # Save session
            self._save_session(self.current_session)
            
            session = self.current_session
            self.current_session = None
            return session
    
    def update_pages_read(self, pages: int):
        """Update pages read count"""
        with self._lock:
            if self.current_session:
                self.current_session.pages_read = pages
                self.real_time_stats['pages_read'] = pages
                self.real_time_stats['last_activity'] = datetime.now().isoformat()
    
    def update_total_flips(self, flips: int):
        """Update total flips count"""
        with self._lock:
            if self.current_session:
                self.current_session.total_flips = flips
                self.real_time_stats['last_activity'] = datetime.now().isoformat()
    
    def update_book_title(self, title: str):
        """Update current book title"""
        with self._lock:
            if self.current_session:
                self.current_session.book_title = title
                self.real_time_stats['book'] = title
    
    def record_question(self, question_type: str, answered: bool = True, correct: Optional[bool] = None):
        """Record a detected question"""
        with self._lock:
            if self.current_session:
                self.current_session.questions_detected += 1
                if answered:
                    self.current_session.questions_answered += 1
                if correct is True:
                    self.current_session.questions_correct += 1
                elif correct is False:
                    self.current_session.questions_incorrect += 1
                
                # Update accuracy
                if self.current_session.questions_answered > 0:
                    accuracy = (self.current_session.questions_correct / 
                               self.current_session.questions_answered * 100)
                    self.real_time_stats['accuracy'] = round(accuracy, 1)
                
                self.real_time_stats['questions_answered'] = self.current_session.questions_answered
                self.real_time_stats['last_activity'] = datetime.now().isoformat()
    
    def record_wrong_answer(self, question_data: Dict[str, Any], wrong_answer: str, correct_answer: Optional[str] = None):
        """Record a wrong answer for learning"""
        with self._lock:
            if self.current_session:
                wrong_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'question': question_data.get('question', ''),
                    'question_type': question_data.get('type', 'unknown'),
                    'wrong_answer': wrong_answer,
                    'correct_answer': correct_answer,
                    'options': question_data.get('options', [])
                }
                self.current_session.wrong_answers.append(wrong_entry)
                self.real_time_stats['last_activity'] = datetime.now().isoformat()
    
    def record_error(self, error_type: str, message: str, screenshot: Optional[str] = None):
        """Record an error"""
        with self._lock:
            if self.current_session:
                error_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'type': error_type,
                    'message': message
                }
                self.current_session.errors.append(error_entry)
                if screenshot:
                    self.current_session.screenshots.append(screenshot)
                self.real_time_stats['last_activity'] = datetime.now().isoformat()
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time statistics for dashboard"""
        with self._lock:
            stats = self.real_time_stats.copy()
            if self.current_session:
                elapsed = datetime.now() - self.current_session.start_time
                minutes = int(elapsed.total_seconds() // 60)
                seconds = int(elapsed.total_seconds() % 60)
                stats['session_duration'] = f"{minutes}m {seconds}s"
            return stats
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent session history"""
        with self._lock:
            return [s.to_dict() for s in self.sessions[-limit:]]
    
    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """Export session history to CSV"""
        if filename is None:
            filename = f"session_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.log_directory / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if not self.sessions:
                return str(filepath)
            
            fieldnames = [
                'session_id', 'start_time', 'end_time', 'book_title',
                'pages_read', 'total_flips', 'questions_detected',
                'questions_answered', 'questions_correct', 'accuracy_rate',
                'reading_time_seconds', 'average_flip_interval'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for session in self.sessions:
                row = session.to_dict()
                writer.writerow({k: row[k] for k in fieldnames})
        
        return str(filepath)
    
    def export_to_json(self, filename: Optional[str] = None) -> str:
        """Export session history to JSON"""
        if filename is None:
            filename = f"session_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.log_directory / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([s.to_dict() for s in self.sessions], f, indent=2)
        
        return str(filepath)
    
    def _save_session(self, session: SessionStats):
        """Save individual session to file"""
        filepath = self.log_directory / f"session_{session.session_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def _load_historical_sessions(self):
        """Load historical sessions from disk"""
        try:
            for filepath in self.log_directory.glob("session_*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = SessionStats(
                        session_id=data['session_id'],
                        start_time=datetime.fromisoformat(data['start_time']),
                        end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
                        book_title=data.get('book_title', ''),
                        pages_read=data.get('pages_read', 0),
                        total_flips=data.get('total_flips', 0),
                        questions_detected=data.get('questions_detected', 0),
                        questions_answered=data.get('questions_answered', 0),
                        questions_correct=data.get('questions_correct', 0),
                        questions_incorrect=data.get('questions_incorrect', 0),
                        wrong_answers=data.get('wrong_answers', []),
                        errors=data.get('errors', []),
                        screenshots=data.get('screenshots', []),
                        reading_time_seconds=data.get('reading_time_seconds', 0.0),
                        average_flip_interval=data.get('average_flip_interval', 0.0)
                    )
                    self.sessions.append(session)
        except Exception as e:
            logging.error(f"Error loading historical sessions: {e}")


class DashboardLogger(logging.Handler):
    """Logging handler that updates dashboard stats"""
    
    def __init__(self, stats_collector: StatsCollector):
        super().__init__()
        self.stats = stats_collector
        self.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
    
    def emit(self, record):
        """Log record to stats collector"""
        if record.levelno >= logging.ERROR:
            self.stats.record_error(
                error_type=record.levelname,
                message=self.format(record)
            )


def setup_logging(
    log_level: str = "INFO",
    log_directory: str = "logs",
    console_output: bool = True,
    file_rotation: bool = True,
    backup_count: int = 7
) -> logging.Logger:
    """
    Setup enhanced logging with file rotation and console output
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_directory: Directory for log files
        console_output: Enable console output
        file_rotation: Enable file rotation
        backup_count: Number of backup log files to keep
    
    Returns:
        Configured logger instance
    """
    # Create log directory
    log_path = Path(log_directory)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger("lightsail_bot")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_rotation:
        from logging.handlers import RotatingFileHandler
        
        log_file = log_path / "lightsail_bot.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error-specific log file
        error_file = log_path / "errors.log"
        error_handler = RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str = "lightsail_bot") -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


if __name__ == "__main__":
    # Test the logging setup
    logger = setup_logging(log_level="DEBUG")
    stats = StatsCollector()
    
    # Add dashboard handler
    dashboard_handler = DashboardLogger(stats)
    logger.addHandler(dashboard_handler)
    
    # Test logging
    logger.info("Testing logging system")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test stats
    stats.start_session()
    stats.update_book_title("Test Book")
    stats.update_pages_read(5)
    stats.record_question("multiple_choice", answered=True, correct=True)
    stats.end_session()
    
    print(f"\nSession exported to: {stats.export_to_csv()}")
    print(f"Real-time stats: {stats.get_real_time_stats()}")
