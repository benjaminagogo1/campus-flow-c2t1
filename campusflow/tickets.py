from campusflow.generate_id import generate_next_id
import json


def create_ticket(title, category, urgency, affected_users, priority, status, assigned_to):

    try: 
        with  open("tickets.json", "r") as file:
            data = json.load(file)

    except FileNotFoundError:
            print(f"{data} not found")
            data = []
    new_id = generate_next_id(data, prefix="T")        
            
    new_ticket_id = {
        "Id": new_id,
        "Title": title,
        "Category": category,
        "Urgency": urgency,
        "Affected_Users": affected_users,
        "Priority": priority,
        "Status": status,
        "Assisgned_to": assigned_to
    }

    data.append(new_ticket_id)

    with open("tickets.json", "w") as file:
          json.dump(data, file, indent=4)
          print(f"Successfully created ticket {new_id}")



