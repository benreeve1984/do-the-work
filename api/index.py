#!/usr/bin/env python3
"""
Do The Work - FastHTML Garmin Connect App
TrainingPeaks-inspired design for displaying Daily Active Calories data
"""

from fasthtml.common import *
from datetime import datetime, timedelta
import json
import statistics
from garmin_data import GarminDataExtractor

# Initialize FastHTML app with custom CSS and JS
css = Link(rel="stylesheet", href="/static/style.css")
chart_js = Script(src="https://cdn.jsdelivr.net/npm/chart.js")
app_js = Script(src="/static/app.js")

app, rt = fast_app(
    hdrs=[css, chart_js, app_js]
)

# Mount static files
from starlette.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global extractor instance
extractor = GarminDataExtractor()

def TrainingPeaksLayout(title: str, *content):
    """TrainingPeaks-inspired layout wrapper"""
    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(f"{title} | Do The Work"),
            
            # OpenGraph meta tags for social media previews
            Meta(property="og:title", content=f"{title} | Do The Work"),
            Meta(property="og:description", content="Garmin Connect analytics inspired by Alan Couzens. Track your daily active calories with 30-day averages, monthly trends, and performance insights."),
            Meta(property="og:type", content="website"),
            Meta(property="og:image", content="https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=1200&h=630&fit=crop"),
            Meta(property="og:image:width", content="1200"),
            Meta(property="og:image:height", content="630"),
            Meta(property="og:site_name", content="Do The Work"),
            
            # Twitter Card meta tags
            Meta(name="twitter:card", content="summary_large_image"),
            Meta(name="twitter:title", content=f"{title} | Do The Work"),
            Meta(name="twitter:description", content="Garmin Connect analytics inspired by Alan Couzens. Track your daily active calories with 30-day averages, monthly trends, and performance insights."),
            Meta(name="twitter:image", content="https://images.unsplash.com/photo-1544966503-7cc5ac882d5f?w=1200&h=630&fit=crop"),
            
            # Standard meta description
            Meta(name="description", content="Garmin Connect analytics inspired by Alan Couzens. Track your daily active calories with 30-day averages, monthly trends, and performance insights."),
            
            css,
            chart_js
        ),
        Body(
            Header(
                Div(
                    H1("Do The Work", cls="logo"),
                    Div(
                        "Garmin Connect analytics inspired by ",
                        A("Alan Couzens", href="https://alancouzens.substack.com/p/its-time-to-get-real-about-the-work", 
                          target="_blank", style="color: #ff6b35; text-decoration: none;"),
                        cls="tagline"
                    ),
                    cls="header-content"
                ),
                cls="header"
            ),
            Main(*content, cls="main-content"),
            app_js,
            cls="training-peaks-theme"
        )
    )

def StatCard(title: str, value: str, subtitle: str = "", trend: str = ""):
    """TrainingPeaks-style stat card component"""
    trend_class = f"trend-{trend}" if trend else ""
    trend_icon = "↗" if trend == "up" else "↘" if trend == "down" else ""
    
    return Div(
        Div(title, cls="stat-title"),
        Div(value, cls="stat-value"),
        Div(
            subtitle,
            Span(f" {trend_icon}", cls=f"trend-icon {trend_class}") if trend_icon else "",
            cls="stat-subtitle"
        ),
        cls="stat-card"
    )

@rt("/")
def get(session):
    """Home page - redirect to login if not authenticated"""
    if not session.get('authenticated'):
        return RedirectResponse('/login')
    return RedirectResponse('/dashboard')

@rt("/login")
def get(session):
    """Login page with TrainingPeaks styling"""
    return TrainingPeaksLayout(
        "Login",
        Div(
            Div(
                H2("Connect to Garmin", cls="login-title"),
                P("Enter your Garmin Connect credentials to analyze your training data", cls="login-subtitle"),
                
                Form(
                    Div(
                        Label("Username", fr="username"),
                        Input(type="email", id="username", name="username", placeholder="your-email@example.com", required=True),
                        cls="form-group"
                    ),
                    Div(
                        Label("Password", fr="password"),
                        Input(type="password", id="password", name="password", placeholder="Password", required=True),
                        cls="form-group"
                    ),
                    Button("Connect to Garmin", type="submit", cls="btn-primary btn-login"),
                    method="post",
                    action="/login",
                    cls="login-form"
                ),
                
                Div(
                    P("🔒 Your credentials are used only to fetch your data and are never stored.", cls="security-note"),
                    cls="security-info"
                ),
                
                cls="login-card"
            ),
            cls="login-container"
        )
    )

