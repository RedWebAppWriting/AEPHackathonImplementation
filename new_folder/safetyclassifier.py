from langchain_ollama import OllamaLLM
import pandas as pd
import numpy as np
import concurrent.futures


#from tokenedcomments import *

llm = OllamaLLM(model="llama3.2")



def generate_response(prompt, process):

    response = process.invoke(prompt)
    return response.strip()

def get_binary_response(prompt, process):

    while True:
        # Ask the model for a binary response
        response_text = generate_response(prompt, process)
        if response_text.lower() in ["yes", "y","yes."]:
            return "YES"
        elif response_text.lower() in ["no", "n","no."]:
            return "NO"
        else:
            print(f"Received invalid response: '{response_text.lower()}'. Please try again, ONLY answer with YES or NO.")

def classify_decision_tree(value, process):

    #context_prompt = f"Analyze the following sentence for connotations and context: '{value}'."
    #context_response = generate_response(context_prompt, process)

    # Batch questions to reduce calls
    '''
    questions = [
        f"{context_response} Was high energy present? (YES/NO)",
        f"{context_response} Was there a high-energy incident? (YES/NO)",
        f"{context_response} Was a serious injury sustained? (YES/NO)",
        f"{context_response} Was a direct control present? (YES/NO)"
    ]
    '''
    questions = [
        "Was high energy present in this sentence? (YES/NO only):" + value,
         "Was there a high-energy incident in this sentence? (YES/NO only):" + value,
        "Was a serious injury sustained in this sentence? (YES/NO only):" + value,
        "Was a direct control present in this sentence? (YES/NO only):" + value
    ]




    # Get binary responses for each question
    responses = [get_binary_response(q, process) for q in questions]

    # Map responses to decision tree logic
    high_energy_present, high_energy_incident, serious_injury, direct_control = responses
    #print("ENTRY ADDED")
    if high_energy_present == "YES":
        if high_energy_incident == "YES":
            return "HSIF" if serious_injury == "YES" else "Capacity" if direct_control == "YES" else "PSIF"
        else:
            return "SUCCESS" if direct_control == "YES" else "EXPOSURE"
    else:
        return "LSIF" if serious_injury == "YES" else "Low Severity"


def LLMclassification(csvfile, textfields, outfile):


    df = (pd.read_csv(csvfile, skipinitialspace=True, usecols=textfields))
    df['combined']= df.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    dataset1 = np.array(df['combined'])

    # Load your CSV file, skip the first row
    #df = pd.read_csv('cleanedtext.csv', skiprows=1, nrows=10)
    first_column_values = dataset1.tolist()

    # Results list
    results = []


    #'''
    for i in range(10):
        value = first_column_values[i]
        classification = classify_decision_tree(value, llm)
        results.append((value, classification))
        print("Result " + str(i) +" added.")
    #'''

    #results = parallel_classification(first_column_values, process=llm)
    #results = parallel_classification(first_column_values[0:100], process=llm)



    # Create a DataFrame and save it to CSV
    results_df = pd.DataFrame(results, columns=['Original', 'Category'])
    results_df.to_csv(outfile, index=False)

    #print("Categorization completed and saved to 'categorized_sentences.csv'.")


def parallel_classification(first_column_values, process):
    results = []

    # Define a helper function to wrap the classification and handle exceptions
    def safe_classify(value):
        try:
            return classify_decision_tree(value, process)
        except Exception as e:
            print(f"Error classifying value: {value}. Error: {e}")
            return "Error"  # Return a fallback value in case of error

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(safe_classify, value): value for value in first_column_values}

        for index, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                classification = future.result(timeout=30)  # Set timeout for each task
                value = futures[future]
                results.append((value, classification))  # Append the result with value and classification
                print(f"Result {index} for value '{value}' added.")
            except concurrent.futures.TimeoutError:
                print(f"Task for value {futures[future]} timed out.")
            except Exception as e:
                print(f"Error processing value {futures[future]}: {e}")

    return results


#LLMclassification("CORE_HackOhio_subset_cleaned_downsampled 1.csv",['QUALIFIER_TXT','PNT_ATRISKNOTES_TX'],"categorized_sentences.csv")
