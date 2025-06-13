# Do The Work

A mobile-friendly FastHTML web application that connects to your Garmin Connect account to display your Daily Active Calories data in a clean, responsive dashboard.

## Features

- **30-Day Average**: See your average daily active calories over the last 30 days
- **Monthly Trend**: Track your progress with monthly ramp rate indicators
- **12-Month History**: Visualize your fitness journey with interactive charts
- **Mobile-First**: Optimized for mobile devices with responsive design
- **Secure**: Session-based authentication, credentials never stored

## Tech Stack

- **FastHTML**: Modern Python web framework
- **garminconnect**: Python library for Garmin Connect API
- **Vercel**: Serverless deployment platform
- **Chart.js**: Interactive data visualization

## Quick Start

### Prerequisites

- Python 3.8+
- A Garmin Connect account
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/do-the-work.git
   cd do-the-work
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5001`

### Test Garmin Data Extraction

Before running the full app, you can test the Garmin data extraction:

```bash
python garmin_data.py
```

Enter your Garmin Connect credentials when prompted.

## Deployment

### Deploy to Vercel

This app is **ready for one-click deployment** on Vercel! 🚀

1. **Push to GitHub**: 
   ```bash
   git add .
   git commit -m "Ready for Vercel deployment"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click "New Project" 
   - Import your GitHub repository
   - Vercel will automatically detect the Python runtime via `vercel.json`
   - Click "Deploy"

3. **Deployment Features**: 
   - ✅ `vercel.json` configured for Python 3.10 runtime
   - ✅ Static files properly routed (`/static/`)
   - ✅ 60-second timeout for data fetching
   - ✅ Serverless functions optimized for FastHTML
   - ✅ No environment variables needed

4. **Performance on Vercel**:
   - **Cold start**: ~2-3 seconds
   - **Data fetching**: ~6-13 seconds for full year (concurrent optimization)
   - **Page loads**: <1 second after initial data fetch

### Environment Variables

No environment variables are required! All authentication is handled through the secure web interface.

## How It Works

1. **Login**: Enter your Garmin Connect username and password
2. **Data Fetch**: The app securely connects to Garmin Connect and pulls your historical active calories data
3. **Processing**: Calculates 30-day averages and monthly trends
4. **Visualization**: Displays your data in an easy-to-read dashboard

## Data Privacy

- Your Garmin credentials are never stored permanently
- Session data is cleared when you close the browser
- No personal data is logged or stored on our servers
- All communication with Garmin Connect is encrypted

## API Rate Limits

The app respects Garmin Connect's API rate limits:
- Data is cached during your session to minimize API calls
- Historical data is fetched once per session
- Real-time updates are throttled appropriately

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Project Structure

```
/
├── main.py              # FastHTML application entry point
├── garmin_data.py       # Garmin Connect data extraction logic
├── static/
│   ├── style.css        # Responsive CSS styles
│   └── chart.js         # Chart visualization code
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel deployment configuration
├── .cursorrules        # AI assistant guidelines
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

### Key Components

- **FastHTML Routes**: Handle login, dashboard, and data endpoints
- **Garmin Integration**: Secure connection to Garmin Connect API
- **Data Processing**: Calculate averages, trends, and chart data
- **Responsive UI**: Mobile-first design with progressive enhancement

## Troubleshooting

### Common Issues

**Login Fails**
- Verify your Garmin Connect credentials
- Check if your account requires two-factor authentication
- Ensure you have an active internet connection

**No Data Displayed**
- Make sure you have activity data in your Garmin Connect account
- Check that your account has at least 30 days of recorded data
- Try refreshing the page to re-fetch data

**Deployment Issues**
- Verify all dependencies are listed in `requirements.txt`
- Check Vercel build logs for specific error messages
- Ensure `main.py` properly exports the FastHTML app

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastHTML](https://fastht.ml/) - Modern Python web framework
- [garminconnect](https://github.com/cyberjunky/python-garminconnect) - Garmin Connect API library
- [Chart.js](https://www.chartjs.org/) - Data visualization library
- [Vercel](https://vercel.com/) - Deployment platform

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/do-the-work/issues) page
2. Create a new issue if your problem isn't already reported
3. Include as much detail as possible about your environment and the issue

---

**Built with ❤️ and FastHTML** 