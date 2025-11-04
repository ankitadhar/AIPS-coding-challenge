import argparse
from traffic_analyzer import TrafficAnalysisResult, TrafficAnalyzer

def main():
    """
    Main function of the program.
    if --inputfile is provided then the file will be read from the given path,
    else it will read from the default path ./data.txt
    1. Transforms the data into a dictionary
    2. Calculates total traffic
    3. Calculates daily traffic
    4. Finds top 3 half hours with highest traffic
    5. Finds contiguous 90 minutes intervals car counts
    6. Prints the results to the console
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputfile", help="Filepath of machine generated traffic data")
    args = parser.parse_args()
    
    if (not args.inputfile):
        file_path = "./data.txt"
    else: 
        file_path = args.inputfile

    traffic_analyzer = TrafficAnalyzer(file_path)

    traffic_analysis_result = TrafficAnalysisResult(
        total_traffic = traffic_analyzer.calculate_traffic(),
        daily_traffic = traffic_analyzer.get_daily_traffic(),
        top_n_half_hours = traffic_analyzer.get_top_n_half_hours(n=3),
        least_ninety_mins_traffic = traffic_analyzer.least_cars_in_ninety_mins()
    )

    print(traffic_analysis_result)

    # print("\n\nCalculating total traffic...")
    # total_traffic = calculate_traffic(data_dict)
    # print(f"The number of cars seen in total: {total_traffic}")

    # print("\n\nCalculating daily traffic...")
    # print("Date       Number of cars seen")
    # print("-------------------------------")
    # daily_traffic = get_daily_traffic(data_dict)
    # for date, traffic in daily_traffic.items():
    #     print(f"{date}\t{traffic}")

    # print("\n\nFinding top 3 half hours with highest traffic...")
    # print("Timestamp           Number of cars seen")
    # print("---------------------------------------")
    # for timestamp, traffic in get_top_n_half_hours(data_dict, n=3):
    #     print(f"{timestamp} {traffic}")

    # print("\n\nFinding contiguous 90 minutes intervals car counts...")
    # contiguous_ninty_mins_traffic = get_contiguous_ninty_mins_traffic(data_dict)
    # least_cars_timestamp = min(contiguous_ninty_mins_traffic.items(), key=lambda x: x[1])
    # print(f"Timestamp with least number of cars seen in next 90 minutes: {least_cars_timestamp[0]}")
    # print("\nTimestamp           Number of cars seen in next 90 minutes")
    # print("---------------------------------------------------")
    # print(f"{least_cars_timestamp[0]}\t{least_cars_timestamp[1]}")

if __name__ == "__main__":
    main()