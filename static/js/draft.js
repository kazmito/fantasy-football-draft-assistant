// Draft interface JavaScript functionality

let currentRecommendations = [];
let currentAvailablePlayers = [];
let currentDraftSummary = {};
let currentPickInfo = { currentTeam: null, nextTeam: null, round: null, pick: null };

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadInitialData();
    setupEventListeners();
});

function setupEventListeners() {
    // Pick form submission
    document.getElementById('pick-form').addEventListener('submit', function(e) {
        e.preventDefault();
        handlePickSubmission();
    });
    
    // Player selection from recommendations
    document.addEventListener('click', function(e) {
        if (e.target.closest('.player-card')) {
            selectPlayerFromRecommendations(e.target.closest('.player-card'));
        }
    });
}

function loadInitialData() {
    loadDraftSummary();
    loadRecommendations();
    loadAvailablePlayers();
    // Ensure current pick info is updated after loading data
    setTimeout(() => {
        if (currentDraftSummary.current_round) {
            updateCurrentPickInfo();
        }
        // Also ensure current pick info is visible
        ensureCurrentPickInfoVisible();
    }, 100);
    
    // Double-check after a longer delay to catch any late updates
    setTimeout(() => {
        ensureCurrentPickInfoVisible();
    }, 500);
}

function loadDraftSummary() {
    fetch('/api/draft-summary')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentDraftSummary = data.summary;
                updateDraftStatus();
                updateRosterDisplay();
                updateTeamOptions();
                
                // Ensure current pick info is visible after loading draft summary
                setTimeout(() => {
                    ensureCurrentPickInfoVisible();
                }, 50);
            }
        })
        .catch(error => console.error('Error loading draft summary:', error));
}

function loadRecommendations() {
    fetch('/api/recommendations')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentRecommendations = data.recommendations;
                updateRecommendationsUI(data.type, data.message);
                displayRecommendations();
                updatePlayerDropdown();
            }
        })
        .catch(error => console.error('Error loading recommendations:', error));
}

function loadAvailablePlayers() {
    fetch('/api/available-players')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentAvailablePlayers = data.players;
                displayAvailablePlayers();
            }
        })
        .catch(error => console.error('Error loading available players:', error));
}

function updateDraftStatus() {
    document.getElementById('current-round').textContent = currentDraftSummary.current_round || '-';
    document.getElementById('current-pick').textContent = currentDraftSummary.current_pick || '-';
    document.getElementById('current-draft-position').textContent = currentDraftSummary.current_draft_position || '-';
    document.getElementById('your-team').textContent = currentDraftSummary.your_team || '-';
    document.getElementById('next-pick').textContent = currentDraftSummary.next_pick_estimate || '-';
    document.getElementById('total-drafted').textContent = currentDraftSummary.total_drafted || '-';
    
    // Update current pick info
    updateCurrentPickInfo();
}

function displayRecommendations() {
    const container = document.getElementById('recommendations-content');
    
    if (!currentRecommendations || currentRecommendations.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No recommendations available. Complete setup first.</p>';
        return;
    }
    
    let html = '';
    currentRecommendations.forEach((rec, index) => {
        if (rec.type === 'best_available') {
            // Display best available players (not your turn)
            html += `
                <div class="player-card position-${rec.position.toLowerCase()}" data-player-name="${rec.player_name}">
                    <div class="player-info">
                        <span class="player-rank">${rec.rank}</span>
                        <span class="player-name">${rec.player_name}</span>
                        <span class="player-position">${rec.position}</span>
                        <span class="player-team">${rec.team}</span>
                        <span class="player-rank-value">Rank: ${rec.expert_rank}</span>
                    </div>
                    <div class="player-reasoning">
                        <strong>Value Score:</strong> ${rec.value_score}/100 | Expert Rank: ${rec.expert_rank}
                    </div>
                </div>
            `;
        } else {
            // Display AI recommendations (your turn)
            html += `
                <div class="player-card position-${rec.position.toLowerCase()}" data-player-name="${rec.player_name}">
                    <div class="player-info">
                        <span class="player-rank">${rec.rank}</span>
                        <span class="player-name">${rec.player_name}</span>
                        <span class="player-position">${rec.position}</span>
                        <span class="player-team">${rec.team}</span>
                        <span class="player-rank-value">Rank: ${rec.expert_rank}</span>
                    </div>
                    <div class="player-reasoning">
                        <strong>Score:</strong> ${rec.recommendation_score} | ${rec.reasoning}
                    </div>
                </div>
            `;
        }
    });
    
    container.innerHTML = html;
}

