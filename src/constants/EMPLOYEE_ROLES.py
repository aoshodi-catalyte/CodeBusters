from enum import Enum

class EmployeeRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            if value in cls._value2member_map_:
                return cls._value2member_map_[value]
        return None