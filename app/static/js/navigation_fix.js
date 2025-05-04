/**
 * EthicAI - Navigation and Button Click Handler Fix
 * This script fixes issues with navigation links and button functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix navigation links to use direct links instead of AJAX
    fixNavigationLinks();
    
    // Fix approval buttons in manager dashboard
    setupApprovalButtons();
    
    // Fix chat form submission
    fixChatForm();

    // Fix bias analyzer links
    fixBiasAnalyzerLinks();
});

/**
 * Fix navigation links to use direct links instead of potentially problematic AJAX
 */
function fixNavigationLinks() {
    // For all dropdown menu links
    const allDropdownLinks = document.querySelectorAll('.dropdown-menu a');
    allDropdownLinks.forEach(link => {
        if (link.getAttribute('href') && link.getAttribute('href') !== '#') {
            link.addEventListener('click', function(e) {
                // Don't prevent default behavior, allow natural navigation
                window.location.href = this.href;
            });
        }
    });
    
    // For Bias Analyzer navigation
    const biasLinks = document.querySelectorAll('a[href*="bias_analyzer"]');
    biasLinks.forEach(link => {
        // Remove event listener that's interfering with navigation
        // No need to add special handling, just let links work naturally
    });
    
    // For Virtual Assistant navigation
    const assistantLinks = document.querySelectorAll('a[href*="virtual_assistant"]');
    assistantLinks.forEach(link => {
        // Remove event listener that's interfering with navigation
        // No need to add special handling, just let links work naturally
    });
    
    // For Governance navigation
    const governanceLinks = document.querySelectorAll('a[href*="governance"]');
    governanceLinks.forEach(link => {
        // Remove event listener that's interfering with navigation
        // No need to add special handling, just let links work naturally
    });
}

/**
 * Fix bias analyzer links and functionality
 */
function fixBiasAnalyzerLinks() {
    // Fix model links
    const modelLinks = document.querySelectorAll('a[href*="bias_analyzer/model"]');
    modelLinks.forEach(link => {
        // Let default navigation work
    });
    
    // Fix report links
    const reportLinks = document.querySelectorAll('a[href*="bias_analyzer/report"]');
    reportLinks.forEach(link => {
        // Let default navigation work
    });
    
    // Fix new analysis link - ensure it works properly
    const newAnalysisLink = document.querySelector('a[href*="bias_analyzer/new_analysis"]');
    if (newAnalysisLink) {
        // Let default navigation work - make sure we're not adding conflicting listeners
    }
    
    // Fix upload model form if it exists
    const uploadForm = document.getElementById('model-upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Make sure form has proper file or API endpoint
            const modelFile = document.getElementById('model_file');
            const apiEndpoint = document.getElementById('api_endpoint');
            
            if ((!modelFile || !modelFile.files.length) && (!apiEndpoint || !apiEndpoint.value.trim())) {
                e.preventDefault();
                alert('Please either upload a model file or provide an API endpoint');
            }
        });
    }
    
    // Fix analyze model form if it exists
    const analyzeForm = document.getElementById('analyze-model-form');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            // Make sure a test dataset is selected
            const testDataset = document.getElementById('test_dataset');
            if (!testDataset || !testDataset.files.length) {
                e.preventDefault();
                alert('Please upload a test dataset');
                return;
            }
            
            // Make sure at least one bias type is selected
            const biasTypes = document.querySelectorAll('input[name="bias_types"]:checked');
            if (biasTypes.length === 0) {
                e.preventDefault();
                alert('Please select at least one bias type to analyze');
                return;
            }

            // Add loading indicator to show progress
            const analyzeButton = document.getElementById('analyze-button');
            if (analyzeButton) {
                analyzeButton.disabled = true;
                analyzeButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
            }
        });
    }
}

/**
 * Set up approval/reject/review buttons in the manager dashboard
 */
