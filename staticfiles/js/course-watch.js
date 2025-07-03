// Course Watch Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeCourseWatch();
});

function initializeCourseWatch() {
    // Initialize tab functionality
    initializeTabs();
    
    // Initialize module dropdowns
    initializeModuleDropdowns();
    
    // Initialize lesson completion tracking
    initializeLessonTracking();
    
    // Initialize video player
    initializeVideoPlayer();
}

function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            showTab(targetId);
        });
    });
}

function showTab(tabId) {
    // Hide all tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Show the selected tab panel
    const targetPanel = document.getElementById(tabId);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
    
    // Update tab button states
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Find and activate the clicked tab
    document.querySelectorAll('.tab').forEach(tab => {
        const onclick = tab.getAttribute('onclick');
        if (onclick && onclick.includes(tabId)) {
            tab.classList.add('active');
        }
    });
}

function initializeModuleDropdowns() {
    // Set up click handlers for module dropdowns
    const moduleLinks = document.querySelectorAll('.module-link');
    
    moduleLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't trigger if clicking on a lesson link
            if (e.target.closest('.lesson-item')) {
                return;
            }
            toggleModuleDropdown(this);
        });
    });
}

function toggleModuleDropdown(element) {
    const dropdown = element.nextElementSibling;
    const arrow = element.querySelector('.dropdown-arrow');
    
    if (dropdown && dropdown.classList.contains('module-dropdown')) {
        const isExpanded = dropdown.classList.contains('expanded');
        
        if (isExpanded) {
            dropdown.classList.remove('expanded');
            if (arrow) arrow.style.transform = 'rotate(0deg)';
        } else {
            dropdown.classList.add('expanded');
            if (arrow) arrow.style.transform = 'rotate(180deg)';
        }
    }
}

function initializeLessonTracking() {
    // Set up lesson completion checkboxes
    const checkboxes = document.querySelectorAll('.lesson-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function(e) {
            e.stopPropagation(); // Prevent triggering module dropdown
            const lessonId = this.getAttribute('onchange').match(/\d+/)[0];
            toggleLessonComplete(lessonId);
        });
    });
}

function toggleLessonComplete(lessonId) {
    const checkbox = document.querySelector(`input[onchange*="${lessonId}"]`);
    const isCompleted = checkbox.checked;
    
    // Send AJAX request to update lesson completion
    fetch(`/courses/api/lesson-complete/${lessonId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({
            completed: isCompleted
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update progress bar
            updateProgressBar(data.progress_percentage);
            
            // Show success message
            showNotification(
                isCompleted ? 'Lesson marked as complete!' : 'Lesson marked as incomplete',
                'success'
            );
        } else {
            // Revert checkbox state on error
            checkbox.checked = !isCompleted;
            showNotification('Error updating lesson progress', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        checkbox.checked = !isCompleted;
        showNotification('Error updating lesson progress', 'error');
    });
}

function updateProgressBar(percentage) {
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.course-progress span[style*="color"]');
    
    if (progressFill) {
        progressFill.style.width = percentage + '%';
    }
    
    if (progressText) {
        progressText.textContent = percentage + '%';
    }
}

function initializeVideoPlayer() {
    const video = document.querySelector('.lesson-video');
    
    if (video && video.tagName === 'VIDEO') {
        // Add video event listeners for progress tracking
        video.addEventListener('timeupdate', function() {
            // Track video progress (could be used for analytics)
            const progress = (this.currentTime / this.duration) * 100;
            // You can implement video progress tracking here
        });
        
        video.addEventListener('ended', function() {
            // Auto-mark lesson as complete when video ends
            const checkbox = document.querySelector('.lesson-item.lesson-active .lesson-checkbox');
            if (checkbox && !checkbox.checked) {
                checkbox.checked = true;
                const lessonId = checkbox.getAttribute('onchange').match(/\d+/)[0];
                toggleLessonComplete(lessonId);
            }
        });
    }
}

function showAddNoteModal() {
    // Placeholder for note modal functionality
    showNotification('Note functionality coming soon!', 'info');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '1000',
        opacity: '0',
        transform: 'translateY(-20px)',
        transition: 'all 0.3s ease'
    });
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.background = '#10b981';
            break;
        case 'error':
            notification.style.background = '#ef4444';
            break;
        case 'warning':
            notification.style.background = '#f59e0b';
            break;
        default:
            notification.style.background = '#3b82f6';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        return csrfToken.value;
    }
    
    // Try to get from cookie
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    return '';
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // Arrow key navigation for lessons
    if (e.key === 'ArrowLeft') {
        const prevBtn = document.querySelector('.prev-btn');
        if (prevBtn) {
            window.location.href = prevBtn.href;
        }
    } else if (e.key === 'ArrowRight') {
        const nextBtn = document.querySelector('.next-btn');
        if (nextBtn) {
            window.location.href = nextBtn.href;
        }
    }
    
    // Space bar to play/pause video
    if (e.code === 'Space') {
        const video = document.querySelector('.lesson-video');
        if (video && video.tagName === 'VIDEO') {
            e.preventDefault();
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        }
    }
});

// Auto-expand current module on page load
document.addEventListener('DOMContentLoaded', function() {
    const activeModule = document.querySelector('.module-item.module-active');
    if (activeModule) {
        const dropdown = activeModule.querySelector('.module-dropdown');
        const arrow = activeModule.querySelector('.dropdown-arrow');
        
        if (dropdown) {
            dropdown.classList.add('expanded');
        }
        if (arrow) {
            arrow.style.transform = 'rotate(180deg)';
        }
    }
});

// Smooth scrolling for lesson navigation
document.addEventListener('DOMContentLoaded', function() {
    const activeLesson = document.querySelector('.lesson-item.lesson-active');
    if (activeLesson) {
        activeLesson.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
});

// Video URL processing for YouTube and Vimeo embeds
function processVideoUrl(url) {
    // YouTube URL processing
    if (url.includes('youtube.com/watch?v=')) {
        const videoId = url.split('v=')[1].split('&')[0];
        return `https://www.youtube.com/embed/${videoId}`;
    }

    if (url.includes('youtu.be/')) {
        const videoId = url.split('youtu.be/')[1].split('?')[0];
        return `https://www.youtube.com/embed/${videoId}`;
    }

    // Vimeo URL processing
    if (url.includes('vimeo.com/')) {
        const videoId = url.split('vimeo.com/')[1].split('?')[0];
        return `https://player.vimeo.com/video/${videoId}`;
    }

    return url;
}

