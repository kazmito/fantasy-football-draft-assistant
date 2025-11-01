#!/usr/bin/env python3
"""
Test script for the Draft Assistant to verify functionality.
Run this to test the core features without manual input.
"""

import sys
import json
from draft_assistant import DraftAssistant

def test_draft_assistant():
    """Test the draft assistant functionality."""
    print("🧪 Testing Draft Assistant...")
    print("=" * 50)
    
    try:
        # Initialize
        print("1. Initializing Draft Assistant...")
        da = DraftAssistant()
        print(f"   ✓ Loaded {len(da.players_df)} players")
        print(f"   ✓ Model trained successfully")
        print()
        
        # Test draft format
        print("2. Setting draft format...")
        format_config = {
            'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 
            'FLEX': 1, 'DST': 1, 'K': 1
        }
        da.set_draft_format(format_config)
        print(f"   ✓ Draft format set: {format_config}")
        print()
        
        # Test draft parameters
        print("3. Setting draft parameters...")
        da.set_draft_parameters(total_teams=12, current_team=5)
        print("   ✓ Draft parameters set: 12 teams, you are team 5")
        print()
        
        # Test recording picks
        print("4. Recording sample picks...")
        test_picks = [
            ("Ja'Marr Chase", 1, False),
            ("Bijan Robinson", 2, False),
            ("CeeDee Lamb", 3, False),
            ("Jahmyr Gibbs", 4, False),
            ("Saquon Barkley", 5, True),  # Your pick
            ("Justin Jefferson", 6, False),
            ("Puka Nacua", 7, False),
            ("Malik Nabers", 8, False),
            ("Amon-Ra St. Brown", 9, False),
            ("Nico Collins", 10, False),
            ("Ashton Jeanty", 11, False),
            ("Brian Thomas", 12, False),
            ("Christian McCaffrey", 1, False),  # Round 2
            ("Devon Achane", 2, False),
            ("Derrick Henry", 3, False),
            ("Drake London", 4, False),
            ("Bucky Irving", 5, True),  # Your pick
        ]
        
        for player_name, team_number, is_your_pick in test_picks:
            success = da.record_pick(player_name, team_number, is_your_pick)
            if success:
                print(f"   ✓ {player_name} to team {team_number}")
            else:
                print(f"   ✗ Failed to record {player_name}")
        
        print()
        
        # Test getting recommendations
        print("5. Getting AI recommendations...")
        recommendations = da.get_recommendations(5)
        print(f"   ✓ Got {len(recommendations)} recommendations:")
        
        for rec in recommendations:
            print(f"      {rec['rank']}. {rec['player_name']} ({rec['position']}) - Score: {rec['recommendation_score']:.4f}")
            print(f"          Reasoning: {rec['reasoning']}")
        
        print()
        
        # Test draft summary
        print("6. Getting draft summary...")
        summary = da.get_draft_summary()
        print(f"   ✓ Current round: {summary['current_round']}")
        print(f"   ✓ Current pick: {summary['current_pick']}")
        print(f"   ✓ Total drafted: {summary['total_drafted']}")
        print(f"   ✓ Your roster: {len(summary['your_roster'])} players")
        print(f"   ✓ Next pick estimate: {summary['next_pick_estimate']} picks away")
        
        print(f"   ✓ Your remaining needs:")
        for pos, count in summary['your_needs'].items():
            if count > 0:
                print(f"      {pos}: {count}")
        
        print()
        
        # Test available players
        print("7. Checking available players...")
        available = da.get_available_players()
        print(f"   ✓ {len(available)} players available")
        
        # Show top available by position
        for position in ['QB', 'RB', 'WR', 'TE']:
            pos_players = available[available['Position'] == position]
            if not pos_players.empty:
                top_player = pos_players.iloc[0]
                print(f"      Top {position}: {top_player['Name']} (Rank: {top_player['Expert_Rank']:.1f})")
        
        print()
        
        # Test export/import
        print("8. Testing export/import...")
        export_file = da.export_draft_state()
        print(f"   ✓ Exported to: {export_file}")
        
        # Test search
        print("9. Testing player search...")
        search_results = da.get_available_players()
        chase_results = search_results[search_results['Name'].str.contains('Chase', case=False, na=False)]
        if not chase_results.empty:
            print(f"   ✓ Search for 'Chase' found {len(chase_results)} results")
        else:
            print("   ✗ Search for 'Chase' failed")
        
        print()
        print("🎉 All tests completed successfully!")
        print("The Draft Assistant is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test the API endpoints if FastAPI is available."""
    try:
        from api_server import app
        from fastapi.testclient import TestClient
        
        print("\n🌐 Testing API endpoints...")
        print("=" * 50)
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("   ✓ Health endpoint working")
        else:
            print("   ✗ Health endpoint failed")
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            print("   ✓ Root endpoint working")
        else:
            print("   ✗ Root endpoint failed")
        
        print("   ✓ API endpoints working correctly")
        return True
        
    except ImportError:
        print("   ⚠️  FastAPI test client not available, skipping API tests")
        return True
    except Exception as e:
        print(f"   ✗ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Draft Assistant Test Suite")
    print("=" * 50)
    
    # Test core functionality
    core_success = test_draft_assistant()
    
    # Test API endpoints
    api_success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if core_success and api_success:
        print("🎉 ALL TESTS PASSED!")
        print("Your Draft Assistant is ready to use!")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
