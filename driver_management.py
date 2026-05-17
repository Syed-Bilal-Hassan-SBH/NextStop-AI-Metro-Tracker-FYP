"""
driver_management.py
==================
NEW FILE - Comprehensive Driver Roster Management System
Contains all driver-related models, services, and API endpoints for the Metro Bus System

Features:
- Driver scheduling and assignments
- Shift planning and management
- Performance tracking
- Availability management
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

class DriverStatus(Enum):
    AVAILABLE = "available"
    ON_SHIFT = "on_shift"
    ON_BREAK = "on_break"
    OFF_DUTY = "off_duty"
    SICK_LEAVE = "sick_leave"
    VACATION = "vacation"

class ShiftType(Enum):
    MORNING = "morning"  # 6:00 - 14:00
    AFTERNOON = "afternoon"  # 14:00 - 22:00
    NIGHT = "night"  # 22:00 - 6:00
    SPLIT = "split"  # Two separate shifts
    FLEXIBLE = "flexible"

@dataclass
class Shift:
    shift_id: str
    shift_type: ShiftType
    start_time: time
    end_time: time
    route_id: str
    bus_id: Optional[str] = None
    driver_id: Optional[str] = None
    is_active: bool = False
    break_duration: int = 30  # minutes
    max_continuous_driving: int = 240  # minutes

@dataclass
class Driver:
    driver_id: str
    name: str
    license_number: str
    phone: str
    email: str
    hire_date: datetime
    status: DriverStatus = DriverStatus.AVAILABLE
    current_shift_id: Optional[str] = None
    experience_years: int = 0
    preferred_routes: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    performance_rating: float = 3.0  # 1-5 scale
    total_hours_worked: float = 0.0
    total_trips_completed: int = 0
    accidents_count: int = 0
    sick_days_used: int = 0
    vacation_days_used: int = 0
    max_weekly_hours: int = 40
    current_week_hours: float = 0.0
    
    # Performance metrics
    on_time_performance: float = 95.0  # percentage
    passenger_complaints: int = 0
    passenger_compliments: int = 0
    fuel_efficiency_score: float = 85.0  # percentage
    
    def __post_init__(self):
        if not self.preferred_routes:
            self.preferred_routes = []

@dataclass
class DriverAssignment:
    assignment_id: str
    driver_id: str
    bus_id: str
    route_id: str
    shift_id: str
    start_time: datetime
    end_time: datetime
    status: str = "scheduled"  # scheduled, active, completed, cancelled
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    notes: str = ""

class DriverRosterManager:
    """Comprehensive driver roster management system"""
    
    def __init__(self, db_manager=None, simulator=None):
        self.db_manager = db_manager
        self.simulator = simulator
        self.logger = logging.getLogger(__name__)
        
        # Storage
        self.drivers: Dict[str, Driver] = {}
        self.shifts: Dict[str, Shift] = {}
        self.assignments: Dict[str, DriverAssignment] = {}
        
        # Configuration
        self.max_daily_driving_hours = 8
        self.min_break_duration = 30  # minutes
        self.max_continuous_driving = 4  # hours
        
        # Initialize sample data
        self._initialize_sample_drivers()
        self._initialize_shift_templates()
    
    def _initialize_sample_drivers(self):
        """Create sample drivers for the system"""
        sample_drivers = [
            {
                "driver_id": "DRV001",
                "name": "Ahmed Hassan",
                "license_number": "DL-2021-001",
                "phone": "+971-50-1234-567",
                "email": "ahmed.hassan@metrobus.ae",
                "experience_years": 5,
                "preferred_routes": ["FR-01", "FR-02"],
                "certifications": ["Heavy Vehicle", "Defensive Driving"],
                "performance_rating": 4.2
            },
            {
                "driver_id": "DRV002", 
                "name": "Fatima Al-Mansoori",
                "license_number": "DL-2019-045",
                "phone": "+971-50-2345-678",
                "email": "fatima.mansoori@metrobus.ae",
                "experience_years": 3,
                "preferred_routes": ["FR-03A", "FR-04"],
                "certifications": ["Heavy Vehicle", "Customer Service"],
                "performance_rating": 4.5
            },
            {
                "driver_id": "DRV003",
                "name": "Mohammed Al-Khouri",
                "license_number": "DL-2020-089",
                "phone": "+971-50-3456-789", 
                "email": "mohammed.khouri@metrobus.ae",
                "experience_years": 7,
                "preferred_routes": ["FR-05", "FR-06"],
                "certifications": ["Heavy Vehicle", "Emergency Response"],
                "performance_rating": 3.8
            },
            {
                "driver_id": "DRV004",
                "name": "Sarah Johnson",
                "license_number": "DL-2021-123",
                "phone": "+971-50-4567-890",
                "email": "sarah.johnson@metrobus.ae", 
                "experience_years": 2,
                "preferred_routes": ["FR-07", "FR-08A"],
                "certifications": ["Heavy Vehicle"],
                "performance_rating": 4.0
            },
            {
                "driver_id": "DRV005",
                "name": "Khalid Abdulaziz",
                "license_number": "DL-2018-234",
                "phone": "+971-50-5678-901",
                "email": "khalid.abdulaziz@metrobus.ae",
                "experience_years": 10,
                "preferred_routes": ["FR-09", "FR-10"],
                "certifications": ["Heavy Vehicle", "Instructor", "Safety Officer"],
                "performance_rating": 4.7
            }
        ]
        
        for driver_data in sample_drivers:
            driver = Driver(
                driver_id=driver_data["driver_id"],
                name=driver_data["name"],
                license_number=driver_data["license_number"],
                phone=driver_data["phone"],
                email=driver_data["email"],
                hire_date=datetime.now() - timedelta(days=random.randint(365, 1825)),
                experience_years=driver_data["experience_years"],
                preferred_routes=driver_data["preferred_routes"],
                certifications=driver_data["certifications"],
                performance_rating=driver_data["performance_rating"]
            )
            self.drivers[driver.driver_id] = driver
    
    def _initialize_shift_templates(self):
        """Create standard shift templates"""
        shift_templates = [
            # Morning shifts
            Shift("SHIFT-MORN-01", ShiftType.MORNING, time(6, 0), time(14, 0), "FR-01"),
            Shift("SHIFT-MORN-02", ShiftType.MORNING, time(6, 30), time(14, 30), "FR-02"),
            Shift("SHIFT-MORN-03", ShiftType.MORNING, time(7, 0), time(15, 0), "FR-03A"),
            
            # Afternoon shifts
            Shift("SHIFT-AFT-01", ShiftType.AFTERNOON, time(14, 0), time(22, 0), "FR-01"),
            Shift("SHIFT-AFT-02", ShiftType.AFTERNOON, time(14, 30), time(22, 30), "FR-04"),
            Shift("SHIFT-AFT-03", ShiftType.AFTERNOON, time(15, 0), time(23, 0), "FR-05"),
            
            # Night shifts
            Shift("SHIFT-NIGHT-01", ShiftType.NIGHT, time(22, 0), time(6, 0), "FR-06"),
            Shift("SHIFT-NIGHT-02", ShiftType.NIGHT, time(23, 0), time(7, 0), "FR-07"),
            
            # Split shifts
            Shift("SHIFT-SPLIT-01", ShiftType.SPLIT, time(6, 0), time(10, 0), "FR-08A"),
            Shift("SHIFT-SPLIT-02", ShiftType.SPLIT, time(16, 0), time(20, 0), "FR-08B"),
        ]
        
        for shift in shift_templates:
            self.shifts[shift.shift_id] = shift
    
    def get_available_drivers(self, date: datetime = None) -> List[Driver]:
        """Get list of available drivers for a specific date"""
        if date is None:
            date = datetime.now()
        
        available = []
        for driver in self.drivers.values():
            if driver.status == DriverStatus.AVAILABLE:
                # Check if driver hasn't exceeded weekly hours
                if driver.current_week_hours < driver.max_weekly_hours:
                    available.append(driver)
        
        return sorted(available, key=lambda d: d.performance_rating, reverse=True)
    
    def assign_driver_to_shift(self, driver_id: str, shift_id: str, date: datetime = None) -> Optional[DriverAssignment]:
        """Assign a driver to a specific shift"""
        if date is None:
            date = datetime.now()
        
        driver = self.drivers.get(driver_id)
        shift = self.shifts.get(shift_id)
        
        if not driver or not shift:
            return None
        
        # Check if driver is available
        if driver.status != DriverStatus.AVAILABLE:
            self.logger.warning(f"Driver {driver_id} is not available for assignment")
            return None
        
        # Check weekly hours limit
        shift_duration = (datetime.combine(date, shift.end_time) - 
                         datetime.combine(date, shift.start_time)).total_seconds() / 3600
        
        if driver.current_week_hours + shift_duration > driver.max_weekly_hours:
            self.logger.warning(f"Driver {driver_id} would exceed weekly hours limit")
            return None
        
        # Create assignment
        assignment_id = f"ASSIGN-{date.strftime('%Y%m%d')}-{driver_id}-{shift_id}"
        assignment = DriverAssignment(
            assignment_id=assignment_id,
            driver_id=driver_id,
            bus_id="",  # Will be assigned later
            route_id=shift.route_id,
            shift_id=shift_id,
            start_time=datetime.combine(date, shift.start_time),
            end_time=datetime.combine(date, shift.end_time),
            status="scheduled"
        )
        
        # Update driver status
        driver.status = DriverStatus.ON_SHIFT
        driver.current_shift_id = shift_id
        driver.current_week_hours += shift_duration
        
        # Update shift
        shift.driver_id = driver_id
        shift.is_active = True
        
        # Store assignment
        self.assignments[assignment_id] = assignment
        
        self.logger.info(f"Assigned driver {driver_id} to shift {shift_id}")
        return assignment
    
    def release_driver_from_shift(self, driver_id: str, completion_time: datetime = None) -> bool:
        """Release driver from current shift"""
        if completion_time is None:
            completion_time = datetime.now()
        
        driver = self.drivers.get(driver_id)
        if not driver:
            return False
        
        # Find and update current assignment
        current_assignment = None
        for assignment in self.assignments.values():
            if (assignment.driver_id == driver_id and 
                assignment.status == "active"):
                current_assignment = assignment
                break
        
        if current_assignment:
            current_assignment.status = "completed"
            current_assignment.actual_end_time = completion_time
            driver.total_trips_completed += 1
        
        # Update driver status
        driver.status = DriverStatus.AVAILABLE
        driver.current_shift_id = None
        
        # Update shift
        if driver.current_shift_id:
            shift = self.shifts.get(driver.current_shift_id)
            if shift:
                shift.driver_id = None
                shift.is_active = False
        
        self.logger.info(f"Released driver {driver_id} from shift")
        return True
    
    def get_driver_performance_metrics(self, driver_id: str) -> Optional[Dict]:
        """Get comprehensive performance metrics for a driver"""
        driver = self.drivers.get(driver_id)
        if not driver:
            return None
        
        # Calculate metrics
        completed_assignments = [a for a in self.assignments.values() 
                                if a.driver_id == driver_id and a.status == "completed"]
        
        total_shifts = len(completed_assignments)
        on_time_shifts = len([a for a in completed_assignments 
                            if a.actual_start_time and 
                            abs((a.actual_start_time - a.start_time).total_seconds()) < 300])  # 5 min grace
        
        return {
            "driver_id": driver_id,
            "name": driver.name,
            "performance_rating": driver.performance_rating,
            "total_shifts_completed": total_shifts,
            "on_time_percentage": (on_time_shifts / max(total_shifts, 1)) * 100,
            "total_hours_worked": driver.total_hours_worked,
            "current_week_hours": driver.current_week_hours,
            "experience_years": driver.experience_years,
            "accidents_count": driver.accidents_count,
            "passenger_complaints": driver.passenger_complaints,
            "passenger_compliments": driver.passenger_compliments,
            "fuel_efficiency_score": driver.fuel_efficiency_score,
            "certifications": driver.certifications,
            "preferred_routes": driver.preferred_routes
        }
    
    def get_shift_coverage_report(self, date: datetime = None) -> Dict:
        """Get shift coverage report for a specific date"""
        if date is None:
            date = datetime.now()
        
        report = {
            "date": date.strftime("%Y-%m-%d"),
            "total_shifts": len(self.shifts),
            "covered_shifts": 0,
            "uncovered_shifts": 0,
            "available_drivers": len(self.get_available_drivers(date)),
            "shift_details": []
        }
        
        for shift in self.shifts.values():
            shift_status = {
                "shift_id": shift.shift_id,
                "route_id": shift.route_id,
                "shift_type": shift.shift_type.value,
                "start_time": shift.start_time.strftime("%H:%M"),
                "end_time": shift.end_time.strftime("%H:%M"),
                "driver_assigned": shift.driver_id is not None,
                "driver_name": self.drivers.get(shift.driver_id).name if shift.driver_id else None
            }
            
            if shift.driver_id:
                report["covered_shifts"] += 1
            else:
                report["uncovered_shifts"] += 1
            
            report["shift_details"].append(shift_status)
        
        return report
    
    def optimize_shift_assignments(self, date: datetime = None) -> List[DriverAssignment]:
        """Automatically optimize shift assignments based on driver preferences and performance"""
        if date is None:
            date = datetime.now()
        
        assignments = []
        available_drivers = self.get_available_drivers(date)
        
        # Sort shifts by priority (morning first, then afternoon, then night)
        sorted_shifts = sorted(self.shifts.values(), 
                             key=lambda s: (s.shift_type.value != 'morning',
                                          s.shift_type.value != 'afternoon',
                                          s.shift_type.value))
        
        for shift in sorted_shifts:
            if shift.driver_id:  # Already assigned
                continue
            
            # Find best driver for this shift
            best_driver = None
            best_score = -1
            
            for driver in available_drivers:
                if driver.status != DriverStatus.AVAILABLE:
                    continue
                
                # Calculate compatibility score
                score = 0
                
                # Route preference bonus
                if shift.route_id in driver.preferred_routes:
                    score += 10
                
                # Performance rating bonus
                score += driver.performance_rating * 2
                
                # Experience bonus
                score += driver.experience_years * 0.5
                
                # Time-based preference (some drivers prefer certain shifts)
                if shift.shift_type == ShiftType.MORNING and driver.experience_years > 3:
                    score += 2
                
                # Check availability for shift duration
                shift_duration = (datetime.combine(date, shift.end_time) - 
                                datetime.combine(date, shift.start_time)).total_seconds() / 3600
                
                if driver.current_week_hours + shift_duration > driver.max_weekly_hours:
                    continue
                
                if score > best_score:
                    best_score = score
                    best_driver = driver
            
            if best_driver:
                assignment = self.assign_driver_to_shift(best_driver.driver_id, shift.shift_id, date)
                if assignment:
                    assignments.append(assignment)
                    available_drivers.remove(best_driver)
        
        self.logger.info(f"Optimized assignments: {len(assignments)} shifts covered")
        return assignments
    
    def get_driver_schedule(self, driver_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get driver's schedule for a date range"""
        assignments = []
        
        for assignment in self.assignments.values():
            if (assignment.driver_id == driver_id and
                start_date.date() <= assignment.start_time.date() <= end_date.date()):
                
                assignments.append({
                    "assignment_id": assignment.assignment_id,
                    "date": assignment.start_time.strftime("%Y-%m-%d"),
                    "start_time": assignment.start_time.strftime("%H:%M"),
                    "end_time": assignment.end_time.strftime("%H:%M"),
                    "route_id": assignment.route_id,
                    "status": assignment.status,
                    "bus_id": assignment.bus_id
                })
        
        return sorted(assignments, key=lambda a: a["date"])
    
    def update_driver_performance(self, driver_id: str, metrics: Dict[str, Any]) -> bool:
        """Update driver performance metrics"""
        driver = self.drivers.get(driver_id)
        if not driver:
            return False
        
        # Update performance metrics
        if "on_time_performance" in metrics:
            driver.on_time_performance = metrics["on_time_performance"]
        if "passenger_complaints" in metrics:
            driver.passenger_complaints += metrics["passenger_complaints"]
        if "passenger_compliments" in metrics:
            driver.passenger_compliments += metrics["passenger_compliments"]
        if "fuel_efficiency_score" in metrics:
            driver.fuel_efficiency_score = metrics["fuel_efficiency_score"]
        if "accidents_count" in metrics:
            driver.accidents_count += metrics["accidents_count"]
        
        # Recalculate overall performance rating
        performance_factors = [
            driver.on_time_performance / 20,  # 0-5 scale
            (5 - min(driver.passenger_complaints, 5)) / 1,  # Fewer complaints is better
            min(driver.passenger_compliments, 5) / 1,  # More compliments is better
            driver.fuel_efficiency_score / 20,  # 0-5 scale
            5 - min(driver.accidents_count, 5)  # Fewer accidents is better
        ]
        
        driver.performance_rating = sum(performance_factors) / len(performance_factors)
        driver.performance_rating = max(1.0, min(5.0, driver.performance_rating))
        
        self.logger.info(f"Updated performance metrics for driver {driver_id}")
        return True
    
    def get_roster_statistics(self) -> Dict:
        """Get comprehensive roster statistics"""
        total_drivers = len(self.drivers)
        available_drivers = len([d for d in self.drivers.values() if d.status == DriverStatus.AVAILABLE])
        on_shift_drivers = len([d for d in self.drivers.values() if d.status == DriverStatus.ON_SHIFT])
        
        # Performance distribution
        excellent_drivers = len([d for d in self.drivers.values() if d.performance_rating >= 4.5])
        good_drivers = len([d for d in self.drivers.values() if 3.5 <= d.performance_rating < 4.5])
        average_drivers = len([d for d in self.drivers.values() if 2.5 <= d.performance_rating < 3.5])
        poor_drivers = len([d for d in self.drivers.values() if d.performance_rating < 2.5])
        
        # Experience distribution
        senior_drivers = len([d for d in self.drivers.values() if d.experience_years >= 5])
        experienced_drivers = len([d for d in self.drivers.values() if 2 <= d.experience_years < 5])
        junior_drivers = len([d for d in self.drivers.values() if d.experience_years < 2])
        
        return {
            "total_drivers": total_drivers,
            "available_drivers": available_drivers,
            "on_shift_drivers": on_shift_drivers,
            "off_duty_drivers": total_drivers - available_drivers - on_shift_drivers,
            "performance_distribution": {
                "excellent": excellent_drivers,
                "good": good_drivers,
                "average": average_drivers,
                "poor": poor_drivers
            },
            "experience_distribution": {
                "senior": senior_drivers,
                "experienced": experienced_drivers,
                "junior": junior_drivers
            },
            "average_performance_rating": sum(d.performance_rating for d in self.drivers.values()) / max(total_drivers, 1),
            "average_experience_years": sum(d.experience_years for d in self.drivers.values()) / max(total_drivers, 1),
            "total_shifts_today": len(self.shifts),
            "covered_shifts_today": len([s for s in self.shifts.values() if s.driver_id]),
            "shift_coverage_percentage": (len([s for s in self.shifts.values() if s.driver_id]) / max(len(self.shifts), 1)) * 100
        }
