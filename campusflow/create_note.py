import json

def add_note_ticket(ticket_id, author, message):
    file_path = "data/tickets.json"
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error: The file was not found.")
        return

    ticket_found = False

    for item in data:
        if item.get("ticket_id") == ticket_id:
            ticket_found = True
            current_status = item.get("status")
            
            if current_status not in ["open", "in_progress"]:
                print(f"Action Denied: Cannot add notes to a ticket with '{current_status}' status.")
                return

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
            break  

    if not ticket_found:
        return f"Error: Ticket {ticket_id} not found."
    

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
        
    return f"Successfully added note {note_id_string} to Ticket {ticket_id}!"

