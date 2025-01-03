#!/usr/bin/python3
import argparse
import os
import time

# Function to parse command-line arguments
def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run robot chip to Hexa with specified trays and chip numbers.")
    
    # Add arguments for trays and chip numbers
    parser.add_argument('--trays_a', type=str, required=True, help="List of trays for A configuration (comma-separated)")
    parser.add_argument('--trays_b', type=str, required=True, help="List of trays for B configuration (comma-separated)")
    parser.add_argument('--chip_number_start_a', type=int, required=True, help="Starting chip number for A")
    parser.add_argument('--chip_number_start_b', type=int, required=True, help="Starting chip number for B")
    
    # Parse the arguments
    return parser.parse_args()

# Function to simulate the Hexa job locally (dummy action)
def simulate_hexa_job(trays_a, trays_b, chip_number_start_a, chip_number_start_b):
    """Simulate the Hexa job with the provided arguments."""
    try:
        # Simulate job logic (replace with actual functionality later)
        print(f"Simulating Hexa job with the following configuration:")
        print(f"Trays A: {trays_a}")
        print(f"Trays B: {trays_b}")
        print(f"Chip number start A: {chip_number_start_a}")
        print(f"Chip number start B: {chip_number_start_b}")

        # Dummy simulation (just sleeps for 5 seconds to simulate work)
        time.sleep(5)
        
        # Simulate the output of the job
        print("Hexa job simulation complete!")
        return True
    except Exception as e:
        print(f"Error simulating Hexa job: {e}")
        return False

# Function to keep the process running in a while loop (simulating the job)
def run_while_loop():
    """Run the robot job in a while loop."""
    # Parse the arguments
    args = parse_arguments()
    
    # Extract trays and chip numbers from the arguments
    trays_a = args.trays_a.split(',')
    trays_b = args.trays_b.split(',')
    chip_number_start_a = args.chip_number_start_a
    chip_number_start_b = args.chip_number_start_b

    # Print the received values for confirmation (or use them in your logic)
    print(f"Trays A: {trays_a}")
    print(f"Trays B: {trays_b}")
    print(f"Chip number start A: {chip_number_start_a}")
    print(f"Chip number start B: {chip_number_start_b}")
    
    # Continuous loop simulating the Hexa job
    while True:
        # Simulate the Hexa job (as dummy action)
        success = simulate_hexa_job(trays_a, trays_b, chip_number_start_a, chip_number_start_b)
        
        if success:
            print("Job completed successfully!")
        else:
            print("Error during job simulation.")
        
        # Sleep before re-running the simulation (or adjust as needed)
        print("Waiting before the next simulation...")
        time.sleep(10)  # Sleep for 10 seconds before restarting the loop

if __name__ == "__main__":
    run_while_loop()
