// Admin Forms JavaScript - Ensures proper editor initialization and visibility

document.addEventListener('DOMContentLoaded', function() {
    // Fix CKEditor5 visibility issues
    function fixCKEditorVisibility() {
        // Wait for CKEditor5 to be fully loaded
        setTimeout(function() {
            const editors = document.querySelectorAll('.ck-editor');
            editors.forEach(function(editor) {
                const editable = editor.querySelector('.ck-editor__editable');
                if (editable) {
                    // Force visibility styles
                    editable.style.background = 'var(--bg-primary, #ffffff)';
                    editable.style.color = 'var(--text-primary, #1e293b)';
                    editable.style.minHeight = '300px';
                    
                    // Check for dark theme
                    if (document.documentElement.getAttribute('data-theme') === 'dark') {
                        editable.style.background = 'var(--bg-primary, #0f172a)';
                        editable.style.color = 'var(--text-primary, #f8fafc)';
                    }
                    
                    // Ensure all content is visible
                    const content = editable.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, span, div');
                    content.forEach(function(element) {
                        element.style.color = 'inherit';
                    });
                }
            });
        }, 500);
    }
    
    // Fix textarea visibility
    function fixTextareaVisibility() {
        const textareas = document.querySelectorAll('textarea.form-control');
        textareas.forEach(function(textarea) {
            textarea.style.background = 'var(--bg-primary, #ffffff)';
            textarea.style.color = 'var(--text-primary, #1e293b)';
            
            // Check for dark theme
            if (document.documentElement.getAttribute('data-theme') === 'dark') {
                textarea.style.background = 'var(--bg-primary, #0f172a)';
                textarea.style.color = 'var(--text-primary, #f8fafc)';
            }
        });
    }
    
    // Fix all form controls
    function fixFormControlsVisibility() {
        const controls = document.querySelectorAll('.form-control');
        controls.forEach(function(control) {
            control.style.background = 'var(--bg-primary, #ffffff)';
            control.style.color = 'var(--text-primary, #1e293b)';
            
            // Check for dark theme
            if (document.documentElement.getAttribute('data-theme') === 'dark') {
                control.style.background = 'var(--bg-primary, #0f172a)';
                control.style.color = 'var(--text-primary, #f8fafc)';
            }
        });
    }
    
    // Initialize fixes
    fixCKEditorVisibility();
    fixTextareaVisibility();
    fixFormControlsVisibility();
    
    // Re-apply fixes when theme changes
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'data-theme') {
                setTimeout(function() {
                    fixCKEditorVisibility();
                    fixTextareaVisibility();
                    fixFormControlsVisibility();
                }, 100);
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['data-theme']
    });
    
    // Fix editors when they are dynamically created
    const editorObserver = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.classList && node.classList.contains('ck-editor')) {
                        setTimeout(fixCKEditorVisibility, 100);
                    }
                    
                    // Check for nested editors
                    const nestedEditors = node.querySelectorAll && node.querySelectorAll('.ck-editor');
                    if (nestedEditors && nestedEditors.length > 0) {
                        setTimeout(fixCKEditorVisibility, 100);
                    }
                }
            });
        });
    });
    
    editorObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Additional fix for CKEditor5 content after typing
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('ck-editor__editable')) {
            const content = e.target.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, span, div');
            content.forEach(function(element) {
                element.style.color = 'inherit';
            });
        }
    });
    
    // Fix for CKEditor5 focus events
    document.addEventListener('focus', function(e) {
        if (e.target.classList.contains('ck-editor__editable')) {
            setTimeout(function() {
                const content = e.target.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, span, div');
                content.forEach(function(element) {
                    element.style.color = 'inherit';
                });
            }, 50);
        }
    }, true);
    
    // Debug function to check editor visibility
    window.debugEditorVisibility = function() {
        console.log('=== Editor Visibility Debug ===');
        
        const editors = document.querySelectorAll('.ck-editor');
        console.log('Found', editors.length, 'CKEditor instances');
        
        editors.forEach(function(editor, index) {
            const editable = editor.querySelector('.ck-editor__editable');
            if (editable) {
                const styles = window.getComputedStyle(editable);
                console.log('Editor', index + 1, ':', {
                    background: styles.backgroundColor,
                    color: styles.color,
                    visibility: styles.visibility,
                    display: styles.display,
                    opacity: styles.opacity
                });
            }
        });
        
        const textareas = document.querySelectorAll('textarea.form-control');
        console.log('Found', textareas.length, 'textarea elements');
        
        textareas.forEach(function(textarea, index) {
            const styles = window.getComputedStyle(textarea);
            console.log('Textarea', index + 1, ':', {
                background: styles.backgroundColor,
                color: styles.color,
                visibility: styles.visibility,
                display: styles.display,
                opacity: styles.opacity
            });
        });
    };
    
    // Auto-run debug in development
    if (window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        window.location.hostname.includes('localhost')) {
        setTimeout(function() {
            console.log('Admin Forms JS loaded. Run debugEditorVisibility() to check editor visibility.');
        }, 1000);
    }
});
