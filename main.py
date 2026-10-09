from ticket_creation import create_ticket


print("tickect creation")
categories = ["Network", "Hardware", "Software", "Other"]
urgency = ["low", "medium", "high"]




while True:

        user_input1 = input("Enter title: ")
        clean_text = user_input1.replace(" ", "")        
        if user_input1 == "" or not clean_text.isalpha():
             print("Incorrect syntax use alphabets")
             continue
        
        user_input2 = input("Enter category: ")
        if user_input2.lower() not in [item.lower() for item in categories]:
          print("Invalid input. Please choose a valid category.")
          continue

        user_input3 = input("Enter urgency: ")
        if user_input3.lower() not in [item.lower() for item in categories]:
            print("Invalid input. Please choose a valid category.")
            continue
        try:
           user_input4 = int(input("Enter affected users: "))

           
           if user_input4 <= 0:
              print("Please enter a positive number of users (greater than 0).")
              continue
        except ValueError:
            print("only numbers")
            continue  


        user_input5 = input("Enter priority: ")   
        user_input6 = input("Enter status: ")
        user_input7 = input("Enter assigned: ")

        create_ticket(user_input1, user_input2, user_input3, user_input4, user_input5, user_input6, user_input7)
