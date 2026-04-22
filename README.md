Valorant Pro Analyzer (AP Region)
A sophisticated Web application for Valorant players to track and analyze their performance. Built with Python Flask and Tailwind CSS, this tool provides deep insights into match history and player statistics for the Asia-Pacific (AP) region.

🌟 Key Features
Instant Player Lookup: Search any player using Riot ID (Name#Tag).
Comprehensive Analytics:
Core Metrics: Real-time calculation of Win Rate, ADR (Average Damage per Round), K/D Ratio, ACS (Average Combat Score), and HS% (Headshot Percentage).
Performance Trends: Visualized ACS and performance history using Chart.js.

Detailed Match History:
Full breakdown of the last 20 matches.
Detailed scoreboards for both Red and Blue teams.
Automatic MVP detection and rank tier icon integration.
High Performance: Utilizes Python's ThreadPoolExecutor for concurrent API requests, ensuring minimal loading times.
Modern UI/UX: Features a "Glassmorphism" design with a fully responsive layout powered by Tailwind CSS.
Localized Content: Built-in mapping for Agents, Maps, and Game Modes (supports official Chinese translations).

🛠️ Tech Stack
Backend: Flask (Python)
Data Processing: Pandas
Frontend: Tailwind CSS
Charts: Chart.js
Data Source: HenrikDev Unofficial Valorant API

🚀 Quick Start
Prerequisites
Python 3.8+
A valid API Key from HenrikDev

Installation
Clone the repository
git clone https://github.com/YourUsername/YourRepoName.git
cd YourRepoName

Install dependencies
pip install flask requests pandas

Configuration
Open app.py and replace MY_API_KEY with your personal API key:
MY_API_KEY = "YOUR_HDEV_API_KEY_HERE"

Run the Application
python app.py
Open your browser and navigate to http://127.0.0.1:5000.

📸 Screenshots
(Tip: Add your screenshots to the static/ folder and link them here)
Dashboard: Overview of player stats and performance charts.
Match Details: Deep dive into specific match scoreboards.

⚠️ Disclaimer
This project is for educational and research purposes only. It is not affiliated with Riot Games. Data is provided by a third-party API and its availability depends on their service uptime.
