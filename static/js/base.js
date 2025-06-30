// Base JavaScript for SQL Playground

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
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

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initKeyboardShortcuts();
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
        const navMenu = document.querySelector('.nav-menu');
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        
        if (navMenu.classList.contains('mobile-open') && 
            !navMenu.contains(e.target) && 
            !mobileMenuBtn.contains(e.target)) {
            navMenu.classList.remove('mobile-open');
        }
    });
});

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
    getCsrfToken
};
