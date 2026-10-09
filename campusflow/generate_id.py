def generate_next_id(data_list, prefix="T"):
    if not data_list:
        return f"{prefix}001"
    
    existing_ids = []
    for item in data_list:
        id_str = item.get("Id", "")
        if id_str.startswith(prefix):
            num_part = int(id_str.replace(prefix, ""))
            existing_ids.append(num_part)
            
    next_num = max(existing_ids) + 1 if existing_ids else 1
    
    return f"{prefix}{next_num:03d}"
