/* Enhanced JavaScript for ChallengeTable inline admin */

document.addEventListener('DOMContentLoaded', function() {
    // Enhanced Add Database functionality
    initializeAddDatabaseButton();

    // Add helpful placeholders and validation
    const schemaTextareas = document.querySelectorAll('.field-schema_sql textarea');
    const runDatasetTextareas = document.querySelectorAll('.field-run_dataset_sql textarea');
    const submitDatasetTextareas = document.querySelectorAll('.field-submit_dataset_sql textarea');
    const tableNameInputs = document.querySelectorAll('.field-table_name input');

function initializeAddDatabaseButton() {
    // Enhance the add row button text and functionality
    const addRowLinks = document.querySelectorAll('.add-row a');
    addRowLinks.forEach(link => {
        // Update button text to be more descriptive
        if (link.textContent.includes('Add another')) {
            link.innerHTML = 'ADD DATABASE SCHEMA';
        }

        // Add click handler for better UX
        link.addEventListener('click', function(e) {
            // Show a brief loading state with animation
            const originalText = this.innerHTML;
            this.innerHTML = '⏳ CREATING DATABASE SCHEMA...';
            this.style.opacity = '0.7';
            this.style.transform = 'scale(0.95)';

            // Show success message
            setTimeout(() => {
                this.innerHTML = '✅ DATABASE SCHEMA ADDED!';
                this.style.background = 'linear-gradient(135deg, #4caf50, #388e3c)';

                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.style.opacity = '1';
                    this.style.transform = 'scale(1)';
                    this.style.background = '';

                    // Re-initialize placeholders for new forms
                    setTimeout(() => {
                        initializePlaceholders();
                        updateOrderFields();
                        highlightNewForm();
                    }, 100);
                }, 1000);
            }, 800);
        });
    });
}

function highlightNewForm() {
    // Highlight the newly added form
    const forms = document.querySelectorAll('.inline-group .stacked .form-row');
    const lastForm = forms[forms.length - 1];
    if (lastForm) {
        lastForm.style.border = '3px solid #4caf50';
        lastForm.style.background = '#e8f5e8';
        lastForm.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setTimeout(() => {
            lastForm.style.border = '';
            lastForm.style.background = '';
        }, 3000);
    }
}

    // Initialize placeholders
    initializePlaceholders();

function initializePlaceholders() {
    // Add placeholders to all current and new forms
    const schemaTextareas = document.querySelectorAll('.field-schema_sql textarea');
    const runDatasetTextareas = document.querySelectorAll('.field-run_dataset_sql textarea');
    const submitDatasetTextareas = document.querySelectorAll('.field-submit_dataset_sql textarea');
    const tableNameInputs = document.querySelectorAll('.field-table_name input');

    schemaTextareas.forEach(textarea => {
        if (!textarea.value) {
            textarea.placeholder = 'CREATE TABLE employees (\n  id INT PRIMARY KEY,\n  name VARCHAR(255),\n  department VARCHAR(100),\n  salary DECIMAL(10,2)\n);';
        }
    });

    runDatasetTextareas.forEach(textarea => {
        if (!textarea.value) {
            textarea.placeholder = 'INSERT INTO employees (id, name, department, salary) VALUES\n(1, \'John Doe\', \'Engineering\', 75000.00),\n(2, \'Jane Smith\', \'Marketing\', 65000.00);';
        }
    });

    submitDatasetTextareas.forEach(textarea => {
        if (!textarea.value) {
            textarea.placeholder = 'INSERT INTO employees (id, name, department, salary) VALUES\n(1, \'John Doe\', \'Engineering\', 75000.00),\n(2, \'Jane Smith\', \'Marketing\', 65000.00),\n(3, \'Bob Johnson\', \'Engineering\', 80000.00);';
        }
    });

    tableNameInputs.forEach(input => {
        if (!input.value) {
            input.placeholder = 'e.g., employees, orders, customers';
        }
    });
}

    // Auto-update order fields
    function updateOrderFields() {
        const orderInputs = document.querySelectorAll('.field-order input');
        orderInputs.forEach((input, index) => {
            if (!input.value || input.value === '0') {
                input.value = (index + 1) * 10;
            }
        });
    }

    // Update order fields when new rows are added
    const addRowLinks = document.querySelectorAll('.add-row a');
    addRowLinks.forEach(link => {
        link.addEventListener('click', function() {
            setTimeout(updateOrderFields, 100);
        });
    });

    // Initial order update
    updateOrderFields();

    // Add syntax highlighting hints
    function addSyntaxHints() {
        const allTextareas = document.querySelectorAll('.inline-group textarea');
        allTextareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                // Simple validation feedback
                const value = this.value.toLowerCase();
                const parent = this.closest('.form-row');
                
                if (parent) {
                    // Remove existing validation classes
                    parent.classList.remove('sql-valid', 'sql-warning', 'sql-error');
                    
                    if (this.classList.contains('field-schema_sql')) {
                        if (value.includes('create table')) {
                            parent.classList.add('sql-valid');
                        } else if (value.length > 0) {
                            parent.classList.add('sql-warning');
                        }
                    } else if (this.classList.contains('field-run_dataset_sql') || 
                               this.classList.contains('field-submit_dataset_sql')) {
                        if (value.includes('insert into')) {
                            parent.classList.add('sql-valid');
                        } else if (value.length > 0) {
                            parent.classList.add('sql-warning');
                        }
                    }
                }
            });
        });
    }

    addSyntaxHints();

    // Add helpful tooltips
    function addTooltips() {
        const schemaFields = document.querySelectorAll('.field-schema_sql');
        const runDatasetFields = document.querySelectorAll('.field-run_dataset_sql');
        const submitDatasetFields = document.querySelectorAll('.field-submit_dataset_sql');

        schemaFields.forEach(field => {
            const label = field.querySelector('label');
            if (label) {
                label.title = 'Define the table structure. The system will automatically add a flag_id column and unique table names.';
            }
        });

        runDatasetFields.forEach(field => {
            const label = field.querySelector('label');
            if (label) {
                label.title = 'Test data that users see when running queries. Used for flag_id=1.';
            }
        });

        submitDatasetFields.forEach(field => {
            const label = field.querySelector('label');
            if (label) {
                label.title = 'Validation data for final submission checking. Used for flag_id=2. Should be more comprehensive than run dataset.';
            }
        });
    }

    addTooltips();
});

// CSS for validation feedback
const style = document.createElement('style');
style.textContent = `
    .form-row.sql-valid {
        border-left: 4px solid #28a745;
    }
    .form-row.sql-warning {
        border-left: 4px solid #ffc107;
    }
    .form-row.sql-error {
        border-left: 4px solid #dc3545;
    }
`;
document.head.appendChild(style);