// Save user's scroll position in sidebar
function saveScrollPosition() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        localStorage.setItem('courseWatchSidebarScroll', sidebar.scrollTop);
    }
}

function restoreScrollPosition() {
    const sidebar = document.querySelector('.sidebar');
    const savedPosition = localStorage.getItem('courseWatchSidebarScroll');

    if (sidebar && savedPosition) {
        sidebar.scrollTop = parseInt(savedPosition);
    }
}

// Auto-save scroll position
document.addEventListener('DOMContentLoaded', function() {
    restoreScrollPosition();

    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.addEventListener('scroll', debounce(saveScrollPosition, 300));
    }
});

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Enhanced video player controls
function enhanceVideoPlayer() {
    const video = document.querySelector('.lesson-video');

    if (video && video.tagName === 'VIDEO') {
        // Add custom controls overlay
        const controlsOverlay = document.createElement('div');
        controlsOverlay.className = 'video-controls-overlay';
        controlsOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        `;

        const playButton = document.createElement('button');
        playButton.innerHTML = '▶';
        playButton.style.cssText = `
            background: rgba(255,255,255,0.9);
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            pointer-events: auto;
        `;

        controlsOverlay.appendChild(playButton);
        video.parentNode.style.position = 'relative';
        video.parentNode.appendChild(controlsOverlay);

        // Show/hide controls
        video.addEventListener('pause', () => {
            controlsOverlay.style.opacity = '1';
            playButton.innerHTML = '▶';
        });

        video.addEventListener('play', () => {
            controlsOverlay.style.opacity = '0';
        });

        playButton.addEventListener('click', () => {
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        });

        // Show controls on hover
        video.parentNode.addEventListener('mouseenter', () => {
            if (video.paused) {
                controlsOverlay.style.opacity = '1';
            }
        });

        video.parentNode.addEventListener('mouseleave', () => {
            if (video.paused) {
                setTimeout(() => {
                    controlsOverlay.style.opacity = '0';
                }, 2000);
            }
        });
    }
}

// Initialize enhanced video player
document.addEventListener('DOMContentLoaded', function() {
    enhanceVideoPlayer();
});

// Fullscreen API support
function toggleFullscreen() {
    const videoContainer = document.querySelector('.video-container');

    if (!document.fullscreenElement) {
        videoContainer.requestFullscreen().catch(err => {
            console.log(`Error attempting to enable fullscreen: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
}

// Add fullscreen button to video container
document.addEventListener('DOMContentLoaded', function() {
    const videoContainer = document.querySelector('.video-container');

    if (videoContainer && document.fullscreenEnabled) {
        const fullscreenBtn = document.createElement('button');
        fullscreenBtn.innerHTML = '⛶';
        fullscreenBtn.className = 'fullscreen-btn';
        fullscreenBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 16px;
            z-index: 10;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        `;

        fullscreenBtn.addEventListener('click', toggleFullscreen);
        fullscreenBtn.addEventListener('mouseenter', () => {
            fullscreenBtn.style.opacity = '1';
        });
        fullscreenBtn.addEventListener('mouseleave', () => {
            fullscreenBtn.style.opacity = '0.7';
        });

        videoContainer.appendChild(fullscreenBtn);
    }
});
