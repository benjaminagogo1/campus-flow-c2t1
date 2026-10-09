import json

def calculate_priority(urgency, num_affected):
    
    if urgency == "high" and num_affected >= 10:
        return "critical"
    elif urgency == "high" or num_affected >= 10:
        return "high"
    elif urgency == "medium" or num_affected >= 3:
        return "medium"  
    else:
        return "low"  
