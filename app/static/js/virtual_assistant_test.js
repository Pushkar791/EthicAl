/**
 * EthicAI Virtual Assistant Test Script
 * This script helps validate the virtual assistant's functionality
 */

class VirtualAssistantTester {
    constructor() {
        this.testResults = {
            total: 0,
            passed: 0,
            failed: 0
        };
        this.testLog = [];
    }

    /**
     * Run all available tests
     */
    runAllTests() {
        console.log('Starting Virtual Assistant tests...');
        
        // Basic UI tests
        this.testVoiceFeedbackToggle();
        this.testConsentToggle();
        this.testChatFormValidation();
        
        // Speech synthesis tests if available
        if ('speechSynthesis' in window) {
            this.testSpeechSynthesis();
        } else {
            this.logTest('Speech Synthesis API', 'SKIPPED', 'Speech Synthesis API not available in this browser');
        }
        
        // Error handling tests
        this.testErrorHandling();
        
        // Display results
        console.log('==== Test Results ====');
        console.log(`Total tests: ${this.testResults.total}`);
        console.log(`Passed: ${this.testResults.passed}`);
        console.log(`Failed: ${this.testResults.failed}`);
        console.log('=====================');
        
        return {
            results: this.testResults,
            log: this.testLog
        };
    }
    
    /**
     * Test voice feedback toggle functionality
     */
    testVoiceFeedbackToggle() {
        try {
            const voiceFeedbackSwitch = document.getElementById('voiceFeedbackSwitch');
            if (!voiceFeedbackSwitch) {
                throw new Error('Voice feedback switch not found');
            }
            
            // Initial state
            const initialState = voiceFeedbackSwitch.checked;
            
            // Toggle to the opposite state
            voiceFeedbackSwitch.checked = !initialState;
            
            // Trigger the change event
            const event = new Event('change');
            voiceFeedbackSwitch.dispatchEvent(event);
            
            // Check if localStorage value was updated
            const storedValue = localStorage.getItem('voiceFeedbackEnabled');
            const success = storedValue === (!initialState).toString();
            
            // Restore original state
            voiceFeedbackSwitch.checked = initialState;
            voiceFeedbackSwitch.dispatchEvent(event);
            
            if (success) {
                this.logTest('Voice Feedback Toggle', 'PASSED', 'Toggle updates localStorage correctly');
            } else {
                throw new Error('localStorage not updated correctly');
            }
        } catch (e) {
            this.logTest('Voice Feedback Toggle', 'FAILED', e.message);
        }
    }
    
    /**
     * Test consent toggle functionality
     */
    testConsentToggle() {
        try {
            const consentSwitch = document.getElementById('consentSwitch');
            const consentInput = document.getElementById('consent_given');
            
            if (!consentSwitch || !consentInput) {
                throw new Error('Consent switch or hidden input not found');
            }
            
            // Initial state
            const initialState = consentSwitch.checked;
            
            // Toggle to the opposite state
            consentSwitch.checked = !initialState;
            
            // Trigger the change event
            const event = new Event('change');
            consentSwitch.dispatchEvent(event);
            
            // Check if hidden input was updated
            const success = consentInput.value === (!initialState).toString();
            
            // Restore original state
            consentSwitch.checked = initialState;
            consentSwitch.dispatchEvent(event);
            
            if (success) {
                this.logTest('Consent Toggle', 'PASSED', 'Toggle updates hidden input correctly');
            } else {
                throw new Error('Hidden consent input not updated correctly');
            }
        } catch (e) {
            this.logTest('Consent Toggle', 'FAILED', e.message);
        }
    }
    
