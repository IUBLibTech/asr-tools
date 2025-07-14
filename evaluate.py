#!/bin/env python3
# Run CompareTranscript to evaluate transcripts generated with various engines/models against ground-truths, and consolidate the performance data for a predefined set of files, 

import os
import logging
import subprocess
import json

def main():
    # go to the tests directory
    tests_dir = "/srv/scratch/yingfeng/tests"
    os.chdir(tests_dir)
    logging.info(f"Changed working directory to: {os.getcwd()}")

    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        filename = 'log/evaluate.log',
        filemode = 'a')
        
    engines = ["whisper", "whisperCpp", "whisperFast", "whiserpX"] 
    models = ["turbo", "large-v3", "large-v2", "medium", "medium.en", "small.en", "base.en", "tiny.en"]
    barcodes = ["40000003402619", "40000003189265", "40000003403856"];
    
    # initialize performance csv 
    title_row = ["Engine", "Model", "Total Time", "CPU Time"]
    rows = [title_row]

    # run comparison and generate performance csv for each file
    for barcode in barcodes:
        output_html = f"evaluate/{barcode}.html"
        output_csv = f"evaluate/{barcode}.csv"        
        groundtruth = f"groundtruth/{barcode}.json"        
        command_html = ["../CompareTranscripts/bin/compare_transcripts", f"--output {output_html}", groundtruth]
        command_csv = ["../CompareTranscripts/bin/compare_transcripts", f"--output {output_csv}", groundtruth]
        perform_csv = f"evaluate/{barcode}.pfm.csv"
        
        # loop through each engine-model
        for engine in engines:
            for model in models:
                # append transcript file (if exists) to comparison command
                output_dir = f"{engine}/{model}"
                transcript = f"{output_dir}/MDPI_{barcode}_01_high.json"
                # only append transcript if exists
                if os.path.exists(transcript):
                    command.append(transcript)
                
                # read performance json file (if exists) and append performance info to csv rows
                perform_json = f"{output_dir}/{barcode}.pfm.json"
                if os.path.exists(perform_json):
                    with open(perform_json, 'r') as file:
                        perform = json.load(file)
                        total_time = perform['total_time']
                        cpu_time = perform['cpu_time']                    
                        row = [engine, model, total_time, cpu_time]                
                        rows.append(row)
                    
        # run comparison command for HTML result            
        logging.info(f"Running evaluation command: {command_html}")            
        try:
            result = subprocess.run(command_html, capture_output=True, text=True, check=True)
       
            # Print the command's output
            logging.debug(f"Command output: \n{result.stdout}")
        
            # Print any errors
            if result.stderr:
                logging.error(f"Command errors: \n{result.stderr}")             
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed to execute with exception: {e}")
            logging.error(f"Stderr: {e.stderr}")
        except FileNotFoundError:
            print(f"Error: Command '{command_html[0]}' not found.")
        
        # run comparison command for CSV result            
        logging.info(f"Running evaluation command: {command_csv}")            
        try:
            result = subprocess.run(command_csv, capture_output=True, text=True, check=True)
       
            # Print the command's output
            logging.debug(f"Command output: \n{result.stdout}")
        
            # Print any errors
            if result.stderr:
                logging.error(f"Command errors: \n{result.stderr}")             
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed to execute with exception: {e}")
            logging.error(f"Stderr: {e.stderr}")
        except FileNotFoundError:
            print(f"Error: Command '{command_csv[0]}' not found.")
        
        # write performance data info csv file
        with open(perform_json, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

if __name__ == "__main__":
    main()        