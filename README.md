# Fantasy Football Draft Assistant

An AI-powered fantasy football draft assistant that uses **XGBoost machine learning** to provide intelligent pick recommendations based on current draft state, positional needs, and value gaps.

## 🚀 Features

### Core Functionality
- **XGBoost AI Model**: Trained on expert rankings to predict player value and identify optimal picks
- **Dynamic Draft Tracking**: Real-time tracking of all picks, team rosters, and draft position
- **Intelligent Recommendations**: AI-powered suggestions based on:
  - Your team's positional needs
  - Available player value
  - Position scarcity
  - Expert rankings vs. current draft position
- **Flexible Draft Formats**: Support for any combination of positions (QB, RB, WR, TE, FLEX, SUPER_FLEX, DST, K)

### Technical Features
- **REST API**: FastAPI backend with comprehensive endpoints
- **Command Line Interface**: Interactive CLI for testing and direct use
- **State Management**: Export/import draft state for persistence
- **Real-time Updates**: Live tracking of draft progress and team needs

## 🏗️ Architecture

The system consists of three main components:

1. **`DraftAssistant` Class** (`draft_assistant.py`): Core AI engine with XGBoost model
2. **FastAPI Server** (`api_server.py`): REST API for web/mobile integration
3. **CLI Interface** (`cli_demo.py`): Command-line testing and direct use

### XGBoost Model Features
The AI model considers:
- Player position and team
- Position-specific rankings
- Overall value scores
- Position scarcity
- Expert ranking vs. current draft position

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Requirements
- Place `REDRAFT-rankings.csv` in the project directory
- CSV should have columns: `Name`, `Team`, `Position`, `Expert_Rank`

## 🚀 Quick Start

### Option 1: Command Line Interface (Recommended for testing)
```bash
python cli_demo.py
```

The CLI will guide you through:
1. Setting draft format (how many of each position)
2. Setting draft parameters (total teams, your team number)
3. Recording picks as they happen
4. Getting AI-powered recommendations
5. Viewing draft summaries and available players

### Option 2: FastAPI Web Server
```bash
python api_server.py
```

The server will start on `http://localhost:8000` with:
- Interactive API docs at `/docs`
- Health check at `/health`
- All draft management endpoints

## 📚 API Endpoints

### Core Draft Management
- `POST /draft/format` - Set draft format (positions and counts)
- `POST /draft/parameters` - Set draft parameters (teams, your team)
- `POST /draft/pick` - Record a pick
- `GET /draft/recommendations` - Get AI recommendations
- `GET /draft/summary` - Get current draft state

### Player Management
- `GET /draft/available` - List available players
- `GET /players/search` - Search players by name
- `GET /draft/export` - Export draft state
- `POST /draft/import` - Import draft state

## 💡 Usage Examples

### Setting Up a 12-Team PPR League
```python
from draft_assistant import DraftAssistant

# Initialize
da = DraftAssistant()

# Set format: 1 QB, 2 RB, 3 WR, 1 TE, 1 FLEX, 1 DST, 1 K
da.set_draft_format({
    'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 
    'FLEX': 1, 'DST': 1, 'K': 1
})

# Set draft parameters
da.set_draft_parameters(total_teams=12, current_team=5)
```

### Recording Picks
```python
# Record picks as they happen
da.record_pick("Ja'Marr Chase", team_number=1, is_your_pick=False)
da.record_pick("Bijan Robinson", team_number=2, is_your_pick=False)
da.record_pick("CeeDee Lamb", team_number=3, is_your_pick=False)
da.record_pick("Jahmyr Gibbs", team_number=4, is_your_pick=False)
da.record_pick("Saquon Barkley", team_number=5, is_your_pick=True)  # Your pick!
```

### Getting Recommendations
```python
# Get top 5 recommendations
recommendations = da.get_recommendations(5)

for rec in recommendations:
    print(f"{rec['rank']}. {rec['player_name']} ({rec['position']})")
    print(f"    Score: {rec['recommendation_score']:.4f}")
    print(f"    Reasoning: {rec['reasoning']}")
```

## 🧠 How the AI Works

### Feature Engineering
The XGBoost model uses these features:
- **Position Encoding**: Numerical representation of player positions
- **Team Encoding**: Numerical representation of NFL teams
- **Position Rank**: Player's rank within their position
- **Overall Rank**: Player's rank across all positions
- **Value Score**: Inverse of expert rank (higher = better value)
- **Position Value**: Value rank within position

### Recommendation Algorithm
1. **Base Score**: Derived from expert ranking
2. **Position Need Bonus**: Higher for positions you need
3. **Value Bonus**: Higher for players with better value scores
4. **Scarcity Bonus**: Higher when few players remain at a position
5. **Final Score**: Weighted combination of all factors

### Reasoning Generation
The system provides human-readable explanations:
- "Need RB players" - Position requirement
- "Top-tier talent" - High expert ranking
- "Only 3 RB players left" - Position scarcity
- "Drafting below ADP" - Value opportunity

## 🔧 Configuration

### Draft Format Examples

**Standard PPR (12 teams):**
```json
{
  "QB": 1, "RB": 2, "WR": 3, "TE": 1, 
  "FLEX": 1, "DST": 1, "K": 1
}
```

**Superflex League (12 teams):**
```json
{
  "QB": 2, "RB": 2, "WR": 3, "TE": 1, 
  "SUPER_FLEX": 1, "DST": 1, "K": 1
}
```

**Best Ball (10 teams):**
```json
{
  "QB": 2, "RB": 4, "WR": 6, "TE": 2, 
  "DST": 1, "K": 1
}
```

## 📊 Data Structure

### Player Rankings CSV
```csv
Name,Team,Position,Expert Rank
Ja'Marr Chase,CIN,WR,1.00
Bijan Robinson,ATL,RB,2.83
CeeDee Lamb,DAL,WR,3.33
...
```

### Draft State Export
```json
{
  "draft_state": {
    "round": 3,
    "pick": 7,
    "total_teams": 12,
    "draft_format": {...},
    "drafted_players": [...],
    "team_rosters": {...},
    "current_team": 5
  }
}
```

## 🚨 Troubleshooting

### Common Issues

**"Player not found in rankings"**
- Check spelling of player names
- Ensure CSV file is properly formatted
- Verify player exists in the rankings

**"No recommendations available"**
- Set draft format first
- Set draft parameters
- Ensure you have remaining positional needs

**Import/Export errors**
- Check file permissions
- Verify JSON format is valid
- Ensure file paths are correct

### Performance Tips
- For large drafts (16+ teams), consider increasing XGBoost parameters
- Export draft state periodically for backup
- Use position filters when viewing available players

## 🔮 Future Enhancements

Potential improvements:
- **Multi-league Support**: Manage multiple drafts simultaneously
- **Advanced Analytics**: Draft efficiency metrics and post-draft analysis
- **Custom Scoring**: Support for different league scoring systems
- **Trade Analysis**: Evaluate potential trades during draft
- **Mobile App**: Native mobile interface
- **Real-time Sync**: Live draft room integration

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional machine learning models
- Enhanced feature engineering
- Better UI/UX
- Performance optimizations
- Additional draft formats

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs` when running the server
3. Test with the CLI interface first
4. Check logs for detailed error messages

---

**Good luck with your draft! 🏈**
