
def get_number(id_text, prefix):
    id_text = str(id_text).strip().upper()

    if not id_text.startswith(prefix.upper()):
        return None

    digits = id_text[len(prefix):]   

    if digits.isascii() and digits.isdigit():
        return int(digits)
    return None


def generate_next_id(data_list, prefix="T", width=3):

    highest = 0
    for item in data_list:
        if not isinstance(item, dict):
            continue
        number = get_number(item.get("id", ""), prefix)
        if number is not None and number > highest:
            highest = number
    return f"{prefix}{highest + 1:0{width}d}"


def next_ticket_id(tickets):
    """Convenience wrapper: the next ticket ID for a list of tickets."""
    return generate_next_id(tickets, prefix="T")