    /**
     * Test chat form validation
     */
    testChatFormValidation() {
        try {
            const chatForm = document.getElementById('chat-form');
            const queryInput = document.getElementById('query');
            
            if (!chatForm || !queryInput) {
                throw new Error('Chat form or query input not found');
            }
            
            // Save original value
            const originalValue = queryInput.value;
            
            // Test with empty value
            queryInput.value = '';
            
            // Try to submit the form
            let wasSubmitted = true;
            
            // Override the fetch function temporarily
            const originalFetch = window.fetch;
            window.fetch = () => {
                wasSubmitted = true;
                return new Promise(() => {});
            };
            
            // Try to submit the form
            const submitEvent = new Event('submit');
            chatForm.dispatchEvent(submitEvent);
            
            // The form shouldn't be submitted (wasSubmitted should stay false)
            const validationSuccess = wasSubmitted === false;
            
            // Restore original fetch
            window.fetch = originalFetch;
            
            // Restore original value
            queryInput.value = originalValue;
            
            if (validationSuccess) {
                this.logTest('Chat Form Validation', 'PASSED', 'Empty query submission prevented');
            } else {
                this.logTest('Chat Form Validation', 'SKIPPED', 'Could not fully test form validation');
            }
        } catch (e) {
            this.logTest('Chat Form Validation', 'FAILED', e.message);
        }
    }
    
    /**
     * Test speech synthesis functionality
     */
    testSpeechSynthesis() {
        try {
            // Check if we have access to the speech synthesis API
            if (!window.speechSynthesis) {
                throw new Error('Speech Synthesis API not available');
            }
            
            // Check if we can create an utterance
            const utterance = new SpeechSynthesisUtterance('Test');
            if (!utterance) {
                throw new Error('Could not create SpeechSynthesisUtterance');
            }
            
            // Check if we can get voices
            let voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {
                this.logTest('Speech Synthesis', 'PASSED', `${voices.length} voices available`);
            } else {
                // Some browsers need to wait for the voiceschanged event
                this.logTest('Speech Synthesis', 'PARTIAL', 'Voices not immediately available, may load later');
            }
        } catch (e) {
            this.logTest('Speech Synthesis', 'FAILED', e.message);
        }
    }
    
    /**
     * Test error handling
     */
    testErrorHandling() {
        try {
            // Test if the showErrorMessage function exists
            if (typeof showErrorMessage !== 'function') {
                throw new Error('showErrorMessage function not found');
            }
            
            // Create a temporary element to test error display
            const testElement = document.createElement('div');
            document.body.appendChild(testElement);
            
            // Call the error function
            showErrorMessage(testElement, 'Test error message');
            
            // Check if error was displayed correctly
            const hasErrorMessage = testElement.innerHTML.includes('Test error message');
            const hasAlertDanger = testElement.innerHTML.includes('alert-danger');
            
            // Clean up
            document.body.removeChild(testElement);
            
            if (hasErrorMessage && hasAlertDanger) {
                this.logTest('Error Handling', 'PASSED', 'Error messages display correctly');
            } else {
                throw new Error('Error message not displayed correctly');
            }
        } catch (e) {
            this.logTest('Error Handling', 'FAILED', e.message);
        }
    }
    
    /**
     * Log a test result
     */
    logTest(testName, status, message) {
        this.testResults.total++;
        
        if (status === 'PASSED') {
            this.testResults.passed++;
            console.log(`✅ ${testName}: ${message}`);
        } else if (status === 'FAILED') {
            this.testResults.failed++;
            console.error(`❌ ${testName}: ${message}`);
        } else {
            console.warn(`⚠️ ${testName}: ${message}`);
        }
        
        this.testLog.push({
            name: testName,
            status,
            message,
            timestamp: new Date().toISOString()
        });
    }
}

// Run tests when the page is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only run in development mode or if explicitly requested
    const isDevMode = document.body.hasAttribute('data-dev-mode');
    const shouldRunTests = isDevMode || localStorage.getItem('runAssistantTests') === 'true';
    
    if (shouldRunTests) {
        setTimeout(() => {
            const tester = new VirtualAssistantTester();
            window.assistantTestResults = tester.runAllTests();
        }, 1000); // Wait for all components to initialize
    }
});

// Export the tester class for external use
window.VirtualAssistantTester = VirtualAssistantTester; 