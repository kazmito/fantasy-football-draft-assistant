#!/usr/bin/env python3
"""
Command-line interface demo for the Draft Assistant.
This allows you to test the core functionality without the web API.
"""

import sys
import json
from draft_assistant import DraftAssistant

def print_header():
    """Print a nice header for the CLI."""
    print("=" * 60)
    print("           FANTASY FOOTBALL DRAFT ASSISTANT")
    print("           Powered by XGBoost AI")
    print("=" * 60)
    print()

def print_menu():
    """Print the main menu options."""
    print("Main Menu:")
    print("1. Set Draft Format")
    print("2. Set Draft Parameters")
    print("3. Record a Pick")
    print("4. Get Recommendations")
    print("5. View Draft Summary")
    print("6. View Available Players")
    print("7. Search Players")
    print("8. Export Draft State")
    print("9. Import Draft State")
    print("0. Exit")
    print()

def get_draft_format():
    """Get draft format from user input."""
    print("\nEnter the number of players needed for each position:")
    
    try:
        qb = int(input("Quarterbacks (QB): "))
        rb = int(input("Running Backs (RB): "))
        wr = int(input("Wide Receivers (WR): "))
        te = int(input("Tight Ends (TE): "))
        flex = int(input("Flex positions (FLEX): "))
        super_flex = int(input("Super Flex positions (SUPER_FLEX): "))
        dst = int(input("Defense/Special Teams (DST): "))
        k = int(input("Kickers (K): "))
        
        return {
            'QB': qb,
            'RB': rb,
            'WR': wr,
            'TE': te,
            'FLEX': flex,
            'SUPER_FLEX': super_flex,
            'DST': dst,
            'K': k
        }
    except ValueError:
        print("Please enter valid numbers.")
        return None

def get_draft_parameters():
    """Get draft parameters from user input."""
    try:
        total_teams = int(input("Total number of teams in draft: "))
        current_team = int(input("Your team number (1-based): "))
        
        if current_team < 1 or current_team > total_teams:
            print("Invalid team number. Must be between 1 and total teams.")
            return None
            
        return total_teams, current_team
    except ValueError:
        print("Please enter valid numbers.")
        return None

def record_pick(draft_assistant):
    """Record a pick from user input."""
    print("\nRecord a Pick:")
    
    player_name = input("Player name: ").strip()
    if not player_name:
        print("Player name cannot be empty.")
        return
    
    try:
        team_number = int(input("Team number that made the pick: "))
    except ValueError:
        print("Please enter a valid team number.")
        return
    
    is_your_pick = input("Was this your pick? (y/n): ").lower().startswith('y')
    
    success = draft_assistant.record_pick(
        player_name=player_name,
        team_number=team_number,
        is_your_pick=is_your_pick
    )
    
    if success:
        print(f"✓ Pick recorded: {player_name} to team {team_number}")
    else:
        print(f"✗ Failed to record pick for {player_name}")

def show_recommendations(draft_assistant):
    """Show draft recommendations."""
    try:
        num_recs = int(input("Number of recommendations (default 5): ") or "5")
    except ValueError:
        num_recs = 5
    
    print(f"\nGetting {num_recs} recommendations...")
    recommendations = draft_assistant.get_recommendations(num_recs)
    
    if not recommendations:
        print("No recommendations available. Make sure you've set the draft format and parameters.")
        return
    
    print(f"\nTop {len(recommendations)} Recommendations:")
    print("-" * 80)
    
    for rec in recommendations:
        print(f"{rec['rank']}. {rec['player_name']} ({rec['position']} - {rec['team']})")
        print(f"    Expert Rank: {rec['expert_rank']:.1f} | Score: {rec['recommendation_score']:.4f}")
        print(f"    Reasoning: {rec['reasoning']}")
        print()

def show_draft_summary(draft_assistant):
    """Show current draft summary."""
    summary = draft_assistant.get_draft_summary()
    
    print("\nDraft Summary:")
    print("=" * 50)
    print(f"Current Round: {summary['current_round']}")
    print(f"Current Pick: {summary['current_pick']}")
    print(f"Your Team: {summary['your_team']}")
    print(f"Total Drafted: {summary['total_drafted']}")
    print(f"Next Pick Estimate: {summary['next_pick_estimate']} picks away")
    
    print(f"\nYour Roster ({len(summary['your_roster'])} players):")
    if summary['your_roster']:
        for pick in summary['your_roster']:
            print(f"  {pick['player_name']} ({pick['position']}) - Round {pick['round']}.{pick['pick']}")
    else:
        print("  No players drafted yet")
    
    print(f"\nYour Remaining Needs:")
    for pos, count in summary['your_needs'].items():
        if count > 0:
            print(f"  {pos}: {count}")
    
    print(f"\nDraft Format:")
    for pos, count in summary['draft_format'].items():
        print(f"  {pos}: {count}")

def show_available_players(draft_assistant):
    """Show available players."""
    try:
        limit = int(input("Number of players to show (default 20): ") or "20")
    except ValueError:
        limit = 20
    
    position = input("Filter by position (QB/RB/WR/TE, or press Enter for all): ").strip().upper()
    
    available = draft_assistant.get_available_players()
    
    if position and position in ['QB', 'RB', 'WR', 'TE']:
        available = available[available['Position'] == position]
        print(f"\nAvailable {position} Players (showing top {limit}):")
    else:
        print(f"\nAll Available Players (showing top {limit}):")
    
    print("-" * 80)
    
    for i, (_, player) in enumerate(available.head(limit).iterrows()):
        print(f"{i+1:2d}. {player['Name']:<25} {player['Position']:<3} {player['Team']:<3} Rank: {player['Expert_Rank']:6.1f}")
    
    print(f"\nTotal available: {len(available)} players")

def search_players(draft_assistant):
    """Search for players by name."""
    query = input("Enter player name to search: ").strip()
    if not query:
        print("Please enter a search query.")
        return
    
    try:
        limit = int(input("Maximum results (default 10): ") or "10")
    except ValueError:
        limit = 10
    
    print(f"\nSearching for '{query}'...")
    
    # Use the search functionality from the API
    available = draft_assistant.get_available_players()
    search_results = available[available['Name'].str.contains(query, case=False, na=False)]
    
    if len(search_results) < limit:
        all_players = draft_assistant.players_df
        all_results = all_players[all_players['Name'].str.contains(query, case=False, na=False)]
        search_results = pd.concat([search_results, all_results]).drop_duplicates(subset=['Name'])
    
    limited = search_results.head(limit)
    
    if limited.empty:
        print(f"No players found matching '{query}'")
        return
    
    print(f"\nSearch Results for '{query}':")
    print("-" * 80)
    
    for i, (_, player) in enumerate(limited.iterrows()):
        is_available = player['Name'] not in [pick['player_name'] for pick in draft_assistant.draft_state['drafted_players']]
        status = "✓ Available" if is_available else "✗ Drafted"
        
        print(f"{i+1:2d}. {player['Name']:<25} {player['Position']:<3} {player['Team']:<3} Rank: {player['Expert_Rank']:6.1f} {status}")

def export_draft_state(draft_assistant):
    """Export current draft state."""
    filename = draft_assistant.export_draft_state()
    print(f"\n✓ Draft state exported to: {filename}")

def import_draft_state(draft_assistant):
    """Import draft state from file."""
    filename = input("Enter filename to import from: ").strip()
    if not filename:
        print("Please enter a filename.")
        return
    
    success = draft_assistant.import_draft_state(filename)
    if success:
        print(f"✓ Draft state imported from: {filename}")
    else:
        print(f"✗ Failed to import from: {filename}")

def main():
    """Main CLI loop."""
    print_header()
    
    try:
        print("Initializing Draft Assistant...")
        draft_assistant = DraftAssistant()
        print("✓ Draft Assistant initialized successfully!")
        print()
        
    except Exception as e:
        print(f"✗ Failed to initialize Draft Assistant: {e}")
        print("Make sure REDRAFT-rankings.csv is in the current directory.")
        sys.exit(1)
    
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (0-9): ").strip()
            
            if choice == '0':
                print("\nGoodbye! Good luck with your draft!")
                break
            elif choice == '1':
                format_config = get_draft_format()
                if format_config:
                    draft_assistant.set_draft_format(format_config)
                    print("✓ Draft format set successfully!")
            elif choice == '2':
                params = get_draft_parameters()
                if params:
                    total_teams, current_team = params
                    draft_assistant.set_draft_parameters(total_teams, current_team)
                    print("✓ Draft parameters set successfully!")
            elif choice == '3':
                record_pick(draft_assistant)
            elif choice == '4':
                show_recommendations(draft_assistant)
            elif choice == '5':
                show_draft_summary(draft_assistant)
            elif choice == '6':
                show_available_players(draft_assistant)
            elif choice == '7':
                search_players(draft_assistant)
            elif choice == '8':
                export_draft_state(draft_assistant)
            elif choice == '9':
                import_draft_state(draft_assistant)
            else:
                print("Invalid choice. Please enter a number between 0-9.")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Good luck with your draft!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
        
        input("\nPress Enter to continue...")
        print()

if __name__ == "__main__":
    main()
