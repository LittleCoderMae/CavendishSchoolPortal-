// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            }
        });
    });

    // Payment amount validation
    const amountInput = document.getElementById('amount');
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (value < 1) {
                this.setCustomValidity('Amount must be at least K1');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Course registration checkboxes limit
    const courseCheckboxes = document.querySelectorAll('input[name="courses"]');
    if (courseCheckboxes.length > 0) {
        const maxCourses = 6; // Maximum courses per semester
        courseCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const checkedCount = document.querySelectorAll('input[name="courses"]:checked').length;
                if (checkedCount > maxCourses) {
                    alert(`You can only register for maximum ${maxCourses} courses per semester.`);
                    this.checked = false;
                }
            });
        });
    }

    // Print docket functionality
    const printButtons = document.querySelectorAll('.btn-success:contains("Print Docket")');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });
});

// jQuery-like contains selector
document.querySelectorAll('*').forEach(element => {
    if (element.textContent.includes('Print Docket')) {
        element.classList.add('print-docket-btn');
    }
});