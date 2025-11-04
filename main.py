import argparse
from traffic_analyzer import TrafficAnalyzer
from model import TrafficAnalysisResult

def main():
    """
    Main function of the program.
    if --inputfile is provided then the file will passed to TrafficAnalyzer,
    else the default path ./data/data.txt will be used.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputfile", help="Filepath of machine generated traffic data")
    args = parser.parse_args()
    
    if (not args.inputfile):
        file_path = "./data/data.txt"
    else: 
        file_path = args.inputfile

    print("Analyzing traffic data...")

    traffic_analyzer = TrafficAnalyzer(file_path)

    print("Generating traffic analysis report...")

    traffic_analysis_result = TrafficAnalysisResult(
        total_traffic = traffic_analyzer.calculate_traffic(),
        daily_traffic = traffic_analyzer.get_daily_traffic(),
        top_n_half_hours = traffic_analyzer.get_top_n_half_hours(n=3),
        least_ninety_mins_traffic = traffic_analyzer.least_cars_in_ninety_mins()
    )

    print(traffic_analysis_result)

if __name__ == "__main__":
    main()
