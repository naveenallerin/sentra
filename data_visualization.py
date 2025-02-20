import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def analyze_and_visualize(log_file="object_logs.csv"):
    # Read the CSV file into a pandas DataFrame
    try:
        df = pd.read_csv(log_file)
    except FileNotFoundError:
        print(f"Error: {log_file} not found. Run camera_feed.py first to generate logs.")
        return

    # Aggregate data: count objects by type
    object_counts = df['object_type'].value_counts()
    print("Object counts by type:")
    print(object_counts)

    # Aggregate by timestamp (group by hour for simplicity)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    hourly_counts = df.groupby(pd.Grouper(key='timestamp', freq='H'))['object_type'].count()
    print("\nObjects detected per hour:")
    print(hourly_counts)

    # Create visualizations
    # Bar chart for object types
    plt.figure(figsize=(10, 6))
    object_counts.plot(kind='bar')
    plt.title("Object Detection Counts by Type")
    plt.xlabel("Object Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Line chart for hourly trends
    plt.figure(figsize=(10, 6))
    hourly_counts.plot(kind='line', marker='o')
    plt.title("Objects Detected Over Time (Hourly)")
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.tight_layout()

    # Show plots
    plt.show()

    # Optionally, save plots to files
    plt.figure(1).savefig("object_type_counts.png")
    plt.figure(2).savefig("hourly_trends.png")
    print("Visualizations saved as object_type_counts.png and hourly_trends.png")

if __name__ == "__main__":
    analyze_and_visualize()