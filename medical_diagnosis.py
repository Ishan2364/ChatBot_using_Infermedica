import requests
import sys
import json
import os

# Replace with your Infermedica API credentials


import os

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")
API_URL = os.getenv("API_URL")




def save_medical_history(medical_history, username):
    """
    Save the user's medical history to a JSON file
    """
    if not os.path.exists('user_medical_histories'):
        os.makedirs('user_medical_histories')
    filename = f"user_medical_histories/{username.lower().replace(' ', '_')}_medical_history.json"
    try:
        with open(filename, 'w') as file:
            json.dump(medical_history, file, indent=4)
        print(f"Medical history saved successfully for {username}")
    except Exception as e:
        print(f"Error saving medical history: {e}")

def load_medical_history(username):
    """
    Load a user's medical history from a JSON file
    """
    filename = f"user_medical_histories/{username.lower().replace(' ', '_')}_medical_history.json"
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"No existing medical history found for {username}")
        return None
    except Exception as e:
        print(f"Error loading medical history: {e}")
        return None

def delete_medical_history(username):
    """
    Delete a user's medical history file
    """
    filename = f"user_medical_histories/{username.lower().replace(' ', '_')}_medical_history.json"
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Medical history for {username} has been successfully deleted.")
        else:
            print(f"No medical history found for {username}.")
    except Exception as e:
        print(f"Error deleting medical history: {e}")

def check_exit():
    """
    Provide a quick option to exit the program
    """
    exit_choice = input("Press 'E' to exit the program, or press Enter to continue: ").strip().lower()
    if exit_choice == 'e':
        print("👋 Exiting the program. Goodbye!")
        sys.exit(0)

def search_symptoms(symptom_name, age, sex):
    """
    Search for symptoms using Infermedica's /symptoms endpoint.
    """
    #check_exit()  # Added simple exit check

    headers = {
        "App-Id": APP_ID,
        "App-Key": APP_KEY,
        "Content-Type": "application/json",
    }

    params = {
        "phrase": symptom_name,
        "age.value": age,
        "sex": sex
    }

    response = requests.get(f"{API_URL}symptoms", headers=headers, params=params)

    if response.status_code == 200:
        results = response.json()
        # Filter results to find the most relevant symptom
        matching_symptoms = [
            symptom for symptom in results
            if symptom_name.lower() in symptom['name'].lower() or
               symptom_name.lower() in symptom['common_name'].lower()
        ]
        return matching_symptoms or results
    else:
        print(f"❌ Symptom Search Error: {response.status_code} - {response.text}")
        return None

