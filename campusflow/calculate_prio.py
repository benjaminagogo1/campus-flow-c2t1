
def calculate_priority(urgency, num_affected):
    """Return 'critical', 'high', 'medium' or 'low'.

    Rules are checked in this exact order (first match wins):
      1. critical: urgency is high AND at least 10 users affected
      2. high:     urgency is high OR at least 10 users affected
      3. medium:   urgency is medium OR at least 3 users affected
      4. low:      everything else

    Contract: urgency is one of 'low', 'medium', 'high' and num_affected is a
    positive integer. Validation happens in campusflow.validation; this
    function only applies the rules and never modifies anything.
    """
    if urgency == "high" and num_affected >= 10:
        return "critical"
    elif urgency == "high" or num_affected >= 10:
        return "high"
    elif urgency == "medium" or num_affected >= 3:
        return "medium"
    else:
        return "low"