function displayAvailablePlayers() {
    const container = document.getElementById('available-players-content');
    
    if (!currentAvailablePlayers || currentAvailablePlayers.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No available players found.</p>';
        return;
    }
    
    let html = '';
    currentAvailablePlayers.slice(0, 20).forEach(player => {
        html += `
            <div class="available-player">
                <div class="available-player-info">
                    <div class="available-player-name">${player.name}</div>
                    <div class="available-player-details">
                        ${player.position} - ${player.team}
                    </div>
                </div>
                <span class="available-player-rank">${player.expert_rank}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateRosterDisplay() {
    const container = document.getElementById('roster-content');
    
    // Check if we have draft summary data at all
    if (!currentDraftSummary || !currentDraftSummary.your_roster) {
        container.innerHTML = '<div class="text-center"><div class="spinner-border text-info" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading your roster...</p></div>';
        return;
    }
    
    if (currentDraftSummary.your_roster.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No players drafted yet.</p>';
        return;
    }
    
    let html = '';
    currentDraftSummary.your_roster.forEach(pick => {
        html += `
            <div class="roster-player">
                <div class="roster-player-info">
                    <div class="roster-player-name">${pick.player_name}</div>
                    <div class="roster-player-details">
                        ${pick.position} - Team ${pick.team_number} | Expert Rank: ${pick.expert_rank}
                    </div>
                </div>
                <span class="roster-player-round">${pick.round}.${pick.pick}</span>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updatePlayerDropdown() {
    const select = document.getElementById('pick-player');
    
    // Clear existing options
    select.innerHTML = '<option value="">Choose from top recommendations...</option>';
    
    // Add recommendation options
    currentRecommendations.forEach(rec => {
        const option = document.createElement('option');
        option.value = rec.player_name;
        option.textContent = `${rec.rank}. ${rec.player_name} (${rec.position} - ${rec.team})`;
        select.appendChild(option);
    });
}

function updateCurrentPickInfo() {
    // Calculate which team is currently picking
    const round = currentDraftSummary.current_round || 1;
    const pick = currentDraftSummary.current_pick || 1;
    const totalTeams = currentDraftSummary.total_teams || 12;
    
    // Snake draft logic - simplified and corrected
    let currentTeam, nextTeam;
    
    // Calculate current team based on current round and pick
    if (round % 2 === 1) {  // Odd rounds (1, 3, 5, ...) - forward order
        currentTeam = pick;
    } else {  // Even rounds (2, 4, 6, ...) - reverse order
        currentTeam = totalTeams - pick + 1;
    }
    
    // Calculate picks until your next turn
    let picksUntilYourTurn = 0;
    let currentRound = round;
    let currentPick = pick;
    let yourTeam = currentDraftSummary.your_team;
    
    // Count picks until we reach your team again
    while (true) {
        let teamPicking;
        
        if (currentRound % 2 === 1) {  // Odd rounds - forward order
            teamPicking = currentPick;
        } else {  // Even rounds - reverse order
            teamPicking = totalTeams - currentPick + 1;
        }
        
        // If this is your team, we've found your next turn
        if (teamPicking === yourTeam) {
            break;
        }
        
        picksUntilYourTurn++;
        
        // Move to next pick
        if (currentPick === totalTeams) {
            // End of round, move to next round
            currentRound++;
            currentPick = 1;
        } else {
            // Same round, next pick
            currentPick++;
        }
    }
    
    // Store the picks count for display
    nextTeam = picksUntilYourTurn;
    
    // Update the display - ensure elements exist before updating
    const currentTeamElement = document.getElementById('current-picking-team');
    const nextTeamElement = document.getElementById('next-picking-team');
    
    if (currentTeamElement && nextTeamElement) {
        // Clear previous content and classes
        currentTeamElement.textContent = `Team ${currentTeam}`;
        nextTeamElement.textContent = `${nextTeam} picks away`;
        currentTeamElement.className = 'h5 text-primary';
        nextTeamElement.className = 'h5 text-success';
        
        // Highlight if it's your team
        if (currentTeam === currentDraftSummary.your_team) {
            currentTeamElement.classList.add('text-warning', 'fw-bold');
            currentTeamElement.textContent += ' (YOU!)';
        }
        
        // Store the current values for potential restoration
        currentPickInfo.currentTeam = currentTeam;
        currentPickInfo.nextTeam = nextTeam;
        currentPickInfo.round = round;
        currentPickInfo.pick = pick;
        
        // Also store in dataset as backup
        currentTeamElement.dataset.currentTeam = currentTeam;
        currentTeamElement.dataset.nextTeam = nextTeam;
        currentTeamElement.dataset.round = round;
        currentTeamElement.dataset.pick = pick;
    }
}

function ensureCurrentPickInfoVisible() {
    // Check if current pick info is visible, restore if needed
    const currentTeamElement = document.getElementById('current-picking-team');
    const nextTeamElement = document.getElementById('next-picking-team');
    
    if (currentTeamElement && nextTeamElement) {
        // If the display is empty or shows "-", restore the stored values
        if (currentTeamElement.textContent === '-' || currentTeamElement.textContent === '' || 
            nextTeamElement.textContent === '-' || nextTeamElement.textContent === '') {
            
            // First try to restore from global variable
            if (currentPickInfo.currentTeam && currentPickInfo.nextTeam) {
                // Restore the display from global variable
                currentTeamElement.textContent = `Team ${currentPickInfo.currentTeam}`;
                nextTeamElement.textContent = `${currentPickInfo.nextTeam} picks away`;
                
                // Restore highlighting if it was your team
                if (currentPickInfo.currentTeam == currentDraftSummary.your_team) {
                    currentTeamElement.classList.add('text-warning', 'fw-bold');
                    currentTeamElement.textContent += ' (YOU!)';
                }
            } else {
                // Fallback to dataset attributes
                const storedCurrentTeam = currentTeamElement.dataset.currentTeam;
                const storedNextTeam = currentTeamElement.dataset.nextTeam;
                
                if (storedCurrentTeam && storedNextTeam) {
                    // Restore the display from dataset
                    currentTeamElement.textContent = `Team ${storedCurrentTeam}`;
                    nextTeamElement.textContent = `${storedNextTeam} picks away`;
                    
                    // Restore highlighting if it was your team
                    if (storedCurrentTeam == currentDraftSummary.your_team) {
                        currentTeamElement.classList.add('text-warning', 'fw-bold');
                        currentTeamElement.textContent += ' (YOU!)';
                    }
                } else if (currentDraftSummary.current_round && currentDraftSummary.current_pick) {
                    // If no stored data but we have current draft summary, update from that
                    updateCurrentPickInfo();
                }
            }
        }
    }
}

function updateRecommendationsUI(type, message) {
    const icon = document.getElementById('recommendations-icon');
    const title = document.getElementById('recommendations-title');
    const messageDiv = document.getElementById('recommendations-message');
    
    if (type === 'ai_recommendations') {
        // It's your turn - show AI recommendations
        icon.className = 'fas fa-brain me-2';
        title.textContent = 'AI Recommendations';
        messageDiv.innerHTML = `<i class="fas fa-lightbulb me-1"></i>${message}`;
        messageDiv.className = 'mt-2 text-success small';
    } else {
        // It's not your turn - show best available
        icon.className = 'fas fa-list-ol me-2';
        title.textContent = 'Best Available Players';
        messageDiv.innerHTML = `<i class="fas fa-info-circle me-1"></i>${message}`;
        messageDiv.className = 'mt-2 text-muted small';
    }
}

function selectPlayerFromRecommendations(playerCard) {
    // Remove previous selection
    document.querySelectorAll('.player-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Select this player
    playerCard.classList.add('selected');
    
    // Update the dropdown
    const playerName = playerCard.dataset.playerName;
    document.getElementById('pick-player').value = playerName;
}

function showPlayerSearch() {
    const modal = new bootstrap.Modal(document.getElementById('playerSearchModal'));
    modal.show();
}

function searchPlayers() {
    const query = document.getElementById('search-query').value.trim();
    
    if (!query) {
        document.getElementById('search-results').innerHTML = '<p class="text-muted text-center">Enter a player name to search...</p>';
        return;
    }
    
    fetch(`/api/search-players?query=${encodeURIComponent(query)}&limit=20`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displaySearchResults(data.players);
            } else {
                document.getElementById('search-results').innerHTML = `<p class="text-danger text-center">Error: ${data.error}</p>`;
            }
        })
        .catch(error => {
            document.getElementById('search-results').innerHTML = `<p class="text-danger text-center">Error: ${error.message}</p>`;
        });
}

function displaySearchResults(players) {
    const container = document.getElementById('search-results');
    
    if (!players || players.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">No players found matching your search.</p>';
        return;
    }
    
    let html = '';
    players.forEach(player => {
        html += `
            <div class="search-result" onclick="selectPlayerFromSearch('${player.name}')">
                <div class="search-result-info">
                    <div class="search-result-name">${player.name}</div>
                    <div class="search-result-details">
                        ${player.position} - ${player.team} | Expert Rank: ${player.expert_rank}
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function selectPlayerFromSearch(playerName) {
    // Update the dropdown
    document.getElementById('pick-player').value = playerName;
    
    // Close the modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('playerSearchModal'));
    modal.hide();
    
    // Show success message
    showAlert(`Selected: ${playerName}`, 'success');
}

function handlePickSubmission() {
    const formData = new FormData(document.getElementById('pick-form'));
    
    // Validate form
    if (!formData.get('player_name')) {
        showAlert('Please select a player.', 'danger');
        return;
    }
    
    // Submit pick
    fetch('/api/record-pick', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
            .then(data => {
            if (data.success) {
                showAlert(data.message, 'success');
                
                // Reset form
                document.getElementById('pick-form').reset();
                
                // Store the new round/pick data
                let newRound = data.round;
                let newPick = data.pick;
                
                // Update current pick info immediately with new data
                if (newRound && newPick) {
                    // Temporarily update the draft summary with new round/pick
                    currentDraftSummary.current_round = newRound;
                    currentDraftSummary.current_pick = newPick;
                    updateCurrentPickInfo();
                }
                
                // Refresh data in background (don't wait for it to complete)
                setTimeout(() => {
                    loadDraftSummary();
                    loadRecommendations();
                    loadAvailablePlayers();
                }, 100);
            } else {
                showAlert('Error: ' + data.error, 'danger');
            }
        })
    .catch(error => {
        showAlert('Error: ' + error.message, 'danger');
    });
}

function filterByPosition() {
    const position = document.getElementById('position-filter').value;
    
    if (!position) {
        displayAvailablePlayers();
        return;
    }
    
    fetch(`/api/available-players?position=${position}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentAvailablePlayers = data.players;
                displayAvailablePlayers();
            }
        })
        .catch(error => console.error('Error filtering players:', error));
}

function refreshData() {
    loadInitialData();
    showAlert('Data refreshed!', 'info');
}

function showAlert(message, type) {
    // Remove existing notification alerts only (not UI elements)
    const existingAlerts = document.querySelectorAll('.alert.alert-dismissible.position-fixed');
    existingAlerts.forEach(alert => {
        if (alert.classList.contains('position-fixed')) {
            alert.remove();
        }
    });
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(alertDiv);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

// Auto-refresh every 30 seconds
setInterval(() => {
    if (document.visibilityState === 'visible') {
        loadDraftSummary();
        // Ensure current pick info stays visible
        ensureCurrentPickInfoVisible();
    }
}, 30000);

// Search on Enter key
document.getElementById('search-query').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchPlayers();
    }
});