function setupApprovalButtons() {
    // Approve buttons
    const approveButtons = document.querySelectorAll('.btn-success[data-model]');
    approveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const modelName = this.getAttribute('data-model');
            const requestor = this.getAttribute('data-requestor');
            
            if (!modelName || !requestor) {
                console.error('Missing model name or requestor data');
                return;
            }
            
            // Make AJAX call to approve
            approveRequest(modelName, requestor);
        });
    });
    
    // Reject buttons
    const rejectButtons = document.querySelectorAll('.btn-danger[data-model]');
    rejectButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const modelName = this.getAttribute('data-model');
            const requestor = this.getAttribute('data-requestor');
            
            if (!modelName || !requestor) {
                console.error('Missing model name or requestor data');
                return;
            }
            
            // Make AJAX call to reject
            rejectRequest(modelName, requestor);
        });
    });
    
    // Review buttons
    const reviewButtons = document.querySelectorAll('.btn-info[data-model]');
    reviewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const modelName = this.getAttribute('data-model');
            
            if (!modelName) {
                console.error('Missing model name data');
                return;
            }
            
            // Navigate to review page
            reviewRequest(modelName);
        });
    });
}

/**
 * Fix chat form submission to prevent redirect
 */
function fixChatForm() {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(chatForm);
            const queryInput = document.getElementById('query');
            const chatHistory = document.getElementById('chat-history');
            const responseElement = document.getElementById('chat-response');
            
            if (!queryInput || !queryInput.value.trim()) {
                return;
            }
            
            // Add user message to chat
            const userMessage = document.createElement('div');
            userMessage.className = 'user-message mb-3';
            userMessage.innerHTML = `
                <div class="message-content alert alert-secondary">
                    ${queryInput.value}
                </div>
            `;
            chatHistory.appendChild(userMessage);
            
            // Display loading indicator
            if (responseElement) {
                responseElement.innerHTML = `
                    <div class="system-message mb-3">
                        <div class="message-content alert alert-info d-flex align-items-center">
                            <div class="spinner-border spinner-border-sm me-2" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            Thinking...
                        </div>
                    </div>
                `;
            }
            
            // Use fetch to submit form via AJAX
            fetch(chatForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear loading indicator
                if (responseElement) {
                    responseElement.innerHTML = '';
                }
                
                // Add system response
                const systemMessage = document.createElement('div');
                systemMessage.className = 'system-message mb-3';
                systemMessage.innerHTML = `
                    <div class="message-content alert alert-info">
                        ${data.response}
                    </div>
                `;
                chatHistory.appendChild(systemMessage);
                
                // Scroll to bottom of chat
                chatHistory.scrollTop = chatHistory.scrollHeight;
                
                // Clear the input
                if (queryInput) {
                    queryInput.value = '';
                    queryInput.focus();
                }
            })
            .catch(error => {
                console.error('Error submitting chat form:', error);
                
                // Show error message
                if (responseElement) {
                    responseElement.innerHTML = `
                        <div class="system-message mb-3">
                            <div class="message-content alert alert-danger">
                                Sorry, there was an error processing your request. Please try again.
                            </div>
                        </div>
                    `;
                }
            });
        });
    }
}

/**
 * Approve a request
 */
function approveRequest(modelName, requestor) {
    // Check for required data
    if (!modelName || !requestor) {
        console.error("Missing required data for approval");
        alert('Error: Missing model data for approval');
        return;
    }

    // Confirm action
    if (!confirm(`Are you sure you want to approve the request for "${modelName}"?`)) {
        return;
    }

    // Make AJAX call to approve endpoint
    fetch('/governance/approve_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            model_name: modelName,
            requestor: requestor
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        alert(`Request for ${modelName} has been approved.`);
        // Refresh the page to show updated status
        window.location.reload();
    })
    .catch(error => {
        console.error('Error approving request:', error);
        alert('An error occurred while approving the request. Please try again.');
    });
}

/**
 * Reject a request
 */
function rejectRequest(modelName, requestor) {
    // Check for required data
    if (!modelName || !requestor) {
        console.error("Missing required data for rejection");
        alert('Error: Missing model data for rejection');
        return;
    }

    const reason = prompt("Please provide a reason for rejection:", "");
    if (reason === null) return; // User cancelled
    
    // Make AJAX call to reject endpoint
    fetch('/governance/reject_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            model_name: modelName,
            requestor: requestor,
            reason: reason
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        alert(`Request for ${modelName} has been rejected.`);
        // Refresh the page to show updated status
        window.location.reload();
    })
    .catch(error => {
        console.error('Error rejecting request:', error);
        alert('An error occurred while rejecting the request. Please try again.');
    });
}

/**
 * Review a request
 */
function reviewRequest(modelName) {
    // Check for required data
    if (!modelName) {
        console.error("Missing model name for review");
        alert('Error: Missing model data for review');
        return;
    }

    // Navigate to the review page
    window.location.href = `/governance/review_request?model=${encodeURIComponent(modelName)}`;
} 