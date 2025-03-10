import re
import json
import os
from datetime import datetime

# Import your existing modules
# This assumes your current code is in a file called medical_diagnosis.py
import medical_diagnosis as md

class MedicalChatbot:
    def __init__(self):
        self.current_user = None
        self.user_data = None
        self.conversation_state = "greeting"
        self.current_symptoms = []
        self.symptom_names = []
        self.age = None
        self.sex = None
        self.current_symptom_results = None
        self.conversation_history = []
        self.current_medical_category = None  # Added to track the current medical category being edited

    def save_chat_history(self):
        """Save the current conversation history to a file"""
        if not self.current_user:
            return False

        if not os.path.exists('chat_histories'):
            os.makedirs('chat_histories')

        filename = f"chat_histories/{self.current_user.lower().replace(' ', '_')}_chat_history.json"
        try:
            with open(filename, 'w') as file:
                json.dump(self.conversation_history, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving chat history: {e}")
            return False

    def process_message(self, message):
        """Process user messages and return appropriate responses"""
        # Add user message to history
        if self.current_user:
            self.conversation_history.append({"role": "user", "message": message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        # Convert message to lowercase for easier pattern matching
        message_lower = message.lower()

        # Handle different conversation states
        if self.conversation_state == "greeting":
            response = self._handle_greeting(message_lower)
        elif self.conversation_state == "get_username":
            response = self._handle_username(message)
        elif self.conversation_state == "main_menu":
            response = self._handle_main_menu(message_lower)
        elif self.conversation_state == "get_age":
            response = self._handle_age(message_lower)
        elif self.conversation_state == "get_sex":
            response = self._handle_sex(message_lower)
        elif self.conversation_state == "get_symptoms":
            response = self._handle_symptoms(message_lower)
        elif self.conversation_state == "select_symptom":
            response = self._handle_symptom_selection(message_lower)
        elif self.conversation_state == "diagnosis_complete":
            response = self._handle_post_diagnosis(message_lower)
        elif self.conversation_state == "medical_history":
            response = self._handle_medical_history(message_lower)
        else:
            response = "I'm not sure what to do next. Let's start over. How can I help you today?"
            self.conversation_state = "greeting"

        # Add bot response to history
        if self.current_user:
            self.conversation_history.append({"role": "bot", "message": response, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.save_chat_history()

        return response

    def _handle_greeting(self, message):
        """Handle initial greeting and guide user to login"""
        if any(word in message for word in ["hi", "hello", "hey", "start", "begin"]):
            self.conversation_state = "get_username"
            return "👋 Welcome to the AI Health Assistant! I can help you manage your medical history and analyze your symptoms. What's your username?"
        else:
            return "👋 Hello! I'm your AI Health Assistant. To get started, please say hi or hello."

    def _handle_username(self, message):
        """Handle username input and load user data if available"""
        username = message.strip()
        self.current_user = username

        # Try to load existing medical history
        self.user_data = md.load_medical_history(username)

        if self.user_data is None:
            welcome_msg = f"Welcome {username}! I don't see any existing medical records for you. Would you like to create a new profile or proceed directly to symptom analysis?"
            self.user_data = {
                'username': username,
                'chronic_conditions': [],
                'allergies': [],
                'medications': [],
                'previous_surgeries': [],
                'previous_predictions': []
            }
        else:
            welcome_msg = f"Welcome back, {username}! I've loaded your medical history. What would you like to do today?"

        self.conversation_state = "main_menu"
        menu = "\n1️⃣ Manage Medical History\n2️⃣ Symptom Diagnosis\n3️⃣ View Previous Diagnoses"

        return welcome_msg + menu

    def _handle_main_menu(self, message):
        """Process main menu selections"""
        if re.search(r"1|manage|history|profile", message):
            self.conversation_state = "medical_history"
            # Reset the current medical category
            self.current_medical_category = None
            return "Let's manage your medical history. What would you like to update?\n1️⃣ Chronic Conditions\n2️⃣ Allergies\n3️⃣ Medications\n4️⃣ Previous Surgeries\n5️⃣ Return to Main Menu"

        elif re.search(r"2|symptom|diagnos|check", message):
            self.conversation_state = "get_age"
            self.current_symptoms = []
            self.symptom_names = []
            return "I'll help you analyze your symptoms. First, what is your age?"

        elif re.search(r"3|view|previous|past", message):
            if not self.user_data.get('previous_predictions') or len(self.user_data['previous_predictions']) == 0:
                return "You don't have any previous diagnoses saved. Would you like to start a new symptom check?\n1️⃣ Yes, start new symptom check\n2️⃣ No, return to main menu"

            # Show the most recent diagnoses (up to 3)
            recent_diagnoses = self.user_data['previous_predictions'][-3:]
            response = "Here are your most recent diagnoses:\n\n"

            for i, diagnosis in enumerate(recent_diagnoses, 1):
                date = diagnosis.get('date', 'Unknown date')
                symptoms = ", ".join(diagnosis.get('symptoms', []))
                conditions = ", ".join([f"{c['name']} ({c['probability']:.1f}%)" for c in diagnosis.get('conditions', [][:2])])

                response += f"Diagnosis {i} ({date}):\n"
                response += f"Symptoms: {symptoms}\n"
                response += f"Top conditions: {conditions}\n\n"

            response += "What would you like to do next?\n1️⃣ Start new symptom check\n2️⃣ Return to main menu"
            return response

        else:
            return "I didn't understand your selection. Please choose one of the following:\n1️⃣ Manage Medical History\n2️⃣ Symptom Diagnosis\n3️⃣ View Previous Diagnoses"

    def _handle_age(self, message):
        """Process age input"""
        try:
            age = int(re.search(r'\d+', message).group())
            if age <= 0 or age > 120:
                return "Please enter a valid age between 1 and 120."

            self.age = age
            self.conversation_state = "get_sex"
            return "Thank you. What is your sex (male/female)?"

        except (ValueError, AttributeError):
            return "I couldn't understand the age. Please enter a number like '35' or '42'."

    def _handle_sex(self, message):
        """Process sex input"""
        if "male" in message:
            self.sex = "male"
            self.conversation_state = "get_symptoms"
            return "Now, please tell me what symptoms you're experiencing. You can enter one symptom at a time."
        elif "female" in message:
            self.sex = "female"
            self.conversation_state = "get_symptoms"
            return "Now, please tell me what symptoms you're experiencing. You can enter one symptom at a time."
        else:
            return "Please specify either 'male' or 'female' for accurate diagnostic purposes."

    def _handle_symptoms(self, message):
     """Process symptom input"""
     if message in ["done", "finished", "that's all", "complete"]:
        if not self.current_symptoms:
            return "You haven't added any symptoms yet. Please tell me what symptoms you're experiencing, or type 'cancel' to go back to the main menu."

        # Move to diagnosis
        diagnosis = md.get_diagnosis(self.age, self.sex, self.current_symptoms)
        triage = md.get_triage(self.age, self.sex, self.current_symptoms)

        response = "Based on your symptoms, here's what I found:\n\n"

        conditions = []
        if diagnosis and "conditions" in diagnosis:
            response += "🩺 Possible Conditions:\n"
            for condition in diagnosis["conditions"][:3]:  # Limit to top 3
                prob = condition['probability'] * 100
                response += f"- {condition['name']} (Probability: {prob:.1f}%)\n"
                conditions.append({
                    "name": condition['name'],
                    "probability": prob
                })

        triage_info = None
        if triage:
            response += "\n🚑 Recommended Next Steps:\n"
            triage_level = triage.get('triage_level', 'unknown')

            recommendations = {
                "self_care": "Your symptoms suggest you can manage this with self-care. Monitor your condition and rest.",
                "consultation": "Consider scheduling a consultation with a healthcare provider.",
                "emergency": "Seek immediate medical attention. Your symptoms may indicate a serious condition."
            }

            recommendation = recommendations.get(triage_level, "Consult with a healthcare professional for guidance.")
            response += recommendation + "\n"

            triage_info = {
                "level": triage_level,
                "recommendation": recommendation,
                "teleconsultation_applicable": triage.get('teleconsultation_applicable', False)
            }

            if triage.get('teleconsultation_applicable'):
                response += "\n💻 A telehealth consultation may be appropriate for your condition."

        # Create and save prediction
        prediction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "age": self.age,
            "sex": self.sex,
            "symptoms": self.symptom_names,
            "conditions": conditions,
            "triage": triage_info
        }

        # Add to user data
        self.user_data['previous_predictions'].append(prediction)

        # Ask about saving
        response += "\nWould you like me to save this diagnosis to your medical history? (yes/no)"
        self.conversation_state = "diagnosis_complete"

        return response

     elif message == "cancel":
        self.conversation_state = "main_menu"
        return "Symptom check cancelled. What would you like to do?\n1️⃣ Manage Medical History\n2️⃣ Symptom Diagnosis\n3️⃣ View Previous Diagnoses"

     else:
        # Search for the symptom
        symptom_results = md.search_symptoms(message, self.age, self.sex)

        if symptom_results and isinstance(symptom_results, list) and len(symptom_results) > 0:
            self.current_symptom_results = symptom_results

            response = "I found these matching symptoms. Please select one by number:\n"
            # Display all results instead of limiting to 5
            for i, symptom in enumerate(symptom_results, 1):
                response += f"{i}. {symptom['name']} (Common Name: {symptom['common_name']})\n"

            response += "\nOr type 'none' if none of these match your symptom."
            self.conversation_state = "select_symptom"
            return response
        else:
            return "I couldn't find any matching symptoms. Please try a different description or type 'done' if you've finished adding symptoms."
    def _handle_symptom_selection(self, message):
        """Handle symptom selection from search results"""
        if message == "none":
            self.conversation_state = "get_symptoms"
            return "No problem. Please try describing your symptom differently, or enter another symptom."

        try:
            if re.match(r'^\d+$', message):
                choice = int(message)
                if 1 <= choice <= len(self.current_symptom_results):
                    selected_symptom = self.current_symptom_results[choice-1]
                    symptom_id = selected_symptom["id"]

                    self.current_symptoms.append({"id": symptom_id, "choice_id": "present"})
                    self.symptom_names.append(selected_symptom['name'])

                    self.conversation_state = "get_symptoms"
                    return f"Added symptom: {selected_symptom['name']}. Please tell me another symptom, or type 'done' if you've entered all your symptoms."
                else:
                    return f"Please select a number between 1 and {len(self.current_symptom_results)}, or type 'none'."
            else:
                return "Please enter just the number of the symptom you want to select, or type 'none'."
        except ValueError:
            return "I didn't understand your selection. Please enter the number next to the symptom."

    def _handle_post_diagnosis(self, message):
        """Handle user response after diagnosis"""
        if message in ["yes", "y", "sure", "save"]:
            md.save_medical_history(self.user_data, self.current_user)
            self.conversation_state = "main_menu"
            return "I've saved your diagnosis to your medical history. What would you like to do next?\n1️⃣ Manage Medical History\n2️⃣ Start Another Symptom Check\n3️⃣ View Previous Diagnoses"
        else:
            self.conversation_state = "main_menu"
            return "I haven't saved this diagnosis. What would you like to do next?\n1️⃣ Manage Medical History\n2️⃣ Start Another Symptom Check\n3️⃣ View Previous Diagnoses"

    def _handle_medical_history(self, message):
        """Handle medical history management"""
        category_pattern = r"1|chronic|condition|2|allerg|3|medic|4|surg|5|return|back|main"
        add_match = re.match(r"add\s+(.+)", message)
        remove_match = re.match(r"remove\s+(.+)", message)

        # Handle category selection
        if re.search(r"1|chronic|condition", message) and not (add_match or remove_match):
            self.current_medical_category = "chronic_conditions"
            current = ", ".join(self.user_data[self.current_medical_category]) if self.user_data[self.current_medical_category] else "None"
            return f"Current Chronic Conditions: {current}\n\nTo add a condition, type 'add [condition]'\nTo remove, type 'remove [condition]'\nType 'done' when finished."

        elif re.search(r"2|allerg", message) and not (add_match or remove_match):
            self.current_medical_category = "allergies"
            current = ", ".join(self.user_data[self.current_medical_category]) if self.user_data[self.current_medical_category] else "None"
            return f"Current Allergies: {current}\n\nTo add an allergy, type 'add [allergy]'\nTo remove, type 'remove [allergy]'\nType 'done' when finished."

        elif re.search(r"3|medic", message) and not (add_match or remove_match):
            self.current_medical_category = "medications"
            current = ", ".join(self.user_data[self.current_medical_category]) if self.user_data[self.current_medical_category] else "None"
            return f"Current Medications: {current}\n\nTo add a medication, type 'add [medication]'\nTo remove, type 'remove [medication]'\nType 'done' when finished."

        elif re.search(r"4|surg", message) and not (add_match or remove_match):
            self.current_medical_category = "previous_surgeries"
            current = ", ".join(self.user_data[self.current_medical_category]) if self.user_data[self.current_medical_category] else "None"
            return f"Previous Surgeries: {current}\n\nTo add a surgery, type 'add [surgery]'\nTo remove, type 'remove [surgery]'\nType 'done' when finished."

        elif re.search(r"5|return|back|main", message) or message == "done":
            md.save_medical_history(self.user_data, self.current_user)
            self.conversation_state = "main_menu"
            return "Medical history updated and saved. What would you like to do next?\n1️⃣ Manage Medical History\n2️⃣ Symptom Diagnosis\n3️⃣ View Previous Diagnoses"

        # Check for add/remove commands
        elif add_match and self.current_medical_category:
            item = add_match.group(1).strip()
            self.user_data[self.current_medical_category].append(item)
            current = ", ".join(self.user_data[self.current_medical_category])
            category_name = self.current_medical_category.replace("_", " ").title()
            return f"Added '{item}' to {category_name}. Current list: {current}\nAdd another or type 'done'."

        elif remove_match and self.current_medical_category:
            item = remove_match.group(1).strip()
            if item in self.user_data[self.current_medical_category]:
                self.user_data[self.current_medical_category].remove(item)
                current = ", ".join(self.user_data[self.current_medical_category]) if self.user_data[self.current_medical_category] else "None"
                category_name = self.current_medical_category.replace("_", " ").title()
                return f"Removed '{item}' from {category_name}. Current list: {current}\nAdd/remove another or type 'done'."
            else:
                return f"'{item}' not found in the current category. Please try again."

        else:
            if not self.current_medical_category:
                return "Please select a category to update first:\n1️⃣ Chronic Conditions\n2️⃣ Allergies\n3️⃣ Medications\n4️⃣ Previous Surgeries\n5️⃣ Return to Main Menu"
            else:
                return "I didn't understand that command. To add an item, type 'add [item]'. To remove an item, type 'remove [item]'. Or type 'done' to finish."

# Simple function to run the chatbot in terminal for testing
def run_chatbot_terminal():
    chatbot = MedicalChatbot()
    print("🩺 Medical Diagnosis Chatbot 🩺")
    print("Type 'exit' to quit")

    # Initial greeting
    print("Chatbot: " + chatbot.process_message("hello"))

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = chatbot.process_message(user_input)
        print("Chatbot: " + response)

if __name__ == "__main__":
    run_chatbot_terminal()
