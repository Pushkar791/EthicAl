/**
 * EthicAI - Form Handlers and AJAX Utilities
 * Provides utilities for handling form submissions and AJAX operations
 */

/**
 * Initialize AJAX form handling for the given form
 * @param {string} formSelector - CSS selector for the form
 * @param {object} options - Configuration options
 */
function setupAjaxForm(formSelector, options = {}) {
    const form = document.querySelector(formSelector);
    if (!form) return;
    
    const defaults = {
        successCallback: null,
        errorCallback: null,
        beforeSubmit: null,
        resetOnSuccess: true,
        showLoadingIndicator: true,
        loadingIndicatorTarget: null,
        redirectOnSuccess: null,
        validationRules: null
    };
    
    const settings = {...defaults, ...options};
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form if validation rules provided
        if (settings.validationRules && !validateForm(form, settings.validationRules)) {
            return;
        }
        
        // Call beforeSubmit callback if provided
        if (settings.beforeSubmit && typeof settings.beforeSubmit === 'function') {
            const result = settings.beforeSubmit(form);
            if (result === false) return;
        }
        
        // Show loading indicator if enabled
        let loadingIndicator = null;
        if (settings.showLoadingIndicator) {
            loadingIndicator = showLoading(settings.loadingIndicatorTarget);
        }
        
        // Create form data
        const formData = new FormData(form);
        
        // Submit form via fetch API
        fetch(form.action, {
            method: form.method || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            }
            
            return response.text();
        })
        .then(data => {
            // Hide loading indicator
            if (loadingIndicator) {
                hideLoading(loadingIndicator);
            }
            
            // Reset form if enabled
            if (settings.resetOnSuccess) {
                form.reset();
            }
            
            // Call success callback if provided
            if (settings.successCallback && typeof settings.successCallback === 'function') {
                settings.successCallback(data, form);
            }
            
            // Redirect if specified
            if (settings.redirectOnSuccess) {
                window.location.href = settings.redirectOnSuccess;
            }
        })
        .catch(error => {
            console.error('Error submitting form:', error);
            
            // Hide loading indicator
            if (loadingIndicator) {
                hideLoading(loadingIndicator);
            }
            
            // Call error callback if provided
            if (settings.errorCallback && typeof settings.errorCallback === 'function') {
                settings.errorCallback(error, form);
            } else {
                // Default error handling
                alert('An error occurred while processing your request. Please try again.');
            }
        });
    });
}

/**
 * Validate a form based on provided rules
 * @param {HTMLFormElement} form - The form to validate
 * @param {object} rules - Validation rules
 * @returns {boolean} - Whether the form is valid
 */
function validateForm(form, rules) {
    let isValid = true;
    
    for (const fieldName in rules) {
        const field = form.elements[fieldName];
        if (!field) continue;
        
        const fieldRules = rules[fieldName];
        const errorElement = document.getElementById(`${fieldName}-error`);
        
        // Clear previous errors
        field.classList.remove('is-invalid');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
        
        // Apply validation rules
        if (fieldRules.required && !field.value.trim()) {
            isValid = false;
            markFieldInvalid(field, errorElement, fieldRules.requiredMessage || 'This field is required');
        } else if (fieldRules.minLength && field.value.length < fieldRules.minLength) {
            isValid = false;
            markFieldInvalid(field, errorElement, `Minimum length is ${fieldRules.minLength} characters`);
        } else if (fieldRules.pattern && !new RegExp(fieldRules.pattern).test(field.value)) {
            isValid = false;
            markFieldInvalid(field, errorElement, fieldRules.patternMessage || 'Invalid format');
        } else if (fieldRules.custom && typeof fieldRules.custom === 'function') {
            const customResult = fieldRules.custom(field.value, form);
            if (customResult !== true) {
                isValid = false;
                markFieldInvalid(field, errorElement, customResult || 'Invalid value');
            }
        }
    }
    
    return isValid;
}

