# ⚽ World Cup 2026 Analytics Platform

![Python](https://img.shields.io/badge/python-3.10-blue)
![Streamlit](https://img.shields.io/badge/streamlit-app-red)
![Status](https://img.shields.io/badge/status-active-success)

A comprehensive football analytics platform built with Streamlit, designed to explore, analyze, and visualize matches, teams, and player performance from a data-driven perspective.

This project simulates a professional football intelligence dashboard, combining event data, tactical analysis, and advanced metrics such as xG, xT, possession structures, and defensive behavior.

🌐 **Live Application:**  
👉 [Access the World Cup 2026 Analytics Platform](https://worldcup26dashboard-develop.streamlit.app/)

Explore live football analytics, tactical visualizations, and advanced match insights.


<p align="center">
  <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/home.png" width="800"/>
</p>

## 📌 Overview

The World Cup 2026 Analytics Platform is an interactive web application that allows users to:

- Explore teams, rosters, venues, fixtures, and results
- Analyze full matches with event-by-event breakdowns
- Visualize tactical behavior (formations, passing networks, heatmaps)
- Track attacking and defensive performance
- Work with advanced metrics such as xG (expected goals) and xT (expected threat)
- Generate downloadable tactical reports

The goal is to deliver a professional-level football analysis experience, similar to tools used in scouting and performance departments.

## 🚀 Key Features

### 🏆 Competition Hub:

> Explore teams, squads, venues and tournament structure in a unified interface.

- Full list of national teams.
- Team profiles with FIFA and ELO integration.
- Stadium and venue exploration.
- Fixtures calendar with filtering by stage, group, and date.
- Interactive results dashboard.



<p align="center">
  
  <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/team_detail.png" width="400"/>
  <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/team_roster.png" width="400"/>
  <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/calendar.png" width="400"/>
  <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/groups.png" width="400"/>
<img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/venues.png" width="400"/>
<img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/filter_result.png" width="400"/>

</p>

---

### 📊 Match Center (Core Feature)

Each match includes a full analytical breakdown:

> #### ⚽ Match Overview

- Live-style scoreboard with team colors.
- Match state (FT / AET / PEN).
- Venue, referee, attendance.
- Man of the Match highlight.

> #### 📍 Event Timeline

- Goals, cards, substitutions, penalties.
- Chronological match event feed.
- Penalty shootout visualization.
- First half / second half / extra time segmentation.

> #### 🧠 Tactical Analysis

- Starting formations.
- Player positioning maps.
- Passing networks.
- Progressive passing analysis.
- Final third entries.
- Zone 14 & half-space occupation.
- Chance creation zones.

> #### 📈 Advanced Analytics

##### ⚡ Attacking Analysis:

- Shot maps with xG context.
- xG flow over time.
- Attack momentum using xT.
- Cross analysis.
- Ball progression patterns.

##### 🛡️ Defensive Analysis:

- Defensive heatmaps.
- Action zones per team.
- Recovery and pressing zones.

##### 🧤 Goalkeeper Analysis:

- Shot placement maps.
- Goalkeeper intervention analysis.

##### 🧠 Possession & Structure:

- Average player positions.
- Passing networks (team structure).
- Touch heatmaps.
- Pass end-zone mapping.

> #### 📑 Automated Reporting System

The platform includes a reporting engine capable of generating:

- Tactical team reports.
- Match performance summaries.
- Shot maps and xG/xT visualizations.
- Defensive and attacking breakdowns.

Reports can be:

- Generated dynamically.
- Exported as PNG images.
- Cached for performance optimization.

## 🧠 Data Sources

The platform integrates multiple football data providers:

🌐 FotMob – match metadata, teams, and contextual information.

🌐 WhoScored – detailed event data, lineups, and advanced statistics.

All data is cached locally to improve performance and ensure fast navigation across matches.

<p align="left">
    <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/fotmob.png" width="60" style="margin:0 100px;"/>
  <img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/ws-logo.png" width="100" style="margin:0 50px;"/>
  
</p>

## 🏗️ Architecture

The system is structured into modular layers:

> ### Data Layer

- Match extraction (WhoScored / FotMob).
- Local caching system (JSON-based).
- Data preprocessing pipelines.

> ### Analytics Layer

- xG / xT computation.
- Event classification.
- Tactical transformations.

> ### Visualization Layer

- Streamlit UI components.
- Matplotlib tactical plots.
- Interactive dashboards.

> ### Application Layer

- Multi-page navigation.
- Session state management.
- Dynamic match rendering system.

## 🖥️ Application Pages

<table>
  <tr>
    <td width="60%">

- 🏆 Teams overview
- 👕 Team rosters
- 🏟️ Stadiums & venues
- 📅 Fixtures calendar
- 📊 Match results dashboard
- ⚽ Full match analysis center

This platform is structured as a multi-page analytics system designed for football intelligence exploration.

</td>
<td width="50%" align="left">

<img src="https://raw.githubusercontent.com/CescBlanco/mi_assets/main/sidebar.png" width="15%">

</td>
</tr>
</table>

## ⚙️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge)
![Seaborn](https://img.shields.io/badge/Seaborn-2E4C6D?style=for-the-badge)

> ### ⚽ Football Analytics Engine
- xG (Expected Goals) modeling  
- xT (Expected Threat) modeling  
- Event-based match reconstruction  

> ### 💾 Data Layer
- JSON caching system  
- Match data preprocessing pipeline  


## 📷 What Makes This Project Unique

This platform goes beyond traditional football dashboards.

It is designed as a **football intelligence system** inspired by professional scouting, performance analysis, and tactical analysis workflows used in elite football environments.

### Key capabilities:

- 📖 **Match storytelling engine** built on event-level data
- 🧠 **Tactical intelligence layer** (formations, spacing, passing networks)
- 📊 **Advanced statistical modeling** (xG, xT, possession metrics)
- 🏗️ **Data engineering pipeline** for structured football event processing
## 📦 Future Improvements (Roadmap)

The project is continuously evolving toward a professional-grade football analytics product. Planned enhancements include:

> ### 🧍 Player & Performance Intelligence

- Enhanced Man of the Match visualization module.
- Identification and ranking of top-performing players per match.
- Advanced player impact metrics and comparisons.

> ### 📑 Advanced Reporting System

- Export tactical reports in PNG/PDF format.
- Player-specific, team-specific, and match-specific reports.
- Fully automated scouting-ready report generation.

> ### 🏆 Competition Expansion

- Full integration of knockout stages.
- Bracket visualization for post-group stage progression.
- Tournament flow and advanced competition tracking.

> ### 🔄 Data Automation & Live Integration

- Improved real-time data extraction pipelines.
- More direct and automated integration with data providers.
- Reduced latency between match events and platform updates.

> ### ⚡ Performance Optimization

- General platform performance improvements.
- Faster rendering of complex tactical visualizations.
- Optimization of data processing pipelines.

> ### 🗄️ Scalable Data Infrastructure

- Migration from local files to external database systems.
- Improved scalability and historical data management.
- Better support for large-scale analytics.

> ### 🤖 Machine Learning Integration

- Match outcome prediction models.
- Player performance forecasting.
- Event prediction and probability modeling..
- Advanced data-driven scouting tools.


## 👤 Author

[![GitHub](https://img.shields.io/badge/GitHub-Cesc_Blanco-black?logo=github)](https://github.com/CescBlanco)
[![LinkedIn](https://custom-icon-badges.demolab.com/badge/LinkedIn-Cesc_Blanco-0A66C2?logo=linkedin-white&logoColor=fff)]([#](https://www.linkedin.com/in/cescblanco))
[![Email](https://img.shields.io/badge/Email-Contact%20Me-blue?logo=gmail)](mailto:cesc.blanco@example.com)


## 📊 Data Disclaimer

This project uses publicly available football data sources for educational and analytical purposes.
All data belongs to their respective providers.

## ⚽ Final Note

This platform bridges football intuition and data science, delivering a complete analytical experience from macro competition overview to micro tactical detail.


## License

MIT License — see LICENSE file for details.