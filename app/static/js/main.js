/**
 * EthicAI - Enterprise AI Responsibility Suite
 * Main JavaScript functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Virtual Assistant Chat Form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            if (!validateChatForm()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Bias Analysis Form
    const biasForm = document.getElementById('bias-analysis-form');
    if (biasForm) {
        biasForm.addEventListener('submit', function(e) {
            if (!validateBiasForm()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Model Upload Form
    const modelUploadForm = document.getElementById('model-upload-form');
    if (modelUploadForm) {
        modelUploadForm.addEventListener('submit', function(e) {
            if (!validateModelUploadForm()) {
                e.preventDefault();
                return false;
            }
        });
    }

    // Initialize any charts on the page
    initializeCharts();

    // Set up dynamic content loaders
    setupDynamicLoaders();
});

/**
 * Validate the chat form
 */
function validateChatForm() {
    const queryInput = document.getElementById('query');
    if (!queryInput || !queryInput.value.trim()) {
        showFormError('query', 'Please enter a question or command');
        return false;
    }
    return true;
}

/**
 * Validate the bias analysis form
 */
function validateBiasForm() {
    const testDatasetInput = document.getElementById('test_dataset');
    const biasTypesChecked = document.querySelectorAll('input[name="bias_types"]:checked');
    
    if (!testDatasetInput || !testDatasetInput.files || testDatasetInput.files.length === 0) {
        showFormError('test_dataset', 'Please upload a test dataset');
        return false;
    }
    
    if (biasTypesChecked.length === 0) {
        showFormError('bias_types', 'Please select at least one bias type to analyze');
        return false;
    }
    
    return true;
}

/**
 * Validate the model upload form
 */
function validateModelUploadForm() {
    const modelFileInput = document.getElementById('model_file');
    const apiEndpointInput = document.getElementById('api_endpoint');
    const modelNameInput = document.getElementById('model_name');
    
    if ((!modelFileInput || !modelFileInput.files || modelFileInput.files.length === 0) && 
        (!apiEndpointInput || !apiEndpointInput.value.trim())) {
        showFormError('model_upload', 'Please either upload a model file or provide an API endpoint');
        return false;
    }
    
    if (!modelNameInput || !modelNameInput.value.trim()) {
        showFormError('model_name', 'Please enter a name for the model');
        return false;
    }
    
    return true;
}

/**
 * Show form validation error
 */
function showFormError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.classList.add('is-invalid');
        
        // Create or update error message
        let errorDiv = field.nextElementSibling;
        if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
            errorDiv = document.createElement('div');
            errorDiv.classList.add('invalid-feedback');
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
        
        errorDiv.textContent = message;
    } else {
        // If field not found, show alert
        alert(message);
    }
}

/**
 * Initialize Charts for Dashboard and Reports
 */
function initializeCharts() {
    // Compliance Progress Chart
    const complianceCanvas = document.getElementById('compliance-chart');
    if (complianceCanvas) {
        const complianceChart = new Chart(complianceCanvas, {
            type: 'bar',
            data: {
                labels: ['GDPR', 'IEEE', 'NIST', 'ISO', 'Custom'],
                datasets: [{
                    label: 'Compliance %',
                    data: [85, 72, 90, 65, 78],
                    backgroundColor: [
                        'rgba(78, 115, 223, 0.8)',
                        'rgba(28, 200, 138, 0.8)',
                        'rgba(54, 185, 204, 0.8)',
                        'rgba(246, 194, 62, 0.8)',
                        'rgba(231, 74, 59, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // Bias Distribution Chart
    const biasCanvas = document.getElementById('bias-distribution-chart');
    if (biasCanvas) {
        const biasChart = new Chart(biasCanvas, {
            type: 'pie',
            data: {
                labels: ['Male', 'Female', 'Non-binary', 'Unknown'],
                datasets: [{
                    data: [45, 35, 5, 15],
                    backgroundColor: [
                        'rgba(78, 115, 223, 0.8)',
                        'rgba(28, 200, 138, 0.8)',
                        'rgba(246, 194, 62, 0.8)',
                        'rgba(54, 185, 204, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Learning Progress Chart
    const learningCanvas = document.getElementById('learning-progress-chart');
    if (learningCanvas) {
        const learningChart = new Chart(learningCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'In Progress', 'Not Started'],
                datasets: [{
                    data: [35, 15, 50],
                    backgroundColor: [
                        'rgba(28, 200, 138, 0.8)',
                        'rgba(246, 194, 62, 0.8)',
                        'rgba(231, 74, 59, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                cutout: '70%'
            }
        });
    }
}

/**
 * Set up dynamic content loaders
 */
function setupDynamicLoaders() {
    // Dynamic content loading for tabs or ajax content
    const dynamicLoaders = document.querySelectorAll('[data-load-content]');
    dynamicLoaders.forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('data-target');
            const contentUrl = this.getAttribute('data-load-content');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement && contentUrl) {
                targetElement.innerHTML = '<div class="text-center p-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
                
                fetch(contentUrl)
                    .then(response => response.text())
                    .then(data => {
                        targetElement.innerHTML = data;
                    })
                    .catch(error => {
                        targetElement.innerHTML = '<div class="alert alert-danger">Error loading content.</div>';
                        console.error('Error loading content:', error);
                    });
            }
        });
    });
}

/**
 * Handle AJAX form submissions
 */
function submitFormAjax(formId, successCallback, errorCallback) {
    const form = document.getElementById(formId);
    if (!form) return;

    const formData = new FormData(form);
    const url = form.getAttribute('action') || window.location.href;
    const method = form.getAttribute('method') || 'POST';

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (typeof successCallback === 'function') {
            successCallback(data);
        }
    })
    .catch(error => {
        if (typeof errorCallback === 'function') {
            errorCallback(error);
        } else {
            console.error('Error submitting form:', error);
        }
    });

    return false;
}

/**
 * Toggle consent for data storage in virtual assistant
 */
function toggleConsentStatus(checked) {
    const consentStatusSpan = document.getElementById('consent-status');
    if (consentStatusSpan) {
        consentStatusSpan.textContent = checked ? 'Enabled' : 'Disabled';
        consentStatusSpan.className = checked ? 'text-success' : 'text-danger';
    }
}

/**
 * Generate a PDF certificate
 */
function generateCertificatePDF(certificateId) {
    window.location.href = `/learning/certificate/${certificateId}/download`;
}

/**
 * Delete user data
 */
function deleteUserData(dataType) {
    if (!confirm(`Are you sure you want to delete your ${dataType} data? This action cannot be undone.`)) {
        return false;
    }
    
    const url = `/assistant/delete_${dataType}`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ confirm: true })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            window.location.reload();
        }
    })
    .catch(error => {
        console.error('Error deleting data:', error);
        alert('An error occurred while deleting your data. Please try again.');
    });
    
    return false;
} 