/**
 * Mark a form field as invalid
 * @param {HTMLElement} field - The form field
 * @param {HTMLElement} errorElement - The error element
 * @param {string} message - The error message
 */
function markFieldInvalid(field, errorElement, message) {
    field.classList.add('is-invalid');
    
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    } else {
        // Create error element if it doesn't exist
        const newErrorElement = document.createElement('div');
        newErrorElement.id = `${field.name}-error`;
        newErrorElement.className = 'invalid-feedback';
        newErrorElement.textContent = message;
        field.parentNode.appendChild(newErrorElement);
    }
    
    // Focus the first invalid field
    if (!document.querySelector('.is-invalid:focus')) {
        field.focus();
    }
}

/**
 * Show a loading indicator
 * @param {string|HTMLElement} target - Target element or selector to insert the loading indicator
 * @returns {HTMLElement} - The loading indicator element
 */
function showLoading(target) {
    const loadingHTML = `
        <div class="loading-indicator">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    let targetElement = null;
    
    if (target) {
        targetElement = typeof target === 'string' ? document.querySelector(target) : target;
    }
    
    if (!targetElement) {
        // Create a floating loading indicator
        const indicator = document.createElement('div');
        indicator.className = 'loading-overlay';
        indicator.innerHTML = loadingHTML;
        document.body.appendChild(indicator);
        return indicator;
    } else {
        // Insert loading indicator into target element
        const indicator = document.createElement('div');
        indicator.innerHTML = loadingHTML;
        const loadingElement = indicator.firstElementChild;
        targetElement.appendChild(loadingElement);
        return loadingElement;
    }
}

/**
 * Hide a loading indicator
 * @param {HTMLElement} indicator - The loading indicator element
 */
function hideLoading(indicator) {
    if (indicator) {
        if (indicator.classList.contains('loading-overlay')) {
            // Remove floating loading indicator
            document.body.removeChild(indicator);
        } else {
            // Remove inline loading indicator
            indicator.parentNode.removeChild(indicator);
        }
    }
}

/**
 * Perform a modal confirmation
 * @param {string} message - Confirmation message
 * @param {function} onConfirm - Callback function to execute on confirmation
 * @param {function} onCancel - Callback function to execute on cancellation
 */
function confirmAction(message, onConfirm, onCancel = null) {
    if (confirm(message)) {
        if (onConfirm && typeof onConfirm === 'function') {
            onConfirm();
        }
    } else if (onCancel && typeof onCancel === 'function') {
        onCancel();
    }
}

/**
 * Handle AJAX form submission for the bias analyzer module
 */
function initBiasAnalyzerForms() {
    // Handle model upload form
    setupAjaxForm('#model-upload-form', {
        beforeSubmit: function(form) {
            const modelFile = form.elements['model_file'];
            const apiEndpoint = form.elements['api_endpoint'];
            
            if ((!modelFile || !modelFile.files.length) && (!apiEndpoint || !apiEndpoint.value.trim())) {
                alert('Please either upload a model file or provide an API endpoint');
                return false;
            }
            
            return true;
        },
        successCallback: function(data, form) {
            if (data && data.model_id) {
                window.location.href = `/bias_analyzer/analyze_model/${data.model_id}`;
            } else {
                window.location.href = '/bias_analyzer/models';
            }
        },
        errorCallback: function(error, form) {
            console.error('Model upload error:', error);
            alert('An error occurred while uploading the model. Please try again.');
        },
        resetOnSuccess: false
    });
    
    // Handle analyze model form
    setupAjaxForm('#analyze-model-form', {
        beforeSubmit: function(form) {
            const testDataset = form.elements['test_dataset'];
            const biasTypes = form.querySelectorAll('input[name="bias_types"]:checked');
            
            if (!testDataset || !testDataset.files.length) {
                alert('Please upload a test dataset');
                return false;
            }
            
            if (biasTypes.length === 0) {
                alert('Please select at least one bias type to analyze');
                return false;
            }
            
            // Show a loading message - this can take time
            alert('Your analysis is being processed. This may take a few moments.');
            return true;
        },
        successCallback: function(data, form) {
            if (data && data.report_id) {
                window.location.href = `/bias_analyzer/view_report/${data.report_id}`;
            } else if (data && data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                // Default fallback if no specific redirect is provided
                window.location.reload();
            }
        },
        errorCallback: function(error, form) {
            console.error('Bias analysis error:', error);
            alert('An error occurred while analyzing the model. Please try again.');
            
            // Enable the submit button again
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = false;
            }
        },
        resetOnSuccess: false
    });
}

/**
 * Handle AJAX form submission for the virtual assistant module
 */
function initVirtualAssistantForms() {
    // Handle chat form
    setupAjaxForm('#chat-form', {
        beforeSubmit: function(form) {
            const query = form.elements['query'].value.trim();
            
            if (!query) {
                return false;
            }
            
            // Add user message to chat
            const chatHistory = document.getElementById('chat-history');
            if (chatHistory) {
                const userMessage = document.createElement('div');
                userMessage.className = 'user-message mb-3';
                userMessage.innerHTML = `
                    <div class="message-content alert alert-secondary">
                        ${escapeHtml(query)}
                    </div>
                `;
                chatHistory.appendChild(userMessage);
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }
            
            return true;
        },
        successCallback: function(data, form) {
            const chatHistory = document.getElementById('chat-history');
            const responseElement = document.getElementById('chat-response');
            
            // Clear loading indicator
            if (responseElement) {
                responseElement.innerHTML = '';
            }
            
            // Add system response
            if (chatHistory && data.response) {
                const systemMessage = document.createElement('div');
                systemMessage.className = 'system-message mb-3';
                systemMessage.innerHTML = `
                    <div class="message-content alert alert-info">
                        ${data.response}
                    </div>
                `;
                chatHistory.appendChild(systemMessage);
                chatHistory.scrollTop = chatHistory.scrollHeight;
                
                // Speak the response if voice feedback is enabled
                if (window.speakText && typeof window.speakText === 'function') {
                    window.speakText(data.response);
                }
            }
            
            // Clear the input
            form.elements['query'].value = '';
            form.elements['query'].focus();
        },
        errorCallback: function(error, form) {
            const responseElement = document.getElementById('chat-response');
            console.error('Assistant error:', error);
            
            if (responseElement) {
                let errorMessage = 'Sorry, there was an error processing your request. Please try again.';
                
                // If we have specific error details, show them
                if (error.response && error.response.status === 500) {
                    try {
                        // Try to parse the error response
                        error.response.json().then(data => {
                            if (data.details) {
                                errorMessage = `Error: ${data.details}`;
                            }
                            showErrorMessage(responseElement, errorMessage);
                        }).catch(() => {
                            showErrorMessage(responseElement, errorMessage);
                        });
                    } catch (e) {
                        showErrorMessage(responseElement, errorMessage);
                    }
                } else {
                    showErrorMessage(responseElement, errorMessage);
                }
            }
        },
        loadingIndicatorTarget: '#chat-response',
        loadingIndicatorHTML: `
            <div class="system-message mb-3">
                <div class="message-content alert alert-info d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    Thinking...
                </div>
            </div>
        `,
        resetOnSuccess: false
    });
}

/**
 * Helper function to show error message in the chat
 */
function showErrorMessage(element, message) {
    element.innerHTML = `
        <div class="system-message mb-3">
            <div class="message-content alert alert-danger">
                ${message}
            </div>
        </div>
    `;
    
    // Scroll chat window to see the error
    const chatHistory = document.getElementById('chat-history');
    if (chatHistory) {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

/**
 * Helper function to escape HTML in user input
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize forms when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize bias analyzer forms
    initBiasAnalyzerForms();
    
    // Initialize virtual assistant forms
    initVirtualAssistantForms();
    
    // Set up global AJAX error handling
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
    });
    
    // Add unhandled promise rejection handling
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
    });
}); 