from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import logging
from draft_assistant import DraftAssistant
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Draft Assistant API",
    description="AI-powered fantasy football draft assistant using XGBoost",
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

# Pydantic models for request/response
class DraftFormatRequest(BaseModel):
    qb: int
    rb: int
    wr: int
    te: int
    flex: int = 0
    super_flex: int = 0
    dst: int = 1
    k: int = 1

class DraftParametersRequest(BaseModel):
    total_teams: int
    current_team: int = 1

class PickRequest(BaseModel):
    player_name: str
    team_number: int
    is_your_pick: bool = False

class RecommendationRequest(BaseModel):
    num_recommendations: int = 5

class PlayerInfo(BaseModel):
    name: str
    position: str
    team: str
    expert_rank: float

class Recommendation(BaseModel):
    rank: int
    player_name: str
    position: str
    team: str
    expert_rank: float
    recommendation_score: float
    reasoning: str

class DraftSummary(BaseModel):
    current_round: int
    current_pick: int
    your_team: int
    your_roster: List[Dict]
    your_needs: Dict[str, int]
    total_drafted: int
    draft_format: Dict[str, int]
    next_pick_estimate: int

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Draft Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/docs - API documentation",
            "/health - Health check",
            "/draft/format - Set draft format",
            "/draft/parameters - Set draft parameters",
            "/draft/pick - Record a pick",
            "/draft/recommendations - Get recommendations",
            "/draft/summary - Get draft summary",
            "/draft/available - Get available players",
            "/draft/export - Export draft state",
            "/draft/import - Import draft state"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    return {
        "status": "healthy",
        "draft_assistant_ready": draft_assistant is not None,
        "total_players": len(draft_assistant.players_df) if draft_assistant else 0
    }

@app.post("/draft/format")
async def set_draft_format(request: DraftFormatRequest):
    """Set the draft format (how many players of each position)."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        format_config = {
            'QB': request.qb,
            'RB': request.rb,
            'WR': request.wr,
            'TE': request.te,
            'FLEX': request.flex,
            'SUPER_FLEX': request.super_flex,
            'DST': request.dst,
            'K': request.k
        }
        
        draft_assistant.set_draft_format(format_config)
        
        return {
            "message": "Draft format set successfully",
            "format": format_config
        }
    
    except Exception as e:
        logger.error(f"Error setting draft format: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft/parameters")
async def set_draft_parameters(request: DraftParametersRequest):
    """Set the draft parameters (total teams, your team number)."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        draft_assistant.set_draft_parameters(
            total_teams=request.total_teams,
            current_team=request.current_team
        )
        
        return {
            "message": "Draft parameters set successfully",
            "total_teams": request.total_teams,
            "current_team": request.current_team
        }
    
    except Exception as e:
        logger.error(f"Error setting draft parameters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft/pick")
async def record_pick(request: PickRequest):
    """Record a pick that was made in the draft."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        success = draft_assistant.record_pick(
            player_name=request.player_name,
            team_number=request.team_number,
            is_your_pick=request.is_your_pick
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=f"Player {request.player_name} not found in rankings")
        
        return {
            "message": "Pick recorded successfully",
            "player": request.player_name,
            "team": request.team_number,
            "is_your_pick": request.is_your_pick
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording pick: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get draft recommendations based on current state and team needs."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        recommendations = draft_assistant.get_recommendations(
            num_recommendations=request.num_recommendations
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/draft/summary")
async def get_draft_summary():
    """Get a summary of the current draft state."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        summary = draft_assistant.get_draft_summary()
        return summary
    
    except Exception as e:
        logger.error(f"Error getting draft summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/draft/available")
async def get_available_players(position: Optional[str] = None, limit: int = 50):
    """Get list of available players, optionally filtered by position."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        available = draft_assistant.get_available_players()
        
        if position:
            available = available[available['Position'] == position.upper()]
        
        # Limit results and convert to list of dicts
        limited = available.head(limit)
        players = []
        
        for _, player in limited.iterrows():
            players.append({
                "name": player['Name'],
                "position": player['Position'],
                "team": player['Team'],
                "expert_rank": player['Expert_Rank']
            })
        
        return {
            "players": players,
            "total_available": len(available),
            "filtered_count": len(players)
        }
    
    except Exception as e:
        logger.error(f"Error getting available players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/draft/export")
async def export_draft_state():
    """Export the current draft state to a JSON file."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        filename = draft_assistant.export_draft_state()
        
        return {
            "message": "Draft state exported successfully",
            "filename": filename
        }
    
    except Exception as e:
        logger.error(f"Error exporting draft state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/draft/import")
async def import_draft_state(filename: str):
    """Import a draft state from a JSON file."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        success = draft_assistant.import_draft_state(filename)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to import draft state")
        
        return {
            "message": "Draft state imported successfully",
            "filename": filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing draft state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players/search")
async def search_players(query: str, limit: int = 10):
    """Search for players by name."""
    if draft_assistant is None:
        raise HTTPException(status_code=503, detail="Draft Assistant not initialized")
    
    try:
        # Search in available players first
        available = draft_assistant.get_available_players()
        search_results = available[available['Name'].str.contains(query, case=False, na=False)]
        
        # Also search in all players if not enough results
        if len(search_results) < limit:
            all_players = draft_assistant.players_df
            all_results = all_players[all_players['Name'].str.contains(query, case=False, na=False)]
            search_results = pd.concat([search_results, all_results]).drop_duplicates(subset=['Name'])
        
        # Limit and format results
        limited = search_results.head(limit)
        players = []
        
        for _, player in limited.iterrows():
            is_available = player['Name'] not in [pick['player_name'] for pick in draft_assistant.draft_state['drafted_players']]
            
            players.append({
                "name": player['Name'],
                "position": player['Position'],
                "team": player['Team'],
                "expert_rank": player['Expert_Rank'],
                "available": is_available
            })
        
        return {
            "players": players,
            "query": query,
            "total_found": len(search_results),
            "returned_count": len(players)
        }
    
    except Exception as e:
        logger.error(f"Error searching players: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
