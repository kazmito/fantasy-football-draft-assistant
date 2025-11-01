from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from draft_assistant import DraftAssistant
from typing import List, Dict, Optional
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Draft Assistant Web Interface",
    description="User-friendly web interface for the AI-powered draft assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize draft assistant
try:
    draft_assistant = DraftAssistant()
    logger.info("Draft Assistant initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Draft Assistant: {e}")
    draft_assistant = None

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Main dashboard page."""
    if draft_assistant is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Draft Assistant failed to initialize"
        })
    
    # Get current draft state
    summary = draft_assistant.get_draft_summary()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "summary": summary,
        "draft_assistant": draft_assistant
    })

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    """Draft setup page."""
    return templates.TemplateResponse("setup.html", {"request": request})

@app.post("/setup/format")
async def setup_draft_format(
    qb: int = Form(...),
    rb: int = Form(...),
    wr: int = Form(...),
    te: int = Form(...),
    flex: int = Form(default=0),
    super_flex: int = Form(default=0),
    dst: int = Form(default=1),
    k: int = Form(default=1)
):
    """Set the draft format."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        format_config = {
            'QB': qb, 'RB': rb, 'WR': wr, 'TE': te,
            'FLEX': flex, 'SUPER_FLEX': super_flex,
            'DST': dst, 'K': k
        }
        
        draft_assistant.set_draft_format(format_config)
        return {"success": True, "format": format_config}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/setup/parameters")
async def setup_draft_parameters(
    total_teams: int = Form(...),
    current_team: int = Form(...)
):
    """Set draft parameters."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        draft_assistant.set_draft_parameters(total_teams, current_team)
        return {"success": True}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/draft", response_class=HTMLResponse)
async def draft_page(request: Request):
    """Main draft interface."""
    if draft_assistant is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Draft Assistant not initialized"
        })
    
    # Get current state
    summary = draft_assistant.get_draft_summary()
    recommendations = draft_assistant.get_recommendations(10)
    available = draft_assistant.get_available_players()
    
    return templates.TemplateResponse("draft.html", {
        "request": request,
        "summary": summary,
        "recommendations": recommendations,
        "available": available
    })

@app.get("/api/recommendations")
async def get_recommendations_api():
    """Get AI recommendations or best available players based on whose turn it is."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        if draft_assistant.is_your_turn():
            # It's your turn - show AI-powered recommendations
            data = draft_assistant.get_recommendations(10)
            return {
                "success": True, 
                "recommendations": data,
                "type": "ai_recommendations",
                "message": "AI-powered recommendations for your team"
            }
        else:
            # It's not your turn - show best available players
            data = draft_assistant.get_best_available_players(10)
            return {
                "success": True, 
                "recommendations": data,
                "type": "best_available",
                "message": "Best available players (not your turn)"
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/available-players")
async def get_available_players_api(position: Optional[str] = None):
    """Get available players."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        available = draft_assistant.get_available_players()
        
        if position and position.upper() in ['QB', 'RB', 'WR', 'TE']:
            available = available[available['Position'] == position.upper()]
        
        # Convert to list of dicts
        players = []
        for _, player in available.head(50).iterrows():
            players.append({
                "name": player['Name'],
                "position": player['Position'],
                "team": player['Team'],
                "expert_rank": player['Expert_Rank']
            })
        
        return {"success": True, "players": players}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/record-pick")
async def record_pick_api(
    player_name: str = Form(...),
    team_number: int = Form(default=None),
    is_your_pick: bool = Form(default=None)
):
    """Record a pick."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        # Convert form data to proper types
        team_num = int(team_number) if team_number else None
        is_your = bool(is_your_pick) if is_your_pick is not None else None
        
        success = draft_assistant.record_pick(player_name, team_num, is_your)
        
        if success:
            # Get the calculated values for the response
            summary = draft_assistant.get_draft_summary()
            calculated_team = draft_assistant._calculate_current_team()
            calculated_is_yours = (calculated_team == draft_assistant.draft_state['current_team'])
            
            return {
                "success": True, 
                "message": f"Pick recorded: {player_name} to Team {calculated_team}",
                "team_number": calculated_team,
                "is_your_pick": calculated_is_yours,
                "round": summary['current_round'],
                "pick": summary['current_pick']
            }
        else:
            return {"success": False, "error": f"Player {player_name} not found"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/search-players")
async def search_players_api(query: str, limit: int = 20):
    """Search for players."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        available = draft_assistant.get_available_players()
        search_results = available[available['Name'].str.contains(query, case=False, na=False)]
        
        players = []
        for _, player in search_results.head(limit).iterrows():
            players.append({
                "name": player['Name'],
                "position": player['Position'],
                "team": player['Team'],
                "expert_rank": player['Expert_Rank']
            })
        
        return {"success": True, "players": players, "count": len(players)}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/draft-summary")
async def get_draft_summary_api():
    """Get current draft summary."""
    if draft_assistant is None:
        return {"success": False, "error": "Draft Assistant not initialized"}
    
    try:
        summary = draft_assistant.get_draft_summary()
        return {"success": True, "summary": summary}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
