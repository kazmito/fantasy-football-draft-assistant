// Dashboard JavaScript functionality

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
});

function loadDashboardData() {
    loadStatus();
    loadDraftSummary();
}

function loadStatus() {
    const container = document.getElementById('status-content');
    
    // Show loading state
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading draft status...</p>
        </div>
    `;
    
    // Load status from API
    fetch('/api/draft-summary')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayStatus(data.summary);
            } else {
                displayStatusError(data.error);
            }
        })
        .catch(error => {
            displayStatusError('Failed to load status');
        });
}

function displayStatus(summary) {
    const container = document.getElementById('status-content');
    
    if (!summary.draft_format || Object.keys(summary.draft_format).length === 0) {
        container.innerHTML = `
            <div class="text-center">
                <i class="fas fa-exclamation-triangle text-warning fa-2x mb-3"></i>
                <h6 class="text-warning">Setup Required</h6>
                <p class="text-muted mb-3">Your draft hasn't been configured yet.</p>
                <a href="/setup" class="btn btn-warning btn-sm">
                    <i class="fas fa-cog me-2"></i>Setup Draft
                </a>
            </div>
        `;
        return;
    }
    
    const totalSpots = Object.values(summary.draft_format).reduce((a, b) => a + b, 0);
    const draftedSpots = summary.your_roster ? summary.your_roster.length : 0;
    const remainingSpots = totalSpots - draftedSpots;
    
    container.innerHTML = `
        <div class="row text-center">
            <div class="col-4">
                <div class="h4 text-primary mb-1">${summary.current_round}</div>
                <small class="text-muted">Current Round</small>
            </div>
            <div class="col-4">
                <div class="h4 text-success mb-1">${draftedSpots}/${totalSpots}</div>
                <small class="text-muted">Your Roster</small>
            </div>
            <div class="col-4">
                <div class="h4 text-info mb-1">${summary.next_pick_estimate}</div>
                <small class="text-muted">Picks Until Next</small>
            </div>
        </div>
        
        <div class="mt-3">
            <div class="progress mb-2" style="height: 8px;">
                <div class="progress-bar" role="progressbar" style="width: ${(draftedSpots/totalSpots)*100}%"></div>
            </div>
            <small class="text-muted">Draft Progress: ${Math.round((draftedSpots/totalSpots)*100)}%</small>
        </div>
        
        <div class="mt-3">
            <a href="/draft" class="btn btn-primary btn-sm w-100">
                <i class="fas fa-play me-2"></i>Continue Drafting
            </a>
        </div>
    `;
}

function displayStatusError(error) {
    const container = document.getElementById('status-content');
    container.innerHTML = `
        <div class="text-center">
            <i class="fas fa-exclamation-circle text-danger fa-2x mb-3"></i>
            <h6 class="text-danger">Error Loading Status</h6>
            <p class="text-muted">${error}</p>
            <button class="btn btn-outline-primary btn-sm" onclick="loadStatus()">
                <i class="fas fa-sync-alt me-2"></i>Retry
            </button>
        </div>
    `;
}

function loadDraftSummary() {
    const container = document.getElementById('draft-summary-content');
    
    // Show loading state
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading draft summary...</p>
        </div>
    `;
    
    // Load summary from API
    fetch('/api/draft-summary')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayDraftSummary(data.summary);
            } else {
                displayDraftSummaryError(data.error);
            }
        })
        .catch(error => {
            displayDraftSummaryError('Failed to load summary');
        });
}

