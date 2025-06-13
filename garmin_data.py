#!/usr/bin/env python3
"""
Garmin Connect Data Extraction for Do The Work App

This script handles the extraction and processing of Daily Active Calories
data from Garmin Connect using the garminconnect library.
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import json
import concurrent.futures
import threading

try:
    from garminconnect import (
        Garmin,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError,
    )
    import garth
    
    # Set the user agent to mimic Garmin Connect mobile app
    garth.http.USER_AGENT = {'User-Agent': 'GCM-iOS-5.7.2.1'}
    
except ImportError:
    print("Error: garminconnect library not installed.")
    print("Install with: pip install garminconnect")
    sys.exit(1)


class GarminDataExtractor:
    """Handles Garmin Connect authentication and data extraction."""
    
    def __init__(self):
        self.client = None
        self.authenticated = False
    
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with Garmin Connect.
        
        Args:
            email: Garmin Connect email/username
            password: Garmin Connect password
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            self.client = Garmin(email, password)
            self.client.login()
            self.authenticated = True
            print("✅ Successfully authenticated with Garmin Connect")
            return True
            
        except GarminConnectAuthenticationError:
            print("❌ Authentication failed. Please check your credentials.")
            return False
        except GarminConnectConnectionError:
            print("❌ Connection error. Please check your internet connection.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during authentication: {e}")
            return False
    
    def _get_single_day_stats(self, date_str: str) -> Dict:
        """
        Get stats for a single day (thread-safe helper method).
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Dictionary containing date and calories data
        """
        try:
            daily_stats = self.client.get_stats(date_str)
            active_calories = daily_stats.get('activeKilocalories', 0)
            
            return {
                'date': date_str,
                'active_calories': active_calories,
                'total_calories': daily_stats.get('totalKilocalories', 0),
                'bmr_calories': daily_stats.get('bmrKilocalories', 0)
            }
        except GarminConnectTooManyRequestsError:
            print(f"⚠️  Rate limit reached for {date_str}")
            return {
                'date': date_str,
                'active_calories': 0,
                'total_calories': 0,
                'bmr_calories': 0,
                'error': 'rate_limit'
            }
        except Exception as e:
            print(f"⚠️  Error getting data for {date_str}: {e}")
            return {
                'date': date_str,
                'active_calories': 0,
                'total_calories': 0,
                'bmr_calories': 0,
                'error': str(e)
            }

    def get_daily_active_calories(self, start_date: datetime, end_date: datetime, use_concurrent: bool = True, max_workers: int = 20) -> List[Dict]:
        """
        Get daily active calories data for a date range using concurrent requests for speed.
        
        Args:
            start_date: Start date for data extraction
            end_date: End date for data extraction
            use_concurrent: Whether to use concurrent requests (default: True)
            max_workers: Maximum number of concurrent workers (default: 20)
            
        Returns:
            List of dictionaries containing date and active calories data
        """
        if not self.authenticated:
            raise Exception("Not authenticated. Please login first.")
        
        # Generate list of all dates to fetch
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        total_days = len(date_list)
        print(f"📊 Extracting data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"🚀 Using {'concurrent' if use_concurrent else 'sequential'} requests for {total_days} days...")
        
        if use_concurrent and total_days > 1:
            # Use concurrent requests for much faster data retrieval
            data = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all requests
                future_to_date = {executor.submit(self._get_single_day_stats, date_str): date_str 
                                for date_str in date_list}
                
                # Collect results as they complete
                completed = 0
                for future in concurrent.futures.as_completed(future_to_date):
                    result = future.result()
                    data.append(result)
                    completed += 1
                    
                    # Progress indicator
                    if completed % 50 == 0 or completed == total_days:
                        print(f"  📈 Progress: {completed}/{total_days} days ({completed/total_days*100:.1f}%)")
                    
                    # Show successful data points
                    if 'error' not in result and result['active_calories'] > 0:
                        print(f"  ✅ {result['date']}: {result['active_calories']} active calories")
            
            # Sort by date to maintain chronological order
            data.sort(key=lambda x: x['date'])
            
        else:
            # Fall back to sequential requests
            data = []
            for i, date_str in enumerate(date_list):
                result = self._get_single_day_stats(date_str)
                data.append(result)
                
                if 'error' not in result and result['active_calories'] > 0:
                    print(f"  {result['date']}: {result['active_calories']} active calories")
                
                # Progress for sequential
                if (i + 1) % 30 == 0 or i == len(date_list) - 1:
                    print(f"  📈 Progress: {i+1}/{total_days} days ({(i+1)/total_days*100:.1f}%)")
        
        # Filter out error entries for final statistics
        valid_data = [d for d in data if 'error' not in d]
        error_count = len(data) - len(valid_data)
        
        print(f"✅ Data extraction complete: {len(valid_data)} successful, {error_count} errors")
        
        return data
    
    def calculate_30_day_average(self, data: List[Dict]) -> float:
        """Calculate 30-day average of active calories."""
        if not data:
            return 0.0
        
        # Get last 30 days of data
        recent_data = data[-30:] if len(data) >= 30 else data
        active_calories = [day['active_calories'] for day in recent_data if day['active_calories'] > 0]
        
        if not active_calories:
            return 0.0
        
        return statistics.mean(active_calories)
    
    def calculate_monthly_ramp_rate(self, data: List[Dict]) -> float:
        """
        Calculate monthly ramp rate (change from 30-60 days ago vs last 30 days).
        
        Returns:
            Percentage change from previous 30-day period to current 30-day period
        """
        if len(data) < 60:
            return 0.0
        
        # Last 30 days
        recent_30 = data[-30:]
        recent_calories = [day['active_calories'] for day in recent_30 if day['active_calories'] > 0]
        
        # Previous 30 days (30-60 days ago)
        previous_30 = data[-60:-30]
        previous_calories = [day['active_calories'] for day in previous_30 if day['active_calories'] > 0]
        
        if not recent_calories or not previous_calories:
            return 0.0
        
        recent_avg = statistics.mean(recent_calories)
        previous_avg = statistics.mean(previous_calories)
        
        if previous_avg == 0:
            return 0.0
        
        return ((recent_avg - previous_avg) / previous_avg) * 100
    
    def get_monthly_averages(self, data: List[Dict]) -> List[Dict]:
        """
        Calculate monthly averages for the last 12 months.
        
        Returns:
            List of dictionaries with month and average active calories
        """
        if not data:
            return []
        
        # Group data by month
        monthly_data = {}
        
        for day in data:
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            month_key = date_obj.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            
            if day['active_calories'] > 0:
                monthly_data[month_key].append(day['active_calories'])
        
        # Calculate averages and format for chart
        monthly_averages = []
        for month, calories_list in monthly_data.items():
            if calories_list:
                avg_calories = statistics.mean(calories_list)
                monthly_averages.append({
                    'month': month,
                    'average_calories': round(avg_calories, 1),
                    'days_recorded': len(calories_list)
                })
        
        # Sort by month and return last 12 months
        monthly_averages.sort(key=lambda x: x['month'])
        return monthly_averages[-12:]
    
    def get_dashboard_data(self, email: str, password: str) -> Dict:
        """
        Get all dashboard data for the user.
        
        Args:
            email: Garmin Connect email/username
            password: Garmin Connect password
            
        Returns:
            Dictionary containing all dashboard metrics
        """
        if not self.authenticate(email, password):
            return {'error': 'Authentication failed'}
        
        try:
            # Get data for the last year
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            raw_data = self.get_daily_active_calories(start_date, end_date)
            
            if not raw_data:
                return {'error': 'No data found'}
            
            # Calculate metrics
            avg_30_day = self.calculate_30_day_average(raw_data)
            ramp_rate = self.calculate_monthly_ramp_rate(raw_data)
            monthly_averages = self.get_monthly_averages(raw_data)
            
            dashboard_data = {
                'success': True,
                'metrics': {
                    'avg_30_day_calories': round(avg_30_day, 1),
                    'monthly_ramp_rate': round(ramp_rate, 1),
                    'total_days': len(raw_data),
                    'active_days': len([d for d in raw_data if d['active_calories'] > 0])
                },
                'monthly_data': monthly_averages,
                'last_updated': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            return {'error': f'Data extraction failed: {str(e)}'}


def main():
    """Main function for testing the data extraction."""
    print("🏃‍♂️ Do The Work - Garmin Data Extractor")
    print("=" * 40)
    
    # Get credentials from user input
    email = input("Enter your Garmin Connect email: ").strip()
    password = input("Enter your Garmin Connect password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required.")
        return
    
    # Create extractor and get data
    extractor = GarminDataExtractor()
    dashboard_data = extractor.get_dashboard_data(email, password)
    
    if 'error' in dashboard_data:
        print(f"❌ Error: {dashboard_data['error']}")
        return
    
    # Display results
    print("\n📊 Dashboard Data:")
    print("=" * 40)
    print(f"30-Day Average: {dashboard_data['metrics']['avg_30_day_calories']} calories")
    print(f"Monthly Ramp Rate: {dashboard_data['metrics']['monthly_ramp_rate']:+.1f}%")
    print(f"Total Days: {dashboard_data['metrics']['total_days']}")
    print(f"Active Days: {dashboard_data['metrics']['active_days']}")
    
    print("\n📈 Monthly Averages:")
    print("=" * 40)
    for month_data in dashboard_data['monthly_data']:
        print(f"{month_data['month']}: {month_data['average_calories']} calories "
              f"({month_data['days_recorded']} days)")
    
    # Save to JSON file for testing
    with open('sample_data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"\n✅ Data saved to 'sample_data.json'")


if __name__ == "__main__":
    main() 