@rt("/login")
def post(username: str, password: str, session):
    """Handle login form submission"""
    try:
        # Authenticate with Garmin Connect
        if extractor.authenticate(username, password):
            session['authenticated'] = True
            session['username'] = username
            return RedirectResponse('/dashboard', status_code=303)
        else:
            return TrainingPeaksLayout(
                "Login",
                Div(
                    Div(
                        Div("❌ Authentication failed. Please check your credentials.", cls="error-message"),
                        H2("Connect to Garmin", cls="login-title"),
                        P("Enter your Garmin Connect credentials to analyze your training data", cls="login-subtitle"),
                        
                        Form(
                            Div(
                                Label("Username", fr="username"),
                                Input(type="email", id="username", name="username", value=username, required=True),
                                cls="form-group"
                            ),
                            Div(
                                Label("Password", fr="password"),
                                Input(type="password", id="password", name="password", required=True),
                                cls="form-group"
                            ),
                            Button("Connect to Garmin", type="submit", cls="btn-primary btn-login"),
                            method="post",
                            action="/login",
                            cls="login-form"
                        ),
                        
                        Div(
                            P("🔒 Your credentials are used only to fetch your data and are never stored.", cls="security-note"),
                            cls="security-info"
                        ),
                        
                        cls="login-card"
                    ),
                    cls="login-container"
                )
            )
    except Exception as e:
        return TrainingPeaksLayout(
            "Login",
            Div(f"Error: {str(e)}", cls="error-message"),
        )

