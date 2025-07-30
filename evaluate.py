#evaluate.py

import os
import json
from rouge_score import rouge_scorer
from summarizer import get_protocol_summary
#import re


#configuration: set folder paths
gold_standard_dir = "C:/Users/sion/OneDrive/Documents/internships/2025summer/TrialSage/data/golden_standard"
processed_text_dir = "C:/Users/sion/OneDrive/Documents/internships/2025summer/TrialSage/data/processed_text"
results_dir = "results/"  #folder to save final report

#helper functions for scoring

def calculate_rouge_scores(generated_text, reference_text):
    """Calculate ROUGE-L F-measure for two strings. Returns a score from 0.0 to 1.0"""

    if not generated_text or not reference_text:
        return 0.0
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(reference_text, generated_text)
    
    return scores['rougeL'].fmeasure

def calculate_list_accuracy(generated_list, reference_list):
    """Calculate a recall score: How many of the reference items were found?
        Returns 0.0 to 1.0."""
    
    if not isinstance(generated_list, list) or not isinstance(reference_list, list):
        return 0.0  #handles cases where the AI gives back the wrong format
    
    #normalize text for better matching (lowercase , no extra spaces)
    generated_set = {str(item).strip().lower() for item in generated_list}
    reference_set = {str(item).strip().lower() for item in reference_list}

    if not reference_set:
        return 1.0  #if there's nothing ot find, the score is perfect
    
    match_count = len(generated_set.intersection(reference_set))

    return match_count / len(reference_set)

#main function

def main():

    #create the results folder if it doesn't already exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    #get a list of JSON files from gold_standard folder
    gold_standard_files = [f for f in os.listdir(gold_standard_dir) if f.endswith(".json")]

    if not gold_standard_files:
        print("Error: No JSON files found in the 'data/golden_standard/' directory.")
        print("Please create at least one gold standard file to run the evaluation.")

        return
    
    print(f"--- Starting Evaluation on {len(gold_standard_files)} Document(s) ---")
    all_scores = []  #list to hold scores for each document

    #loop through each gold standard file created
    for i, gold_file in enumerate(gold_standard_files):
        base_name = os.path.splitext(gold_file)[0]
        print(f"[{i+1}/{len(gold_standard_files)}] Evaluating: {base_name}")

        #load gold standard JSON
        with open(os.path.join(gold_standard_dir, gold_file), 'r', encoding='utf-8') as f:
            gold_data = json.load(f)

        #load corresponding full protocol text file
        text_file_path = os.path.join(processed_text_dir, f"{base_name}.txt")
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                protocol_text = f.read()
        except FileNotFoundError:
            print(f"- Error: Matching text file not found at '{text_file_path}'. Skipping.")
            continue  #skip to the next file line in loop

        #get AI generated summary by calling function from summarizer.py
        generated_summary_str = get_protocol_summary(protocol_text)

        #check if API call was successful
        if not generated_summary_str:
            print(f" - Error: API failed to return a summary for {base_name}. Skipping.")
            continue

        #try to analyze the AI's text response into a JSON object
        try:
            generated_data = json.loads(generated_summary_str)
        except json.JSONDecodeError:
            print(f" - Error: API returned deformed JSON for {base_name}. Skipping.")
            continue  #skip if AI's response isn't valid JSON

        #compare and calculate scores for each section
        objective_score = calculate_rouge_scores(generated_data.get('study objective', ''), #use .get() for safety
                                                 gold_data.get('study_objective', ''))
        inclusion_score = calculate_list_accuracy(generated_data.get('inclusion_criteria', []), #use .get() for safety
                                                  gold_data.get('inclusion_criteria', []))
        exclusion_score = calculate_list_accuracy(generated_data.get('exclusion_criteria', []), #use .get() for safety
                                                  gold_data.get('exclusion_criteria', []))
        primary_endpoint_score = calculate_list_accuracy(generated_data.get('primary_endpoints', []),
                                                         gold_data.get('primary_endpoints', []))
        secondary_endpoint_score = calculate_list_accuracy(generated_data.get('secondary_endpoints', []),
                                                         gold_data.get('secondary_endpoints', []))
        #store scores for the one document in a dictionary
        doc_scores = {
            "document": base_name,
            "objective_rougeL": objective_score,
            "inclusion_accuracy": inclusion_score,
            "exclusion_accuracy": exclusion_score,
            "primary_endpoint_accuracy": primary_endpoint_score,
            "secondary_endpoint_accuracy": secondary_endpoint_score
        }
        all_scores.append(doc_scores)
        print(f" - Scored. Objective ROUGE-L: {objective_score:.2f}, Inclusion Acc: {inclusion_score:.2f}")

        #after loop, collect all scores and print final report
        if all_scores:
            avg_rouge = sum(s['objective_rougeL'] for s in all_scores) / len(all_scores)
            avg_inclusion = sum(s['inclusion_accuracy'] for s in all_scores) / len(all_scores)
            avg_exclusion = sum(s['exclusion_accuracy'] for s in all_scores) / len(all_scores)
            avg_primary = sum(s['primary_endpoint_accuracy'] for s in all_scores) / len(all_scores)
            avg_secondary = sum(s['secondary_endpoint_accuracy'] for s in all_scores) / len(all_scores)

            print("\n--- Evaluation Complete ---")
            print(f"Average ROUGE-L F-meausure (Objective): {avg_rouge:.2f}")
            print(f"Average Accuracy (Inclusion Criteria): {avg_inclusion:.2f}")
            print(f"Average Accuracy (Exclusion Criteria): {avg_exclusion:.2f}")
            print(f"Primary Endpoint Acc: {primary_endpoint_score:.2f}")
            print(f"Secondarry Endpoint Acc: {secondary_endpoint_score:.2f}")

            #Save detailed report to JSON file in results folder
            report_path = os.path.join(results_dir, "summary_report.json")
            with open(report_path, 'w') as f:
                json.dump({
                    "average_scores": {
                        "objective_rougeL": avg_rouge,
                        "inclusion_accuracy": avg_inclusion,
                        "exclusion_accuracy": avg_exclusion,
                        "primary_endpoint_accuracy": avg_primary,
                        "secondary_endpoint_accuracy": avg_secondary
                    },
                    "individual_scores": all_scores
                }, f, indent=2)
                print(f"\nDetailed report saved to {report_path}")
        else:
                print("\n--- Evaluation Finished: No documents were successfully scored." \
                "---")


#makes script runnable with python evaluate.py
if __name__ == "__main__":
    main()