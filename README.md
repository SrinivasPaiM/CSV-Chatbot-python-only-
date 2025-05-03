# CSV Chatbot

CSV Chatbot is a Python-based command-line interface (CLI) tool that allows users to interact with a CSV dataset conversationally. It uses a local language model (e.g., LLaMA 3, 2, 1B Instruct) running on LM Studio to answer questions about the dataset.

## Features
- Summarizes dataset details (columns, data types, null counts, etc.).
- Retrieves unique values, descriptive statistics, and rows with maximum/minimum values for specific columns.
- Handles approximate column name matches for user-friendly queries.
- Saves chat history to a log file.

## Requirements
- Python 3.8 or higher
- LM Studio with a compatible model (e.g., LLaMA 3, 2, 1B Instruct)
- Required Python libraries (see `requirements.txt`)

## Installation
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd CSVloc
   ```
2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure LM Studio is running with the desired model and accessible at the configured API URL.

## Usage
1. Place your CSV file in the same directory as the program and update the `CSV_PATH` variable in `csv_chatbot.py` with the file name.
2. Run the program:
   ```bash
   python csv_chatbot.py
   ```
3. Interact with the chatbot by typing your queries.

## Best Practices for Entering Prompts
To ensure the chatbot understands your queries effectively:
- Use clear and concise language.
- Mention the column name or part of it in your query. For example:
  - Instead of: "What is the average price?"
  - Use: "What is the average value in the `average farm price` column?"
- For unique values, include the word "unique" and the column name. Example:
  - "List all unique crops in the `type of crops` column."
- For maximum or minimum values, specify the column name. Example:
  - "What is the maximum value in the `yield per hectare` column?"
- Avoid overly complex or ambiguous queries.

## Example Queries
- "What is the average value in the `average farm price` column?"
- "List all unique crops in the `type of crops` column."
- "What is the minimum value in the `yield per hectare` column?"
- "Show the row with the maximum value in the `total production` column."

## Notes
- This program currently supports CLI interaction only.
- Ensure the CSV file is properly formatted and accessible.
- The chatbot uses approximate matching for column names, so minor variations in input are acceptable.

## License
This project is licensed under the MIT License.