@rt("/dashboard")
def get(session):
    """Main dashboard with TrainingPeaks-style data visualization"""
    if not session.get('authenticated'):
        return RedirectResponse('/login')
    
    try:
        # Get data for the last year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        print("📊 Fetching dashboard data...")
        data = extractor.get_daily_active_calories(start_date, end_date)
        
        # Calculate metrics
        avg_30_day_value = extractor.calculate_30_day_average(data)
        ramp_rate = extractor.calculate_monthly_ramp_rate(data)
        monthly_data = extractor.get_monthly_averages(data)
        
        # Calculate monthly trend in calories as well as percentage
        if len(data) >= 60:
            recent_30 = data[-30:]
            previous_30 = data[-60:-30]
            recent_calories = [day['active_calories'] for day in recent_30 if day['active_calories'] > 0]
            previous_calories = [day['active_calories'] for day in previous_30 if day['active_calories'] > 0]
            
            if recent_calories and previous_calories:
                recent_avg = sum(recent_calories) / len(recent_calories)
                previous_avg = sum(previous_calories) / len(previous_calories)
                calorie_change = recent_avg - previous_avg
            else:
                calorie_change = 0
        else:
            calorie_change = 0
        
        # Format metrics for display
        avg_30_day = f"{avg_30_day_value:.0f}"
        ramp_trend = "up" if ramp_rate > 0 else "down" if ramp_rate < 0 else "neutral"
        calorie_sign = "+" if calorie_change >= 0 else ""
        ramp_display_percent = f"{ramp_rate:+.1f}%"
        ramp_display_calories = f"{calorie_sign}{calorie_change:.0f} cal/day"
        
        # Calculate 3-month average for performance level
        three_month_data = data[-90:] if len(data) >= 90 else data
        three_month_calories = [day['active_calories'] for day in three_month_data if day['active_calories'] > 0]
        three_month_avg = sum(three_month_calories) / len(three_month_calories) if three_month_calories else 0
        
        # Determine performance level
        if three_month_avg < 500:
            performance_level = "Health & Fitness"
            level_color = "#94a3b8"
        elif three_month_avg < 1000:
            performance_level = "Recreational"
            level_color = "#22c55e"
        elif three_month_avg < 1500:
            performance_level = "Developmental" 
            level_color = "#f59e0b"
        elif three_month_avg < 2000:
            performance_level = "Competitive"
            level_color = "#0077be"
        elif three_month_avg < 3000:
            performance_level = "Top Amateur"
            level_color = "#8b5cf6"
        else:
            performance_level = "Elite/Pro"
            level_color = "#ff6b35"
        
        # Prepare chart data with proper month formatting
        chart_labels = []
        chart_values = [month['average_calories'] for month in monthly_data]
        
        for month in monthly_data:
            # Parse YYYY-MM format and convert to "Jan-25" format
            year_month = month['month']
            year, month_num = year_month.split('-')
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_name = month_names[int(month_num) - 1]
            chart_labels.append(f"{month_name}-{year[-2:]}")
        
        # Calculate annual average for chart line
        annual_average = sum(chart_values) / len(chart_values) if chart_values else 0
        
        # Activity calories by type over the last 30 days (average per day, including unlogged portion)
        activity_breakdown = extractor.get_activity_calories_breakdown(start_date, end_date, data)
        panel_avg_30 = avg_30_day_value  # exact same source as the 30-day panel
        
        return TrainingPeaksLayout(
            "Dashboard",
            
            # Welcome section
            Div(
                H2(f"Welcome back, {session.get('username', 'Athlete')}", cls="welcome-title"),
                P(f"Training data from {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}", cls="date-range"),
                cls="welcome-section"
            ),
            
            # Key metrics cards
            Div(
                StatCard(
                    "30-Day Average",
                    avg_30_day,
                    "Active Calories/Day",
                ),
                Div(
                    Div("Monthly Trend", cls="stat-title"),
                    Div(ramp_display_percent, cls="stat-value"),
                    Div(ramp_display_calories, cls="stat-subtitle-secondary"),
                    Div(
                        "vs Previous 30 Days",
                        Span(f" {'↗' if ramp_trend == 'up' else '↘' if ramp_trend == 'down' else ''}", cls=f"trend-icon trend-{ramp_trend}") if ramp_trend != "neutral" else "",
                        cls="stat-subtitle"
                    ),
                    cls="stat-card"
                ),
                Div(
                    Div("Performance Level", cls="stat-title"),
                    Div(performance_level, cls="stat-value"),
                    Div(f"{three_month_avg:.0f} cal/day", cls="stat-subtitle-secondary"),
                    Div("3-Month Average", cls="stat-subtitle"),
                    cls="stat-card"
                ),
                cls="metrics-grid"
            ),
            
            # Chart section
            Div(
                H3("12-Month Active Calories Trend", cls="chart-title"),
                Div(
                    Canvas(id="caloriesChart", width="400", height="200"),
                    cls="chart-container"
                ),
                cls="chart-section"
            ),
            
            # Activity calories by type section (30-day avg)
            Div(
                H3("Active Calories by Activity Type (30-day avg)", cls="chart-title"),
                Div(
                    f"Percentages reflect share of last-30-day average daily active calories (~ {int(round(panel_avg_30)):,} cal/day).",
                    cls="activity-note"
                ),
                Div(
                    *[
                        (lambda pct: Div(
                            Div(item['type'], cls="activity-type"),
                            Div(
                                Div(cls="progress-bar-fill", style=f"width: {pct}%"),
                                cls="progress-bar"
                            ),
                            Div(
                                Span(f"{int(round(item['calories'])):,} cal/day", cls="activity-calories"),
                                Span(f"{pct:.1f}% of daily active", cls="activity-percent"),
                                cls="activity-stats"
                            ),
                            cls="activity-item"
                        ))(max(0.0, min(100.0, (item['calories'] / panel_avg_30 * 100.0) if panel_avg_30 > 0 else 0.0)))
                        for item in activity_breakdown.get('by_type', [])
                    ],
                    cls="activity-breakdown-grid"
                ),
                cls="activity-section"
            ),
            
            # Data insights
            Div(
                H3("Insights", cls="insights-title"),
                Div(
                    Div(
                        H4("Best Month"),
                        P(f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][int(max(monthly_data, key=lambda x: x['average_calories'])['month'].split('-')[1]) - 1]}-{max(monthly_data, key=lambda x: x['average_calories'])['month'].split('-')[0][-2:]}" if monthly_data else "N/A"),
                        P(f"{max(monthly_data, key=lambda x: x['average_calories'])['average_calories']:.0f} cal/day" if monthly_data else "No data", cls="insight-value"),
                        cls="insight-card"
                    ),
                    Div(
                        H4("Biggest Day"),
                        P(f"{datetime.strptime(max(data, key=lambda x: x.get('active_calories', 0))['date'], '%Y-%m-%d').strftime('%-d-%b-%y') if data else 'N/A'}"),
                        P(f"{max(data, key=lambda x: x.get('active_calories', 0))['active_calories']:.0f} calories" if data else "No data", cls="insight-value"),
                        cls="insight-card"
                    ),
                    Div(
                        H4("Annual Average"),
                        P("12-Month Average"),
                        P(f"{annual_average:.0f} cal/day", cls="insight-value"),
                        cls="insight-card"
                    ),
                    cls="insights-grid"
                ),
                cls="insights-section"
            ),
            
            # Chart data script
            Script(f"""
                const chartData = {{
                    labels: {json.dumps(chart_labels)},
                    values: {json.dumps(chart_values)},
                    annualAverage: {annual_average:.1f}
                }};
                
                // Initialize chart when page loads
                document.addEventListener('DOMContentLoaded', function() {{
                    initChart(chartData);
                }});
            """),
            
            # Logout section
            Div(
                A("Logout", href="/logout", cls="btn-secondary"),
                cls="logout-section"
            )
        )
        
    except Exception as e:
        return TrainingPeaksLayout(
            "Dashboard",
            Div(f"Error loading dashboard: {str(e)}", cls="error-message"),
            A("Back to Login", href="/login", cls="btn-primary")
        )

@rt("/logout")
def get(session):
    """Logout and clear session"""
    session.clear()
    return RedirectResponse('/login')

# Export the app for Vercel
# Vercel will automatically serve this as a serverless function
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 