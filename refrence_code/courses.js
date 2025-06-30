/**
 * Courses page functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize AUTH UI
    if (window.AUTH) {
        window.AUTH.updateUI();
    }
    
    // Initialize UI components
    initializeUI();
    
    // Check if user is logged in
    if (!window.AUTH || !window.AUTH.isLoggedIn()) {
        // Redirect to login page if not logged in
        window.location.href = 'login.html';
        return;
    }
    
    const token = window.AUTH.getToken();

    // Elements
    const coursesContainer = document.getElementById('coursesContainer');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const noCoursesMessage = document.getElementById('noCoursesMessage');
    const courseCardTemplate = document.getElementById('courseCardTemplate');
    const recommendedCourses = document.getElementById('recommendedCourses');
    const courseSearch = document.getElementById('courseSearch');
    const filterCheckboxes = document.querySelectorAll('.filter-menu input[type="checkbox"]');
    
    // Stats elements
    const totalCoursesElement = document.getElementById('totalCourses');
    const inProgressCoursesElement = document.getElementById('inProgressCourses');
    const completedCoursesElement = document.getElementById('completedCourses');
    const certificatesEarnedElement = document.getElementById('certificatesEarned');

    // Store courses data
    let userCourses = [];
    let filteredCourses = [];

    // Load courses data
    loadUserCourses();
    loadRecommendedCourses();

    // Event listeners
    courseSearch.addEventListener('input', filterCourses);
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', filterCourses);
    });
    
    // Initialize filter dropdown toggle
    const filterBtn = document.querySelector('.filter-btn');
    const filterMenu = document.querySelector('.filter-menu');
    
    filterBtn.addEventListener('click', function() {
        filterMenu.classList.toggle('active');
    });
    
    // Close filter dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.filter-dropdown') && filterMenu.classList.contains('active')) {
            filterMenu.classList.remove('active');
        }
    });

    /**
     * Load user's enrolled courses
     */
    async function loadUserCourses() {
        try {
            // Show loading spinner
            loadingSpinner.style.display = 'flex';
            
            const response = await fetch('/api/my-courses', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load courses data');
            }

            const data = await response.json();
            userCourses = data.courses || [];
            filteredCourses = [...userCourses];
            
            // Update UI
            updateCourseStats(userCourses);
            renderCourses(userCourses);
        } catch (error) {
            console.error('Error loading courses:', error);
            showNotification('Error loading your courses', 'error');
            // Show no courses message
            loadingSpinner.style.display = 'none';
            noCoursesMessage.style.display = 'flex';
        }
    }

    /**
     * Load recommended courses
     */
    async function loadRecommendedCourses() {
        try {
            const response = await fetch('/api/courses', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load recommended courses');
            }

            const data = await response.json();
            const allCourses = data.courses || [];
            
            // Filter out courses the user is already enrolled in
            const userCourseIds = userCourses.map(course => course.id);
            const recommendedCoursesList = allCourses
                .filter(course => !userCourseIds.includes(course.id))
                .slice(0, 3); // Limit to 3 recommendations
            
            renderRecommendedCourses(recommendedCoursesList);
        } catch (error) {
            console.error('Error loading recommended courses:', error);
            // Hide recommended courses section if there's an error
            document.querySelector('.explore-courses').style.display = 'none';
        }
    }

    /**
     * Update course statistics
     */
    function updateCourseStats(courses) {
        if (!courses || !Array.isArray(courses)) {
            return;
        }
        
        // Total courses
        const total = courses.length;
        totalCoursesElement.textContent = total;
        
        // In progress courses (progress > 0 and < 100)
        const inProgress = courses.filter(course => course.progress > 0 && course.progress < 100).length;
        inProgressCoursesElement.textContent = inProgress;
        
        // Completed courses (progress = 100)
        const completed = courses.filter(course => course.progress === 100).length;
        completedCoursesElement.textContent = completed;
        
        // Not started courses (progress = 0)
        const notStarted = courses.filter(course => course.progress === 0).length;
        
        // Certificates earned (same as completed for now)
        certificatesEarnedElement.textContent = completed;
    }

    /**
     * Render user's enrolled courses
     */
    function renderCourses(courses) {
        // Hide loading spinner
        loadingSpinner.style.display = 'none';
        
        // Clear existing courses
        const existingCourses = coursesContainer.querySelectorAll('.course-card');
        existingCourses.forEach(course => course.remove());
        
        if (!courses || courses.length === 0) {
            // Show no courses message
            noCoursesMessage.style.display = 'flex';
            return;
        }
        
        // Hide no courses message
        noCoursesMessage.style.display = 'none';
        
        // Render each course
        courses.forEach(course => {
            const courseCard = courseCardTemplate.content.cloneNode(true);
            
            // Set course data
            courseCard.querySelector('.course-title').textContent = course.title;
            courseCard.querySelector('.course-description').textContent = course.description;
            courseCard.querySelector('.course-duration').textContent = course.duration || '0h';
            courseCard.querySelector('.course-modules').textContent = course.moduleCount || '0';
            courseCard.querySelector('.course-level').textContent = course.level || 'Beginner';
            
            // Set course image
            const courseImage = courseCard.querySelector('.course-image img');
            courseImage.src = course.imageUrl || 'https://via.placeholder.com/300x200';
            courseImage.alt = course.title;
            
            // Set progress
            const progressFill = courseCard.querySelector('.progress-fill');
            const progressText = courseCard.querySelector('.progress-text');
            const progress = course.progress || 0;
            
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `${progress}% Complete`;
            
            // Set button links
            const continueBtn = courseCard.querySelector('.continue-btn');
            const detailsBtn = courseCard.querySelector('.details-btn');
            
            continueBtn.href = `course-details.html?id=${course.id}`;
            detailsBtn.href = `course-details.html?id=${course.id}`;
            
            // Add course status class
            const courseCardElement = courseCard.querySelector('.course-card');
            if (progress === 100) {
                courseCardElement.classList.add('completed');
            } else if (progress > 0) {
                courseCardElement.classList.add('in-progress');
            } else {
                courseCardElement.classList.add('not-started');
            }
            
            // Append to container
            coursesContainer.appendChild(courseCard);
        });
    }

    /**
     * Render recommended courses
     */
    function renderRecommendedCourses(courses) {
        if (!courses || courses.length === 0) {
            // Hide recommended courses section if there are no recommendations
            document.querySelector('.explore-courses').style.display = 'none';
            return;
        }
        
        // Clear existing recommendations
        recommendedCourses.innerHTML = '';
        
        // Create a simplified version of the course card for recommendations
        courses.forEach(course => {
            const courseCard = document.createElement('div');
            courseCard.className = 'recommended-course-card';
            
            courseCard.innerHTML = `
                <div class="course-image">
                    <img src="${course.imageUrl || 'https://via.placeholder.com/300x200'}" alt="${course.title}">
                </div>
                <div class="course-content">
                    <h3 class="course-title">${course.title}</h3>
                    <p class="course-description">${course.description}</p>
                    <div class="course-meta">
                        <span><i class="fas fa-clock"></i> ${course.duration || '0h'}</span>
                        <span><i class="fas fa-layer-group"></i> ${course.moduleCount || '0'} modules</span>
                    </div>
                    <a href="course-details.html?id=${course.id}" class="btn-secondary">View Course</a>
                </div>
            `;
            
            recommendedCourses.appendChild(courseCard);
        });
    }

    /**
     * Filter courses based on search and filter criteria
     */
    function filterCourses() {
        // Get search term
        const searchTerm = courseSearch.value.toLowerCase();
        
        // Get selected filters
        const selectedFilters = Array.from(filterCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);
        
        // Filter courses
        filteredCourses = userCourses.filter(course => {
            // Search term filter
            const matchesSearch = course.title.toLowerCase().includes(searchTerm) || 
                                 course.description.toLowerCase().includes(searchTerm);
            
            // Status filter
            let matchesStatus = false;
            const progress = course.progress || 0;
            
            if (selectedFilters.includes('completed') && progress === 100) {
                matchesStatus = true;
            }
            
            if (selectedFilters.includes('in-progress') && progress > 0 && progress < 100) {
                matchesStatus = true;
            }
            
            if (selectedFilters.includes('not-started') && progress === 0) {
                matchesStatus = true;
            }
            
            return matchesSearch && matchesStatus;
        });
        
        // Render filtered courses
        renderCourses(filteredCourses);
    }

    /**
     * Initialize UI components
     */
    function initializeUI() {
        // Initialize profile dropdown
        const profileIcon = document.getElementById('profileIcon');
        const profileDropdown = document.getElementById('profileDropdown');
        
        if (profileIcon && profileDropdown) {
            profileIcon.addEventListener('click', function(e) {
                e.stopPropagation();
                profileDropdown.classList.toggle('active');
            });
            
            document.addEventListener('click', function(e) {
                if (!profileDropdown.contains(e.target) && !profileIcon.contains(e.target)) {
                    profileDropdown.classList.remove('active');
                }
            });
        }
        
        // Add logout functionality
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                if (window.AUTH) {
                    window.AUTH.logout();
                }
            });
        }
    }
    
    /**
     * Show notification message
     */
    function showNotification(message, type = 'info') {
        // Check if notification container exists, create if not
        let notificationContainer = document.querySelector('.notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.className = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add close button
        const closeBtn = document.createElement('span');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', function() {
            notification.remove();
        });
        notification.appendChild(closeBtn);
        
        // Add to container
        notificationContainer.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
});