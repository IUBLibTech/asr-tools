#!/bin/env python3
# Run whisper transcribe on a predefined set of language models and audio files and save relevant performance information along with transcript results.

import os
import logging
import subprocess
import time
import json


def main():
    # activate whipser virtual environment
    venv = "/srv/scratch/yingfeng/whisper/.venv/bin/activate"
    
    # go to the tests directory
    tests_dir = "/srv/scratch/yingfeng/tests"
    os.chdir(tests_dir)
    logging.info(f"Changed working directory to: {os.getcwd()}")
    
    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        filename = 'log/whisper.log',
        filemode = 'a')
    
    # set up whisper command
    engine = "whisper"
    models = ["turbo", "large-v3", "large-v2", "medium", "medium.en", "small.en", "base.en", "tiny.en"]
    barcodes = ["40000003402619", "40000003189265", "40000003403856"];   
    lang_param = f"--language en"
    # TODO vary performance-impact parameters 
    # params = []
    
    # run whisper: loop through models
    for model in models:
        model_param = f"--model {model}"
        output_dir = f"{engine}/{model}"
        output_param = f"-o {output_dir}"
        
        # run whisper: loop through files
        for barcode in barcodes:
            # if the corresponding performance file exists, skip this model-file, as it has been run
            pfm_file = f"{output_dir}/{barcode}.pfm.json"
            if os.path.exists(pfm_file):
                continue

            # audio file to transcribe
            audio = f"/N/esquilax/srv/storage/mdpi_research/wsjv/MDPI_{barcode}_01_high.mp4"
                         
            # command line for running whisper
            command = ["whisper", model_param, lang_paran, output_param, audio]
            
            # Record the start time
            start_time = time.perf_counter()
            start_time_cpu = time.process_time()
            logging.info(f"Starting command: {command}, \n\t start_time: {start_time}, start_time_cpu: {start_time_cpu}")
        
            try:
                # Run the command and capture its output
                # `capture_output=True` redirects stdout and stderr to the result object
                # `text=True` decodes the output as text
                result = subprocess.run(command, capture_output=True, text=True, check=True)
            
                # TODO record memory usage
            
                # Record the end time
                end_time = time.perf_counter()
                end_time_cpu = time.process_time()
                logging.info(f"Completed command: {command}, \n\t end_time: {end_time}, end_time_cpu: {end_time_cpu}")
            
                # Calculate the elapsed time
                total_time = end_time - start_time
                cpu_time = end_time_cpu - start_time_cpu
                logging.info(f"Total execution time: {total_time:.4f} seconds, CPU time used: {cpu_time:.4f} seconds")
                
                # Print the command's output
                logging.debug(f"Command output: {result.stdout}")
            
                # Print errors if any; otherwise save performance info into file
                if result.stderr:
                    logging.error(f"Command errors: \n{result.stderr}")             
                else:            
                    pfm_info = {
                        "total_time": total_time, 
                        "cpu_time": cpu_time
                    }           
                    with open(pfm_file, 'w') as file:
                        json.dump(pfm_info, file) 
            except subprocess.CalledProcessError as e:
                # Handle errors if the command returns a non-zero exit code
                logging.error(f"Command failed to execute with exception: {e}")
                logging.error(f"Stderr: {e.stderr}")
            except FileNotFoundError as e:
                logging.error(f"Error: Command '{command[0]}' not found: {e}.")
            except IOError as e:
                logging.error(f"Failed to write performance info into file {pfm_file}: {e}")
        

if __name__ == "__main__":
    main()        