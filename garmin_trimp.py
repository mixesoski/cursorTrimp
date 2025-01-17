from garminconnect import Garmin
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials from environment variables
EMAIL = os.getenv('GARMIN_EMAIL')
PASSWORD = os.getenv('GARMIN_PASSWORD')

def get_garmin_data():
    # Initialize Garmin client
    client = Garmin(EMAIL, PASSWORD)
    
    # Login to Garmin Connect
    client.login()
    
    # Calculate date range (last 42 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=42)
    
    # Get activities
    activities = client.get_activities_by_date(
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    # Extract TRIMP values and dates
    data = []
    for activity in activities:
        # Get detailed activity data
        activity_id = activity['activityId']
        try:
            activity_details = client.get_activity_details(activity_id)
            
            date = datetime.strptime(activity['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
            trimp = activity_details.get('summaryDTO', {}).get('trainingIntensityPoints', 0)
            
            data.append({
                'date': date,
                'trimp': trimp,
                'activity_type': activity.get('activityType', {}).get('typeKey', 'Unknown'),
                'activity_name': activity.get('activityName', 'Unknown')
            })
            
            print(f"\nProcessing activity: {activity.get('activityName', 'Unknown')}")
            print(f"TRIMP value: {trimp}")
            
        except Exception as e:
            print(f"Error getting details for activity {activity_id}: {str(e)}")
            continue
    
    return pd.DataFrame(data)

def create_trimp_chart(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['trimp'], marker='o')
    plt.title('TRIMP Values Over Last 42 Days')
    plt.xlabel('Date')
    plt.ylabel('TRIMP')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the chart
    plt.savefig('trimp_chart.png')
    plt.close()

def main():
    try:
        # Get data
        df = get_garmin_data()
        
        # Sort by date
        df = df.sort_values('date')
        
        # Print the data
        print("\nFetched TRIMP data:")
        print("==================")
        for index, row in df.iterrows():
            print(f"Date: {row['date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Activity: {row['activity_name']} ({row['activity_type']})")
            print(f"TRIMP: {row['trimp']}")
            print("------------------")
        
        print("\nTotal activities:", len(df))
        print("Average TRIMP:", round(df['trimp'].mean(), 2))
        print("==================\n")
        
        # Create chart
        create_trimp_chart(df)
        
        print("Chart has been created successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main() 