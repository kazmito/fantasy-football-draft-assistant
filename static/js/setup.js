// Setup page JavaScript functionality

let currentStep = 1;
let draftFormat = {};
let draftParameters = {};

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    updateProgressBar();
    setupEventListeners();
});

function setupEventListeners() {
    // Format form submission
    document.getElementById('format-form').addEventListener('submit', function(e) {
        e.preventDefault();
        handleFormatSubmit();
    });
    
    // Parameters form submission
    document.getElementById('parameters-form').addEventListener('submit', function(e) {
        e.preventDefault();
        handleParametersSubmit();
    });
    
    // Total teams change handler
    document.getElementById('total_teams').addEventListener('change', function() {
        updateTeamOptions();
    });
}

function handleFormatSubmit() {
    const formData = new FormData(document.getElementById('format-form'));
    
    // Validate required fields
    const requiredFields = ['qb', 'rb', 'wr', 'te'];
    for (let field of requiredFields) {
        if (!formData.get(field)) {
            showAlert('Please fill in all required fields.', 'danger');
            return;
        }
    }
    
    // Store format data
    draftFormat = {
        qb: parseInt(formData.get('qb')),
        rb: parseInt(formData.get('rb')),
        wr: parseInt(formData.get('wr')),
        te: parseInt(formData.get('te')),
        flex: parseInt(formData.get('flex') || 0),
        super_flex: parseInt(formData.get('super_flex') || 0),
        dst: parseInt(formData.get('dst') || 1),
        k: parseInt(formData.get('k') || 1)
    };
    
    // Send to server
    fetch('/setup/format', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStep(2);
            updateProgressBar();
        } else {
            showAlert('Error setting draft format: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showAlert('Error: ' + error.message, 'danger');
    });
}

function handleParametersSubmit() {
    const formData = new FormData(document.getElementById('parameters-form'));
    
    // Validate required fields
    if (!formData.get('total_teams') || !formData.get('current_team')) {
        showAlert('Please fill in all required fields.', 'danger');
        return;
    }
    
    // Store parameters data
    draftParameters = {
        total_teams: parseInt(formData.get('total_teams')),
        current_team: parseInt(formData.get('current_team'))
    };
    
    // Send to server
    fetch('/setup/parameters', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStep(3);
            updateProgressBar();
            displaySummary();
        } else {
            showAlert('Error setting draft parameters: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        showAlert('Error: ' + error.message, 'danger');
    });
}

function showStep(step) {
    // Hide all steps
    document.getElementById('step-1').style.display = 'none';
    document.getElementById('step-2').style.display = 'none';
    document.getElementById('step-3').style.display = 'none';
    
    // Show the requested step
    document.getElementById('step-' + step).style.display = 'block';
    
    currentStep = step;
}

function updateProgressBar() {
    const progress = (currentStep / 3) * 100;
    document.getElementById('setup-progress').style.width = progress + '%';
}

function updateTeamOptions() {
    const totalTeams = parseInt(document.getElementById('total_teams').value);
    const currentTeamSelect = document.getElementById('current_team');
    
    // Clear existing options
    currentTeamSelect.innerHTML = '<option value="">Select your team...</option>';
    
    if (totalTeams) {
        // Add team options
        for (let i = 1; i <= totalTeams; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Team ${i}`;
            currentTeamSelect.appendChild(option);
        }
    }
}

function displaySummary() {
    // Display format summary
    const formatSummary = document.getElementById('format-summary');
    formatSummary.innerHTML = `
        <div class="row">
            <div class="col-6">
                <strong>QB:</strong> ${draftFormat.qb}<br>
                <strong>RB:</strong> ${draftFormat.rb}<br>
                <strong>WR:</strong> ${draftFormat.wr}<br>
                <strong>TE:</strong> ${draftFormat.te}
            </div>
            <div class="col-6">
                <strong>Flex:</strong> ${draftFormat.flex}<br>
                <strong>Super Flex:</strong> ${draftFormat.super_flex}<br>
                <strong>DST:</strong> ${draftFormat.dst}<br>
                <strong>K:</strong> ${draftFormat.k}
            </div>
        </div>
    `;
    
    // Display parameters summary
    const parametersSummary = document.getElementById('parameters-summary');
    parametersSummary.innerHTML = `
        <strong>Total Teams:</strong> ${draftParameters.total_teams}<br>
        <strong>Your Team:</strong> ${draftParameters.current_team}<br>
        <strong>Total Roster Spots:</strong> ${draftFormat.qb + draftFormat.rb + draftFormat.wr + draftFormat.te + draftFormat.flex + draftFormat.super_flex + draftFormat.dst + draftFormat.k}
    `;
}

function showAlert(message, type) {
    // Remove existing alerts
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && currentStep === 1) {
        handleFormatSubmit();
    } else if (e.key === 'Enter' && currentStep === 2) {
        handleParametersSubmit();
    }
});

// Form validation helpers
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], select[required]');
    
    let isValid = true;
    inputs.forEach(input => {
        if (!input.value) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Add visual feedback for form interactions
document.querySelectorAll('.form-select, .form-control').forEach(element => {
    element.addEventListener('change', function() {
        if (this.value) {
            this.classList.add('is-valid');
            this.classList.remove('is-invalid');
        } else {
            this.classList.remove('is-valid');
            this.classList.add('is-invalid');
        }
    });
});
