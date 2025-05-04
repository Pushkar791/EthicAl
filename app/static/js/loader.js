/**
 * EthicAI - Gene Loader Animation
 * Shows a rotating gene-style loader when navigating between sections
 */

// Create the loader element
function createLoader() {
    if (document.getElementById('gene-loader')) return;
    
    const loader = document.createElement('div');
    loader.id = 'gene-loader';
    loader.className = 'gene-loader-overlay';
    loader.innerHTML = `
        <div class="gene-loader">
            <div class="gene-strand">
                <div class="gene-helix"></div>
                <div class="gene-helix"></div>
            </div>
            <p class="gene-loader-text">Loading...</p>
        </div>
    `;
    document.body.appendChild(loader);
}

// Show the loader
function showLoader() {
    createLoader();
    document.getElementById('gene-loader').style.display = 'flex';
    document.body.classList.add('overflow-hidden');
}

// Hide the loader
function hideLoader() {
    const loader = document.getElementById('gene-loader');
    if (loader) {
        loader.style.display = 'none';
        document.body.classList.remove('overflow-hidden');
    }
}

// Show loader for a specific duration
function showLoaderFor(duration = 2000) {
    showLoader();
    return new Promise(resolve => {
        setTimeout(() => {
            hideLoader();
            resolve();
        }, duration);
    });
}

// Initialize the loader for all navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Add loader for all internal navigation links
    const internalLinks = document.querySelectorAll('a[href^="/"]:not([data-no-loader])');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Skip if it's an external link or has data-no-loader attribute
            if (this.hasAttribute('data-no-loader') || this.getAttribute('target') === '_blank') {
                return;
            }
            
            const href = this.getAttribute('href');
            // Skip for # links or javascript: links
            if (href === '#' || href.startsWith('javascript:') || href.startsWith('#')) {
                return;
            }
            
            e.preventDefault();
            showLoaderFor(2000).then(() => {
                window.location.href = href;
            });
        });
    });
    
    // Add loader for form submissions
    const forms = document.querySelectorAll('form:not([data-no-loader])');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!this.hasAttribute('data-no-loader')) {
                showLoader();
            }
        });
    });
    
    // Handle back button
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            hideLoader();
        }
    });
    
    // Initialize loader for section transitions within the page
    const sectionButtons = document.querySelectorAll('[data-section-target]');
    sectionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetSection = this.getAttribute('data-section-target');
            const currentSection = document.querySelector('.section.active');
            
            if (targetSection && document.getElementById(targetSection)) {
                showLoaderFor(2000).then(() => {
                    if (currentSection) currentSection.classList.remove('active');
                    document.getElementById(targetSection).classList.add('active');
                });
            }
        });
    });
});

// Manually add transition for next/prev assessment sections
if (document.querySelector('.next-btn') || document.querySelector('.prev-btn')) {
    document.addEventListener('DOMContentLoaded', function() {
        const nextButtons = document.querySelectorAll('.next-btn');
        const prevButtons = document.querySelectorAll('.prev-btn');
        
        nextButtons.forEach(button => {
            const originalClickHandler = button.onclick;
            button.onclick = null;
            
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const nextSectionId = this.getAttribute('data-next');
                const currentSection = this.closest('.assessment-section');
                
                // Show loader before transitioning
                await showLoaderFor(2000);
                
                // Hide current section, show next section
                currentSection.style.display = 'none';
                document.getElementById(nextSectionId).style.display = 'block';
                
                // Update progress bar if needed
                const progressBar = document.querySelector('.progress-bar');
                if (progressBar) {
                    let progress = 0;
                    if (nextSectionId === 'section2') progress = 33;
                    if (nextSectionId === 'section3') progress = 66;
                    if (nextSectionId === 'results') progress = 100;
                    
                    progressBar.style.width = progress + '%';
                    progressBar.setAttribute('aria-valuenow', progress);
                    progressBar.textContent = progress + '%';
                }
            });
        });
        
        prevButtons.forEach(button => {
            const originalClickHandler = button.onclick;
            button.onclick = null;
            
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const prevSectionId = this.getAttribute('data-prev');
                const currentSection = this.closest('.assessment-section');
                
                // Show loader before transitioning
                await showLoaderFor(2000);
                
                // Hide current section, show previous section
                currentSection.style.display = 'none';
                document.getElementById(prevSectionId).style.display = 'block';
                
                // Update progress bar if needed
                const progressBar = document.querySelector('.progress-bar');
                if (progressBar) {
                    let progress = 0;
                    if (prevSectionId === 'section1') progress = 0;
                    if (prevSectionId === 'section2') progress = 33;
                    
                    progressBar.style.width = progress + '%';
                    progressBar.setAttribute('aria-valuenow', progress);
                    progressBar.textContent = progress + '%';
                }
            });
        });
    });
} 