function displayDraftSummary(summary) {
    const container = document.getElementById('draft-summary-content');
    
    if (!summary.draft_format || Object.keys(summary.draft_format).length === 0) {
        container.innerHTML = `
            <div class="text-center">
                <i class="fas fa-info-circle text-info fa-2x mb-3"></i>
                <h6 class="text-info">No Draft Configuration</h6>
                <p class="text-muted">Complete the setup to start your draft.</p>
                <a href="/setup" class="btn btn-info btn-sm">
                    <i class="fas fa-cog me-2"></i>Go to Setup
                </a>
            </div>
        `;
        return;
    }
    
    // Display draft format
    let formatHtml = '<div class="row">';
    Object.entries(summary.draft_format).forEach(([position, count]) => {
        if (count > 0) {
            formatHtml += `
                <div class="col-6 mb-2">
                    <span class="badge bg-secondary me-2">${count}</span>
                    <small>${position}</small>
                </div>
            `;
        }
    });
    formatHtml += '</div>';
    
    // Display your roster
    let rosterHtml = '';
    if (summary.your_roster && summary.your_roster.length > 0) {
        summary.your_roster.forEach(pick => {
            rosterHtml += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <strong>${pick.player_name}</strong>
                        <small class="text-muted ms-2">${pick.position} - Team ${pick.team_number}</small>
                    </div>
                    <span class="badge bg-primary">${pick.round}.${pick.pick}</span>
                </div>
            `;
        });
    } else {
        rosterHtml = '<p class="text-muted text-center">No players drafted yet</p>';
    }
    
    // Display remaining needs
    let needsHtml = '';
    if (summary.your_needs) {
        Object.entries(summary.your_needs).forEach(([position, count]) => {
            if (count > 0) {
                needsHtml += `
                    <span class="badge bg-warning text-dark me-2 mb-2">
                        ${position}: ${count}
                    </span>
                `;
            }
        });
    }
    
    if (!needsHtml) {
        needsHtml = '<span class="badge bg-success">All positions filled!</span>';
    }
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <h6 class="text-primary mb-3">
                    <i class="fas fa-list me-2"></i>Draft Format
                </h6>
                ${formatHtml}
            </div>
            <div class="col-md-4">
                <h6 class="text-success mb-3">
                    <i class="fas fa-user-friends me-2"></i>Your Roster
                </h6>
                ${rosterHtml}
            </div>
            <div class="col-md-4">
                <h6 class="text-warning mb-3">
                    <i class="fas fa-exclamation-triangle me-2"></i>Remaining Needs
                </h6>
                ${needsHtml}
            </div>
        </div>
        
        <div class="mt-4 text-center">
            <a href="/draft" class="btn btn-primary me-2">
                <i class="fas fa-play me-2"></i>Go to Draft
            </a>
            <a href="/setup" class="btn btn-outline-secondary">
                <i class="fas fa-cog me-2"></i>Modify Setup
            </a>
        </div>
    `;
}

function displayDraftSummaryError(error) {
    const container = document.getElementById('draft-summary-content');
    container.innerHTML = `
        <div class="text-center">
            <i class="fas fa-exclamation-circle text-danger fa-2x mb-3"></i>
            <h6 class="text-danger">Error Loading Summary</h6>
            <p class="text-muted">${error}</p>
            <button class="btn btn-outline-primary btn-sm" onclick="loadDraftSummary()">
                <i class="fas fa-sync-alt me-2"></i>Retry
            </button>
        </div>
    `;
}

// Auto-refresh dashboard data every 60 seconds
setInterval(() => {
    if (document.visibilityState === 'visible') {
        loadDashboardData();
    }
}, 60000);

// Add some interactive features
document.addEventListener('click', function(e) {
    // Make feature cards clickable
    if (e.target.closest('.card.text-center')) {
        const card = e.target.closest('.card.text-center');
        const title = card.querySelector('h5').textContent;
        
        // Add visual feedback
        card.style.transform = 'scale(1.02)';
        card.style.transition = 'transform 0.2s ease';
        
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 200);
        
        // Navigate based on card
        if (title.includes('Quick Start')) {
            window.location.href = '/setup';
        }
    }
});

// Add hover effects to feature cards
document.querySelectorAll('.card.text-center').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
        this.style.transition = 'transform 0.3s ease';
        this.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
        this.style.boxShadow = '0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)';
    });
});