def get_diagnosis(age, sex, symptoms):
    """
    Send symptoms to Infermedica API and get predicted diseases.
    """
    # check_exit()  # Added simple exit check

    headers = {
        "App-Id": APP_ID,
        "App-Key": APP_KEY,
        "Content-Type": "application/json",
    }

    data = {
        "sex": sex,
        "age": {"value": age},
        "evidence": symptoms,
    }

    response = requests.post(f"{API_URL}diagnosis", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Diagnosis Error: {response.status_code} - {response.text}")
        return None

def get_triage(age, sex, symptoms):
    """
    Get triage recommendations based on symptoms.
    """
    #heck_exit()  # Added simple exit check

    headers = {
        "App-Id": APP_ID,
        "App-Key": APP_KEY,
        "Content-Type": "application/json",
    }

    data = {
        "sex": sex,
        "age": {"value": age},
        "evidence": symptoms,
    }

    response = requests.post(f"{API_URL}triage", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Triage Error: {response.status_code} - {response.text}")
        return None

def manage_medical_history():
    """
    Allows users to view, add, update, or delete their medical history
    """
    while True:
        username = input("Enter your username: ").strip()
        existing_history = load_medical_history(username)

        if existing_history is None:
            # Initialize a new medical history if none exists
            existing_history = {
                'username': username,
                'chronic_conditions': [],
                'allergies': [],
                'medications': [],
                'previous_surgeries': [],
                'previous_predictions': []
            }
        elif 'previous_predictions' not in existing_history:
            # Add previous_predictions key if it doesn't exist
            existing_history['previous_predictions'] = []

        print("\nMedical History Options:")
        print("1. Add/Update Medical History")
        print("2. View Existing Medical History")
        print("3. Delete Medical History")
        print("4. Return to Main Menu")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            print("\nChronic Conditions:")
            existing_history['chronic_conditions'] = []
            while True:
                condition = input("Enter a chronic condition (or 'done' to finish): ").strip()
                if condition.lower() == 'done':
                    break
                existing_history['chronic_conditions'].append(condition)

            print("\nAllergies:")
            existing_history['allergies'] = []
            while True:
                allergy = input("Enter an allergy (or 'done' to finish): ").strip()
                if allergy.lower() == 'done':
                    break
                existing_history['allergies'].append(allergy)

            print("\nMedications:")
            existing_history['medications'] = []
            while True:
                medication = input("Enter a medication (or 'done' to finish): ").strip()
                if medication.lower() == 'done':
                    break
                existing_history['medications'].append(medication)

            print("\nPrevious Surgeries:")
            existing_history['previous_surgeries'] = []
            while True:
                surgery = input("Enter a previous surgery (or 'done' to finish): ").strip()
                if surgery.lower() == 'done':
                    break
                existing_history['previous_surgeries'].append(surgery)

            save = input("\nWould you like to save this medical history? (yes/no): ").lower()
            if save == 'yes':
                save_medical_history(existing_history, username)

            return existing_history, username

        elif choice == '2':
            if existing_history:
                print("\nExisting Medical History:")
                print(json.dumps(existing_history, indent=2))
                input("\nPress Enter to continue...")
            else:
                print("No existing medical history found.")

        elif choice == '3':
            confirm = input("Are you sure you want to delete your medical history? (yes/no): ").lower()
            if confirm == 'yes':
                delete_medical_history(username)
                input("Press Enter to continue...")

        elif choice == '4':
            return None, None

        else:
            print("Invalid choice. Please try again.")

def run_symptom_diagnosis(username=None):
    """
    Run the symptom diagnosis system and save results to medical history
    """
    print("🔹 Welcome to the AI Health Symptom Diagnosis Assistant 🔹")

    if not username:
        username = input("Enter your username: ").strip()

    # Load existing medical history or create a new one
    medical_history = load_medical_history(username)
    if medical_history is None:
        medical_history = {
            'username': username,
            'chronic_conditions': [],
            'allergies': [],
            'medications': [],
            'previous_surgeries': [],
            'previous_predictions': []
        }
    elif 'previous_predictions' not in medical_history:
        medical_history['previous_predictions'] = []

    # Get user input for age and sex
    while True:
        try:
            age = int(input("Enter your age: "))
            if age <= 0:
                print("❌ Age must be a positive number.")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid age.")

    sex = ""
    while sex not in ["male", "female"]:
        sex = input("Enter your sex (male/female): ").strip().lower()
        if sex not in ["male", "female"]:
            print("❌ Invalid input. Please enter 'male' or 'female'.")

    symptoms = []
    symptom_names = []  # To store human-readable symptom names

    while True:
        symptom_name = input("Enter a symptom (e.g., 'fever') or type 'done' to finish: ").strip()
        if symptom_name.lower() == "done":
            break

        # Search for the symptom ID
        symptom_results = search_symptoms(symptom_name, age, sex)

        if symptom_results and isinstance(symptom_results, list) and len(symptom_results) > 0:
            print("\nAvailable Symptoms:")
            # Display all symptoms instead of limiting them
            for i, symptom in enumerate(symptom_results, 1):
                print(f"{i}. {symptom['name']} (Common Name: {symptom['common_name']})")

            while True:
                try:
                    choice = int(input("\nSelect a symptom number (or 0 to skip): "))
                    if choice == 0:
                        break
                    if 1 <= choice <= len(symptom_results):
                        selected_symptom = symptom_results[choice-1]
                        symptom_id = selected_symptom["id"]
                        print(f"✔ Selected symptom: {selected_symptom['name']} (ID: {symptom_id})")
                        symptoms.append({"id": symptom_id, "choice_id": "present"})
                        symptom_names.append(selected_symptom['name'])
                        break
                    else:
                        print("❌ Invalid selection. Please try again.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        else:
            print(f"❌ No matching symptoms found for '{symptom_name}'.")

    if not symptoms:
        print("⚠ No symptoms provided. Returning to main menu.")
        return

    # Get diagnosis
    diagnosis = get_diagnosis(age, sex, symptoms)
    conditions = []

    if diagnosis:
        print("\n🩺 Possible Conditions:")
        for condition in diagnosis["conditions"]:
            condition_info = {
                "name": condition['name'],
                "probability": condition['probability'] * 100
            }
            conditions.append(condition_info)
            print(f"- {condition['name']} (Probability: {condition['probability'] * 100:.2f}%)")

    # Get triage recommendation
    triage = get_triage(age, sex, symptoms)
    triage_info = None

    if triage:
        print("\n🚑 Recommended Next Steps:")

        # Mapping triage levels to more descriptive recommendations
        triage_recommendations = {
            "self_care": "Your symptoms suggest you can manage this with self-care. Monitor your condition and rest.",
            "consultation": "Consider scheduling a consultation with a healthcare provider.",
            "emergency": "Seek immediate medical attention. Your symptoms may indicate a serious condition."
        }

        # Get the triage level recommendation
        triage_level = triage.get('triage_level', 'unknown')
        recommendation = triage_recommendations.get(triage_level, "Consult with a healthcare professional for guidance.")

        triage_info = {
            "level": triage_level,
            "recommendation": recommendation,
            "teleconsultation_applicable": triage.get('teleconsultation_applicable', False)
        }

        print(recommendation)

        # Additional context if available
        if triage.get('teleconsultation_applicable'):
            print("\n💻 Teleconsultation may be a convenient option for you.")

    # Create prediction record
    import datetime
    prediction = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "age": age,
        "sex": sex,
        "symptoms": symptom_names,
        "conditions": conditions,
        "triage": triage_info
    }

    # Add prediction to medical history
    medical_history['previous_predictions'].append(prediction)

    # Save updated medical history
    save_choice = input("\nWould you like to save this prediction to your medical history? (yes/no): ").lower()
    if save_choice == 'yes':
        save_medical_history(medical_history, username)
        print(f"Prediction saved to {username}'s medical history.")

def main():
    while True:
        print("\n🔹 Welcome to the AI Health Assistant 🔹")
        print("1. Manage Medical History")
        print("2. Symptom Diagnosis")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == '1':
            manage_medical_history()

        elif choice == '2':
            username = input("Enter your username: ").strip()
            run_symptom_diagnosis(username)

        elif choice == '3':
            print("👋 Exiting the program. Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()


# In[ ]:




