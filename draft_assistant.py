import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DraftAssistant:
    """
    A comprehensive draft assistant that uses XGBoost to provide intelligent pick recommendations
    based on current draft state, positional needs, and value gaps.
    """
    
    def __init__(self, rankings_file: str = "REDRAFT-rankings.csv"):
        """
        Initialize the draft assistant with player rankings and train the XGBoost model.
        
        Args:
            rankings_file: Path to the CSV file containing player rankings
        """
        self.rankings_file = rankings_file
        self.players_df = None
        self.model = None
        self.label_encoders = {}
        self.draft_state = {
            'round': 1,
            'pick': 1,
            'total_teams': 12,
            'draft_format': {},
            'drafted_players': [],
            'team_rosters': {},
            'current_team': 1
        }
        
        self._load_data()
        self._prepare_features()
        self._train_model()
    
    def _load_data(self):
        """Load and preprocess the player rankings data."""
        try:
            self.players_df = pd.read_csv(self.rankings_file)
            logger.info(f"Loaded {len(self.players_df)} players from rankings file")
            
            # Clean up any missing values
            self.players_df = self.players_df.dropna()
            
            # Convert Expert Rank to numeric, handling any non-numeric values
            self.players_df['Expert_Rank'] = pd.to_numeric(self.players_df['Expert Rank'], errors='coerce')
            self.players_df = self.players_df.dropna(subset=['Expert_Rank'])
            
            # Sort by expert rank
            self.players_df = self.players_df.sort_values('Expert_Rank')
            
        except Exception as e:
            logger.error(f"Error loading rankings file: {e}")
            raise
    
    def _prepare_features(self):
        """Prepare features for the XGBoost model."""
        # Create label encoders for categorical variables
        self.label_encoders['Position'] = LabelEncoder()
        self.label_encoders['Team'] = LabelEncoder()
        
        # Encode categorical variables
        self.players_df['Position_Encoded'] = self.label_encoders['Position'].fit_transform(self.players_df['Position'])
        self.players_df['Team_Encoded'] = self.label_encoders['Team'].fit_transform(self.players_df['Team'])
        
        # Create additional features
        self.players_df['Position_Rank'] = self.players_df.groupby('Position')['Expert_Rank'].rank()
        self.players_df['Overall_Rank'] = self.players_df['Expert_Rank'].rank()
        
        # Calculate value metrics
        self.players_df['Value_Score'] = 1 / self.players_df['Expert_Rank']
        self.players_df['Position_Value'] = self.players_df.groupby('Position')['Value_Score'].transform('rank')
        
        logger.info("Features prepared successfully")
    
    def _train_model(self):
        """Train the XGBoost model to predict player value."""
        try:
            # Prepare features for training
            feature_columns = ['Position_Encoded', 'Team_Encoded', 'Position_Rank', 'Overall_Rank', 'Value_Score', 'Position_Value']
            X = self.players_df[feature_columns].values
            y = self.players_df['Expert_Rank'].values
            
            # Split data for training
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Initialize and train XGBoost model
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                objective='reg:squarederror'
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            logger.info(f"XGBoost model trained successfully. MSE: {mse:.4f}")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def set_draft_format(self, format_config: Dict[str, int]):
        """
        Set the draft format (how many players of each position).
        
        Args:
            format_config: Dictionary with position as key and count as value
                          Example: {'QB': 2, 'RB': 5, 'WR': 6, 'TE': 2}
        """
        self.draft_state['draft_format'] = format_config
        logger.info(f"Draft format set: {format_config}")
    
    def set_draft_parameters(self, total_teams: int, current_team: int = 1):
        """
        Set the draft parameters.
        
        Args:
            total_teams: Total number of teams in the draft
            current_team: Your team number (1-based)
        """
        self.draft_state['total_teams'] = total_teams
        self.draft_state['current_team'] = current_team
        logger.info(f"Draft parameters set: {total_teams} teams, you are team {current_team}")
    
    def record_pick(self, player_name: str, team_number: int = None, is_your_pick: bool = None):
        """
        Record a pick that was made in the draft.
        
        Args:
            player_name: Name of the player drafted
            team_number: Team number that made the pick (auto-calculated if not provided)
            is_your_pick: Whether this was your pick (auto-calculated if not provided)
        """
        # Find the player in our data
        player = self.players_df[self.players_df['Name'] == player_name]
        if player.empty:
            logger.warning(f"Player {player_name} not found in rankings")
            return False
        
        player_data = player.iloc[0]
        
        # Auto-calculate team number if not provided
        if team_number is None:
            team_number = self._calculate_current_team()
        
        # Auto-calculate if it's your pick if not provided
        if is_your_pick is None:
            is_your_pick = (team_number == self.draft_state['current_team'])
        
        # Record the pick
        pick_info = {
            'player_name': player_name,
            'team_number': team_number,
            'position': player_data['Position'],
            'expert_rank': player_data['Expert_Rank'],
            'round': self.draft_state['round'],
            'pick': self.draft_state['pick'],
            'is_your_pick': is_your_pick,
            'timestamp': datetime.now().isoformat()
        }
        
        self.draft_state['drafted_players'].append(pick_info)
        
        # Update team rosters
        if team_number not in self.draft_state['team_rosters']:
            self.draft_state['team_rosters'][team_number] = []
        
        self.draft_state['team_rosters'][team_number].append(pick_info)
        
        # Update draft position for snake draft
        self._advance_draft_position()
        
        logger.info(f"Recorded pick: {player_name} to team {team_number} (Round {self.draft_state['round']}, Pick {self.draft_state['pick']})")
        return True
    
    def _calculate_current_team(self) -> int:
        """Calculate which team should be picking based on current draft position."""
        round_num = self.draft_state['round']
        pick_num = self.draft_state['pick']
        total_teams = self.draft_state['total_teams']
        
        # Snake draft logic
        if round_num % 2 == 1:  # Odd rounds (1, 3, 5, ...) - forward order
            team = pick_num
        else:  # Even rounds (2, 4, 6, ...) - reverse order
            team = total_teams - pick_num + 1
        
        return team
    
    def _advance_draft_position(self):
        """Advance the draft position for snake draft."""
        total_teams = self.draft_state['total_teams']
        
        if self.draft_state['pick'] == total_teams:
            # End of round, move to next round
            self.draft_state['round'] += 1
            self.draft_state['pick'] = 1
        else:
            # Move to next pick in current round
            self.draft_state['pick'] += 1
    
    def is_your_turn(self) -> bool:
        """Check if it's currently your turn to pick."""
        current_team = self._calculate_current_team()
        return current_team == self.draft_state['current_team']
    
    def get_current_draft_position(self) -> int:
        """Get the current overall draft position (1, 2, 3, etc.)."""
        return (self.draft_state['round'] - 1) * self.draft_state['total_teams'] + self.draft_state['pick']
    
    def get_available_players(self) -> pd.DataFrame:
        """Get list of players that haven't been drafted yet."""
        drafted_names = [pick['player_name'] for pick in self.draft_state['drafted_players']]
        available = self.players_df[~self.players_df['Name'].isin(drafted_names)].copy()
        return available.sort_values('Expert_Rank')
    
    def get_team_needs(self, team_number: int) -> Dict[str, int]:
        """
        Calculate the remaining positional needs for a specific team.
        
        Args:
            team_number: Team number to analyze
            
        Returns:
            Dictionary showing remaining needs for each position
        """
        if team_number not in self.draft_state['team_rosters']:
            return self.draft_state['draft_format'].copy()
        
        current_roster = self.draft_state['team_rosters'][team_number]
        position_counts = {}
        
        for pick in current_roster:
            pos = pick['position']
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        needs = {}
        for pos, required in self.draft_state['draft_format'].items():
            current = position_counts.get(pos, 0)
            needs[pos] = max(0, required - current)
        
        return needs
    
    def calculate_value_gaps(self) -> Dict[str, List[Tuple[str, float]]]:
        """
        Calculate value gaps for each position based on available players.
        
        Returns:
            Dictionary with position as key and list of (player_name, value_score) tuples
        """
        available = self.get_available_players()
        value_gaps = {}
        
        for position in self.draft_state['draft_format'].keys():
            pos_players = available[available['Position'] == position]
            if not pos_players.empty:
                # Sort by value score (higher is better)
                pos_players = pos_players.sort_values('Value_Score', ascending=False)
                value_gaps[position] = [
                    (row['Name'], row['Value_Score']) 
                    for _, row in pos_players.head(10).iterrows()
                ]
        
        return value_gaps
    
    def get_recommendations(self, num_recommendations: int = 5) -> List[Dict]:
        """
        Get draft recommendations based on current state and team needs.
        
        Args:
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommendation dictionaries
        """
        your_team = self.draft_state['current_team']
        your_needs = self.get_team_needs(your_team)
        value_gaps = self.calculate_value_gaps()
        available = self.get_available_players()
        
        recommendations = []
        
        # Calculate recommendation scores for each available player
        player_scores = []
        
        # Calculate relative value scores for all available players
        if not available.empty:
            best_value = available['Value_Score'].max()
            worst_value = available['Value_Score'].min()
            value_range = best_value - worst_value
            
            if value_range > 0:
                available['relative_value'] = ((available['Value_Score'] - worst_value) / value_range) * 100
            else:
                available['relative_value'] = 100
        
        for _, player in available.iterrows():
            position = player['Position']
            
            # Base score from expert ranking
            base_score = 1 / player['Expert_Rank']
            
            # Calculate current draft position (ADP context)
            current_pick = (self.draft_state['round'] - 1) * self.draft_state['total_teams'] + self.draft_state['pick']
            
            # ADP value bonus - significant bonus for players drafted way below their ADP
            adp_value_bonus = 0
            if player['Expert_Rank'] < current_pick:
                # Player is being drafted below their ADP - this is good value
                adp_difference = current_pick - player['Expert_Rank']
                adp_value_bonus = min(adp_difference * 0.1, 2.0)  # Cap at 2.0 bonus
            
            # Position need bonus (but don't skip positions you already have)
            need_bonus = 0
            if your_needs.get(position, 0) > 0:
                need_bonus = your_needs[position] * 0.3
            else:
                # Position is filled, but still consider if ADP value is exceptional
                need_bonus = -0.2  # Small penalty, but can be overcome by ADP value
            
            # Value gap bonus (higher for players with better relative value)
            relative_value = available.loc[available['Name'] == player['Name'], 'relative_value'].iloc[0]
            value_bonus = relative_value * 0.02  # Scale down since relative value is 0-100
            
            # Position scarcity bonus (if few players left at position)
            pos_available = len(available[available['Position'] == position])
            scarcity_bonus = max(0, (10 - pos_available) * 0.1)
            
            # Calculate final score
            final_score = base_score + need_bonus + value_bonus + scarcity_bonus + adp_value_bonus
            
            player_scores.append({
                'player': player,
                'score': final_score,
                'position': position,
                'expert_rank': player['Expert_Rank']
            })
        
        # Sort by score and get top recommendations
        player_scores.sort(key=lambda x: x['score'], reverse=True)
        
        for i, player_score in enumerate(player_scores[:num_recommendations]):
            player = player_score['player']
            
            recommendation = {
                'rank': i + 1,
                'player_name': player['Name'],
                'position': player['Position'],
                'team': player['Team'],
                'expert_rank': player['Expert_Rank'],
                'recommendation_score': round(player_score['score'], 4),
                'reasoning': self._generate_reasoning(player_score, your_needs, value_gaps)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_best_available_players(self, num_players: int = 10) -> List[Dict]:
        """
        Get the best available players based on expert rank and value score.
        This is used when it's not your turn to pick.
        
        Args:
            num_players: Number of players to return
            
        Returns:
            List of player dictionaries
        """
        available = self.get_available_players()
        
        if available.empty:
            return []
        
        # Calculate relative value scores based on best available player
        best_value = available['Value_Score'].max()
        worst_value = available['Value_Score'].min()
        value_range = best_value - worst_value
        
        if value_range > 0:
            # Normalize value scores to 0-100 scale relative to best player
            available['relative_value'] = ((available['Value_Score'] - worst_value) / value_range) * 100
        else:
            # If all players have same value, give them all 100
            available['relative_value'] = 100
        
        # Sort by a combination of expert rank and relative value score
        available['combined_score'] = (1.0 / available['Expert_Rank']) + (available['relative_value'] * 0.01)
        available = available.sort_values('combined_score', ascending=False)
        
        players = []
        for i, (_, player) in enumerate(available.head(num_players).iterrows()):
            players.append({
                'player_name': player['Name'],
                'position': player['Position'],
                'team': player['Team'],
                'expert_rank': player['Expert_Rank'],
                'value_score': round(player['relative_value'], 1),  # Use relative value score
                'rank': i + 1,
                'type': 'best_available'
            })
        
        return players
    
    def _generate_reasoning(self, player_score: Dict, team_needs: Dict, value_gaps: Dict) -> str:
        """Generate human-readable reasoning for a recommendation."""
        player = player_score['player']
        position = player_score['position']
        
        reasons = []
        
        # Calculate current draft position for ADP context
        current_pick = (self.draft_state['round'] - 1) * self.draft_state['total_teams'] + self.draft_state['pick']
        
        # ADP value analysis
        if player_score['expert_rank'] < current_pick:
            adp_difference = current_pick - player_score['expert_rank']
            if adp_difference >= 20:
                reasons.append(f"EXCEPTIONAL VALUE: {adp_difference} picks below ADP!")
            elif adp_difference >= 10:
                reasons.append(f"Great value: {adp_difference} picks below ADP")
            else:
                reasons.append(f"Good value: {adp_difference} picks below ADP")
        
        # Position need analysis
        if team_needs.get(position, 0) > 0:
            reasons.append(f"Need {position} players")
        else:
            # Position is filled, but explain why still recommended
            reasons.append(f"Position filled but value too good to pass up")
        
        # Value ranking context
        if player_score['expert_rank'] <= 50:
            reasons.append("Top-tier talent")
        elif player_score['expert_rank'] <= 100:
            reasons.append("Strong value pick")
        
        # Position scarcity
        pos_available = len(self.get_available_players()[self.get_available_players()['Position'] == position])
        if pos_available <= 5:
            reasons.append(f"Only {pos_available} {position} players left")
        
        # Team needs context for other positions
        other_positions_needed = [pos for pos, need in team_needs.items() if need > 0 and pos != position]
        if other_positions_needed:
            reasons.append(f"Also need: {', '.join(other_positions_needed)}")
        
        return "; ".join(reasons) if reasons else "Good value for current draft position"
    
    def get_draft_summary(self) -> Dict:
        """Get a summary of the current draft state."""
        your_team = self.draft_state['current_team']
        your_roster = self.draft_state['team_rosters'].get(your_team, [])
        your_needs = self.get_team_needs(your_team)
        
        summary = {
            'current_round': self.draft_state['round'],
            'current_pick': self.draft_state['pick'],
            'current_draft_position': self.get_current_draft_position(),
            'your_team': your_team,
            'your_roster': your_roster,
            'your_needs': your_needs,
            'total_drafted': len(self.draft_state['drafted_players']),
            'draft_format': self.draft_state['draft_format'],
            'next_pick_estimate': self._estimate_next_pick()
        }
        
        return summary
    
    def _estimate_next_pick(self) -> int:
        """Estimate when your next pick will be."""
        your_team = self.draft_state['current_team']
        total_teams = self.draft_state['total_teams']
        
        # Calculate picks until your next turn
        if self.draft_state['pick'] < your_team:
            # This round
            picks_until_next = your_team - self.draft_state['pick']
        else:
            # Next round
            picks_until_next = total_teams - self.draft_state['pick'] + your_team
        
        return picks_until_next
    
    def export_draft_state(self, filename: str = None) -> str:
        """Export the current draft state to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"draft_state_{timestamp}.json"
        
        export_data = {
            'draft_state': self.draft_state,
            'export_timestamp': datetime.now().isoformat(),
            'total_players': len(self.players_df),
            'available_players': len(self.get_available_players())
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Draft state exported to {filename}")
        return filename
    
    def import_draft_state(self, filename: str) -> bool:
        """Import a draft state from a JSON file."""
        try:
            with open(filename, 'r') as f:
                import_data = json.load(f)
            
            self.draft_state = import_data['draft_state']
            logger.info(f"Draft state imported from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing draft state: {e}")
            return False
