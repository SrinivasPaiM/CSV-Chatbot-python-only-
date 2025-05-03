import pandas as pd
import requests
import json
import os
import difflib

# ---- CONFIG ----
CSV_PATH = "farm_production_dataset.csv"  # Replace with your actual CSV file
API_URL = "http://127.0.0.1:1234/v1/chat/completions"
SAVE_FILE = "chat_log.txt"
MODEL_NAME = "local-model"  # Leave as-is for LM Studio

# ---- LOAD CSV ----
try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# Data summary
def generate_summary():
    return {
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "nulls": df.isnull().sum().to_dict(),
        "stats": df.describe().to_dict(),
        "null_percentage": (df.isnull().sum() / len(df) * 100).to_dict()
    }

summary = generate_summary()

system_prompt = f"""You are a helpful assistant helping to explore a dataset.
Here are some details about the data:
- Columns: {summary['columns']}
- Data types: {summary['dtypes']}
- Null counts: {summary['nulls']}
- Null percentage: {summary['null_percentage']}
- Statistical Summary: {summary['stats']}
"""

history = [{"role": "system", "content": system_prompt}]

# Function to extract and match the closest column name from user input
def get_closest_column_name(input_name):
    column_names = summary["columns"]
    
    # Tokenize the user input into words
    input_tokens = input_name.lower().split()
    
    # Check for direct matches with column names
    for token in input_tokens:
        for col in column_names:
            if token in col.lower():
                print(f"🔍 Found a match for '{token}' in column: '{col}'.")
                return col

    # Fallback to finding the closest match using difflib
    closest_match = difflib.get_close_matches(input_name.lower(), [col.lower() for col in column_names], n=1, cutoff=0.6)
    if closest_match:
        matched_column = next(col for col in column_names if col.lower() == closest_match[0])
        print(f"🔍 Did you mean '{matched_column}'? Using the closest match.")
        return matched_column

    print(f"⚠️ No match found for '{input_name}'. Using the input as-is.")
    return input_name  # Return the input name if no match is found

# Function to get unique values from a specific column
def get_unique_values(column_name):
    column_name = get_closest_column_name(column_name)  # Flexible matching
    if column_name in df.columns:
        unique_values = df[column_name].unique()
        return unique_values  # Return all unique values
    else:
        return f"Column '{column_name}' not found in the dataset."

# Function to get descriptive statistics for a numeric column
def get_column_statistics(column_name):
    column_name = get_closest_column_name(column_name)  # Flexible matching
    if column_name in df.columns:
        if pd.api.types.is_numeric_dtype(df[column_name]):
            stats = df[column_name].describe()
            return stats.to_dict()
        else:
            return f"Column '{column_name}' is not numeric. Descriptive statistics are only available for numeric columns."
    else:
        return f"Column '{column_name}' not found in the dataset."

# Function to get the row with maximum value in a column
def get_max_row(column_name):
    column_name = get_closest_column_name(column_name)  # Flexible matching
    if column_name in df.columns:
        if pd.api.types.is_numeric_dtype(df[column_name]):
            max_value_row = df[df[column_name] == df[column_name].max()]
            return max_value_row
        else:
            return f"Column '{column_name}' is not numeric. Maximum value can only be determined for numeric columns."
    else:
        return f"Column '{column_name}' not found in the dataset."

# Function to get the row with minimum value in a column
def get_min_row(column_name):
    column_name = get_closest_column_name(column_name)  # Flexible matching
    if column_name in df.columns:
        if pd.api.types.is_numeric_dtype(df[column_name]):
            min_value_row = df[df[column_name] == df[column_name].min()]
            return min_value_row
        else:
            return f"Column '{column_name}' is not numeric. Minimum value can only be determined for numeric columns."
    else:
        return f"Column '{column_name}' not found in the dataset."

# Function to ask the model
def ask_model(question):
    history.append({"role": "user", "content": question})

    response = requests.post(
        API_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": MODEL_NAME,
            "messages": history,
            "temperature": 0.7,
            "max_tokens": 3000
        })
    )

    try:
        reply = response.json()['choices'][0]['message']['content']
        print(f"\n🤖 {reply}\n")
        history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print("Error parsing response:", e)
        print("Raw response:", response.text)

def save_reply(question, answer):
    with open(SAVE_FILE, "a", encoding="utf-8") as f:
        f.write(f"Q: {question}\nA: {answer}\n{'-'*40}\n")

# ---- INTERACTIVE CHAT LOOP ----
print("✅ CSV loaded. Ask me anything about it. Type 'save' to save the last response, 'exit' to quit.\n")

last_q = ""
last_a = ""

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("👋 Goodbye! Thank you for using the CSV chatbot.")
        break
    elif user_input.lower() == "save":
        if last_q and last_a:
            save_reply(last_q, last_a)
            print("💾 Response saved successfully.")
        else:
            print("⚠️ No response to save yet. Ask a question first.")
        continue
    elif "average" in user_input.lower():
        column_name = get_closest_column_name(user_input)  # Extract column name directly
        avg_stats = get_column_statistics(column_name)

        if isinstance(avg_stats, dict):
            avg_table = "\n".join([f"- {key}: {value}" for key, value in avg_stats.items()])
            last_q = user_input
            last_a = f"**Descriptive Statistics for '{column_name}':**\n{avg_table}"
        else:
            last_q = user_input
            last_a = f"🤖 {avg_stats}"

        print(f"🤖 {last_a}\n")
        continue
    elif "maximum value" in user_input.lower():
        column_name = get_closest_column_name(user_input)  # Extract column name directly
        max_row = get_max_row(column_name)

        if isinstance(max_row, pd.DataFrame) and not max_row.empty:
            max_row_output = max_row.to_string(index=False)
            last_q = user_input
            last_a = f"**Row with Maximum '{column_name}' Value:**\n{max_row_output}"
        else:
            last_q = user_input
            last_a = f"🤖 {max_row}"

        print(f"🤖 {last_a}\n")
        continue
    elif "minimum value" in user_input.lower():
        column_name = get_closest_column_name(user_input)  # Extract column name directly
        min_row = get_min_row(column_name)

        if isinstance(min_row, pd.DataFrame) and not min_row.empty:
            min_row_output = min_row.to_string(index=False)
            last_q = user_input
            last_a = f"**Row with Minimum '{column_name}' Value:**\n{min_row_output}"
        else:
            last_q = user_input
            last_a = f"🤖 {min_row}"

        print(f"🤖 {last_a}\n")
        continue
    elif "null" in user_input.lower():
        null_count = summary['nulls']
        null_count_output = "\n".join([f"- {col}: {count}" for col, count in null_count.items()])
        last_q = user_input
        last_a = f"**Null Counts for Each Column:**\n{null_count_output}"

        print(f"🤖 {last_a}\n")
        continue
    elif "unique" in user_input.lower():
        column_name = get_closest_column_name(user_input)  # Extract column name directly
        unique_values = get_unique_values(column_name)

        if isinstance(unique_values, list):
            unique_values_output = "\n".join([f"- {value}" for value in unique_values])
            last_q = user_input
            last_a = f"**Unique Values in '{column_name}':**\n{unique_values_output}"
        else:
            last_q = user_input
            last_a = f"🤖 {unique_values}"

        print(f"🤖 {last_a}\n")
        continue

    last_q = user_input
    last_a = ask_model(user_input)
