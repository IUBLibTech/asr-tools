#!/usr/bin/env python
# Run CompareTranscript to evaluate transcripts generated with various engines/models against ground-truths, and consolidate the performance data for a predefined set of files, 

import os
import logging
import subprocess
import json
import csv

def main():
    # go to the tests directory
    tests_dir = "/srv/scratch/yingfeng/tests"
    os.chdir(tests_dir)

    logging.basicConfig(
        #filename = 'log/evaluate.log',
        #filemode = 'a',
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    logging.info(f"Changed working directory to: {os.getcwd()}")
        
    engines = ["whisper", "whisperCpp", "whisperFast", "whiserpX"] 
    models = ["turbo", "large-v3", "large-v2", "medium", "medium.en", "small.en", "base.en", "tiny.en"]
    barcodes = ["40000003402619", "40000003189265", "40000003403856"];
    
    # initialize performance csv 
    title_row = ["Engine", "Model", "Total Time", "CPU Time"]
    rows = [title_row]

    # run comparison and generate performance csv for each file
    for barcode in barcodes:
        output_html = f"evaluation/{barcode}.html"
        output_csv = f"evaluation/{barcode}.csv"        
        groundtruth = f"groundtruth/{barcode}.json"        
        command_html = ["../CompareTranscripts/bin/compare_transcripts", f"--output {output_html}", groundtruth]
        command_csv = ["../CompareTranscripts/bin/compare_transcripts", f"--output {output_csv}", groundtruth]
        perform_csv = f"evaluation/{barcode}.pfm.csv"
        
        # loop through each engine-model
        for engine in engines:
            for model in models:
                # append transcript file (if exists) to comparison command
                output_dir = f"{engine}/{model}"
                transcript = f"{output_dir}/MDPI_{barcode}_01_high.json"
                # only append transcript if exists
                if os.path.exists(transcript):
                    command_html.append(transcript)
                    command_csv.append(transcript)                        
                
                # read performance json file (if exists) and append performance info to csv rows
                perform_json = f"{output_dir}/{barcode}.pfm.json"
                if os.path.exists(perform_json):
                    logging.info(f"Reading performance info from file {perform_json}")
                    with open(perform_json, 'r') as file:
                        perform = json.load(file)
                        total_time = perform['total_time']
                        cpu_time = perform['cpu_time']                    
                        row = [engine, model, total_time, cpu_time]                
                        rows.append(row)
                    
        # run comparison command for HTML result  
        if len(command_html) < 4:
            logging.info(f"No transcript has been generated for {barcode}, skip compare_transcripts for html output.")
        else:        
            logging.info(f"Running compare_transcripts command for html output: {command_html}")            
            try:
                result = subprocess.run(command_html, capture_output=True, text=True, check=True)
           
                # Print the command's output
                logging.debug(f"Command output: {result.stdout}")
            
                # Print any errors
                if result.stderr:
                    logging.error(f"Command errors: {result.stderr}")             
            except subprocess.CalledProcessError as e:
                logging.error(f"Command failed to execute with exception: {e}")
                logging.error(f"Stderr: {e.stderr}")
            except FileNotFoundError:
                logging.error(f"Error: Command '{command_html[0]}' not found.")
        
        # run comparison command for CSV result            
        if len(command_csv) < 4:
                logging.info(f"No transcript has been generated for {barcode}, skip compare_transcripts for csv output.")
        else:        
            logging.info(f"Running compare_transcripts command for csv output: {command_csv}")            
            try:
                result = subprocess.run(command_csv, capture_output=True, text=True, check=True)
           
                # Print the command's output
                logging.debug(f"Command output: {result.stdout}")
            
                # Print any errors
                if result.stderr:
                    logging.error(f"Command errors: {result.stderr}")             
            except subprocess.CalledProcessError as e:
                logging.error(f"Command failed to execute with exception: {e}")
                logging.error(f"Stderr: {e.stderr}")
            except FileNotFoundError:
                logging.error(f"Error: Command '{command_csv[0]}' not found.")
        
        # write performance info into csv file
        logging.info(f"Saving {len(rows)} rows of performance info into file {perform_csv}")     
        try:
            with open(perform_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        except IOError as e:
            logging.error(f"Failed to save {len(rows)} rows of performance info into file {perform_csv}: {e}")


if __name__ == "__main__":
    main()        