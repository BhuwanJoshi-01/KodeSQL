// Base JavaScript for SQL Playground

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // Default to dark theme or detect system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDark ? 'dark' : 'dark'); // Default to dark theme
    }
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update theme toggle icon
    const themeToggle = document.querySelector('.theme-toggle .material-icons');
    if (themeToggle) {
        themeToggle.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    // Send theme preference to server if user is authenticated
    if (window.user && window.user.is_authenticated) {
        fetch('/auth/api/update-theme/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ theme: newTheme })
        }).catch(console.error);
    }
}

// Mobile Menu
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('mobile-open');
}



// CSRF Token Helper
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

// API Helper Functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Message System
function showMessage(message, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    
    const messageElement = document.createElement('div');
    messageElement.className = `message message-${type}`;
    
    const iconMap = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
    };
    
    messageElement.innerHTML = `
        <span class="material-icons">${iconMap[type] || 'info'}</span>
        ${message}
        <button class="message-close" onclick="this.parentElement.remove()">
            <span class="material-icons">close</span>
        </button>
    `;
    
    messagesContainer.appendChild(messageElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageElement.parentElement) {
            messageElement.remove();
        }
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

// Loading State Management
function setLoading(element, isLoading) {
    if (isLoading) {
        element.disabled = true;
        element.classList.add('loading');
        
        // Add spinner if it doesn't exist
        if (!element.querySelector('.spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'spinner';
            element.insertBefore(spinner, element.firstChild);
        }
    } else {
        element.disabled = false;
        element.classList.remove('loading');
        
        // Remove spinner
        const spinner = element.querySelector('.spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(input);
        }
    });
    
    return isValid;
}

function showFieldError(input, message) {
    clearFieldError(input);
    
    input.classList.add('error');
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    
    input.parentElement.appendChild(errorElement);
}

function clearFieldError(input) {
    input.classList.remove('error');
    const errorElement = input.parentElement.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
}

// Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search (if implemented)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Implement search functionality
        }
        
        // Ctrl/Cmd + Enter for execute query (if on editor page)
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const executeBtn = document.querySelector('.execute-query-btn');
            if (executeBtn && !executeBtn.disabled) {
                e.preventDefault();
                executeBtn.click();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.open');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

// Modal Management
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modal) {
    if (typeof modal === 'string') {
        modal = document.getElementById(modal);
    }
    
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

// Auto-hide messages after delay
function autoHideMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach((message, index) => {
        // Auto-hide success and info messages after 5 seconds
        if (message.classList.contains('message-success') || message.classList.contains('message-info')) {
            setTimeout(() => {
                if (message.parentElement) {
                    message.style.opacity = '0';
                    message.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        message.remove();
                    }, 300);
                }
            }, 5000 + (index * 500)); // Stagger the hiding
        }
        // Auto-hide warning messages after 8 seconds
        else if (message.classList.contains('message-warning')) {
            setTimeout(() => {
                if (message.parentElement) {
                    message.style.opacity = '0';
                    message.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        message.remove();
                    }, 300);
                }
            }, 8000 + (index * 500));
        }
        // Error messages stay until manually closed
    });
}

// Enhanced message display with better animations
function enhanceMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach((message, index) => {
        // Add entrance animation delay
        message.style.animationDelay = `${index * 0.1}s`;

        // Add click to dismiss functionality
        message.addEventListener('click', (e) => {
            if (!e.target.closest('.message-close')) {
                message.style.opacity = '0';
                message.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    message.remove();
                }, 300);
            }
        });
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initKeyboardShortcuts();
    autoHideMessages();
    enhanceMessages();

    // Close mobile menu and dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        const navMenu = document.querySelector('.nav-menu');
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');

        if (navMenu && navMenu.classList.contains('mobile-open') &&
            !navMenu.contains(e.target) &&
            !mobileMenuBtn.contains(e.target)) {
            navMenu.classList.remove('mobile-open');
        }
    });
});

// Newsletter Form Handler
function handleNewsletterSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const emailInput = form.querySelector('.newsletter-input');
    const submitBtn = form.querySelector('.newsletter-btn');
    const email = emailInput.value.trim();

    if (!email) {
        showMessage('Please enter a valid email address', 'error');
        return;
    }

    // Disable form during submission
    emailInput.disabled = true;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="material-icons">hourglass_empty</span>';

    // Simulate API call (replace with actual implementation)
    setTimeout(() => {
        // Reset form
        emailInput.disabled = false;
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="material-icons">send</span>';
        emailInput.value = '';

        // Show success message
        showMessage('Thank you for subscribing! You\'ll receive our latest updates.', 'success');
    }, 1500);
}

// Make newsletter function globally available
window.handleNewsletterSubmit = handleNewsletterSubmit;

// Export functions for use in other scripts
window.sqlPlayground = {
    toggleTheme,
    toggleMobileMenu,
    apiRequest,
    showMessage,
    setLoading,
    validateForm,
    openModal,
    closeModal,
    getCsrfToken,
    handleNewsletterSubmit
};
