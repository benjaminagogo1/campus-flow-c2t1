def add_note_ticket(tickets, ticket_id, author, message):
    
    ticket_found = False

    for item in tickets:
        if str(item.get("id")).upper() == str(ticket_id).upper():
            ticket_found = True
            current_status = item.get("status")
            
            if current_status not in ["open", "in_progress"]:
                raise ValueError(f"Cannot add notes to a ticket with '{current_status}' status.")

            if "notes" not in item:
                item["notes"] = []
            
            next_note_number = len(item["notes"]) + 1
            note_id_string = f"N{next_note_number:03d}"  
            
            full_note_id = f"{ticket_id}-{note_id_string}"
            
            new_note = {
                "note_id": full_note_id,
                "author": author,
                "message": message
            }
            
            item["notes"].append(new_note)
            return item  

    if not ticket_found:
        raise ValueError(f"Ticket {ticket_id} not found.")
