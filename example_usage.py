#!/usr/bin/env python3
"""
Example script showing how to use the Draft Assistant programmatically.
This demonstrates the core functionality in a script format.
"""

from draft_assistant import DraftAssistant
import json

def main():
    """Example usage of the Draft Assistant."""
    print("🏈 Fantasy Football Draft Assistant - Example Usage")
    print("=" * 60)
    
    # Initialize the draft assistant
    print("1. Initializing Draft Assistant...")
    da = DraftAssistant()
    print(f"   ✓ Loaded {len(da.players_df)} players")
    print(f"   ✓ XGBoost model trained and ready")
    print()
    
    # Set up a 12-team PPR league format
    print("2. Setting up 12-team PPR league format...")
    ppr_format = {
        'QB': 1,      # 1 Quarterback
        'RB': 2,      # 2 Running Backs
        'WR': 3,      # 3 Wide Receivers
        'TE': 1,      # 1 Tight End
        'FLEX': 1,    # 1 Flex position
        'DST': 1,     # 1 Defense/Special Teams
        'K': 1        # 1 Kicker
    }
    da.set_draft_format(ppr_format)
    print(f"   ✓ Format set: {ppr_format}")
    print()
    
    # Set draft parameters
    print("3. Setting draft parameters...")
    da.set_draft_parameters(total_teams=12, current_team=5)
    print("   ✓ 12 teams, you are team 5")
    print()
    
    # Simulate the first few rounds of a draft
    print("4. Simulating first few rounds...")
    
    # Round 1
    round1_picks = [
        ("Ja'Marr Chase", 1, False),      # Team 1
        ("Bijan Robinson", 2, False),     # Team 2
        ("CeeDee Lamb", 3, False),       # Team 3
        ("Jahmyr Gibbs", 4, False),      # Team 4
        ("Saquon Barkley", 5, True),     # Your pick!
        ("Justin Jefferson", 6, False),   # Team 6
        ("Puka Nacua", 7, False),        # Team 7
        ("Malik Nabers", 8, False),      # Team 8
        ("Amon-Ra St. Brown", 9, False), # Team 9
        ("Nico Collins", 10, False),     # Team 10
        ("Ashton Jeanty", 11, False),    # Team 11
        ("Brian Thomas", 12, False),     # Team 12
    ]
    
    for player, team, is_yours in round1_picks:
        da.record_pick(player, team, is_yours)
        if is_yours:
            print(f"   ✓ You drafted: {player}")
        else:
            print(f"   - {player} → Team {team}")
    
    print()
    
    # Round 2 (snake draft - reverse order)
    print("5. Round 2 (snake draft)...")
    round2_picks = [
        ("Christian McCaffrey", 12, False), # Team 12
        ("Devon Achane", 11, False),        # Team 11
        ("Derrick Henry", 10, False),       # Team 10
        ("Drake London", 9, False),         # Team 9
        ("Bucky Irving", 8, False),         # Team 8
        ("A.J. Brown", 7, False),           # Team 7
        ("Chase Brown", 6, False),          # Team 6
        ("Jonathan Taylor", 5, True),       # Your pick!
        ("Ladd McConkey", 4, False),        # Team 4
        ("Josh Jacobs", 3, False),          # Team 3
        ("Brock Bowers", 2, False),         # Team 2
        ("Omarion Hampton", 1, False),      # Team 1
    ]
    
    for player, team, is_yours in round2_picks:
        da.record_pick(player, team, is_yours)
        if is_yours:
            print(f"   ✓ You drafted: {player}")
        else:
            print(f"   - {player} → Team {team}")
    
    print()
    
    # Get current draft summary
    print("6. Current draft status...")
    summary = da.get_draft_summary()
    print(f"   ✓ Round: {summary['current_round']}")
    print(f"   ✓ Pick: {summary['current_pick']}")
    print(f"   ✓ Total drafted: {summary['total_drafted']}")
    print(f"   ✓ Your roster: {len(summary['your_roster'])} players")
    
    print(f"   ✓ Your roster:")
    for pick in summary['your_roster']:
        print(f"      Round {pick['round']}.{pick['pick']}: {pick['player_name']} ({pick['position']})")
    
    print(f"   ✓ Your remaining needs:")
    for pos, count in summary['your_needs'].items():
        if count > 0:
            print(f"      {pos}: {count}")
    
    print()
    
    # Get AI recommendations for your next pick
    print("7. AI recommendations for your next pick...")
    recommendations = da.get_recommendations(5)
    
    print(f"   Top {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"   {rec['rank']}. {rec['player_name']} ({rec['position']} - {rec['team']})")
        print(f"       Expert Rank: {rec['expert_rank']:.1f} | Score: {rec['recommendation_score']:.4f}")
        print(f"       Reasoning: {rec['reasoning']}")
        print()
    
    # Show available players by position
    print("8. Available players by position...")
    available = da.get_available_players()
    
    for position in ['QB', 'RB', 'WR', 'TE']:
        pos_players = available[available['Position'] == position]
        if not pos_players.empty:
            print(f"   Top available {position}:")
            for i, (_, player) in enumerate(pos_players.head(3).iterrows()):
                print(f"      {i+1}. {player['Name']} (Rank: {player['Expert_Rank']:.1f})")
            print()
    
    # Export draft state
    print("9. Exporting draft state...")
    export_file = da.export_draft_state()
    print(f"   ✓ Draft state saved to: {export_file}")
    
    # Show some statistics
    print("\n10. Draft statistics...")
    total_players = len(da.players_df)
    drafted_players = len(da.draft_state['drafted_players'])
    remaining_players = total_players - drafted_players
    
    print(f"   ✓ Total players in rankings: {total_players}")
    print(f"   ✓ Players drafted: {drafted_players}")
    print(f"   ✓ Players remaining: {remaining_players}")
    print(f"   ✓ Draft completion: {(drafted_players/total_players)*100:.1f}%")
    
    print("\n🎉 Example completed successfully!")
    print("Your Draft Assistant is working perfectly!")
    
    return da

if __name__ == "__main__":
    try:
        draft_assistant = main()
        print("\n💡 You can now:")
        print("   - Use the CLI: python cli_demo.py")
        print("   - Start the API server: python api_server.py")
        print("   - Run tests: python test_draft_assistant.py")
        print("   - Import this script in your own code")
        
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
