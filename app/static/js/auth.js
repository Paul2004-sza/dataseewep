document.addEventListener('DOMContentLoaded', function() {
    // Client-side validation for auth forms
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add('was-validated');
        }, false);
    });

    // Password strength indicator (for registration)
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strengthIndicator = document.getElementById('password-strength');
            if (strengthIndicator) {
                const strength = calculatePasswordStrength(this.value);
                strengthIndicator.textContent = strength.text;
                strengthIndicator.className = 'password-strength ' + strength.class;
            }
        });
    }
});

function calculatePasswordStrength(password) {
    let strength = 0;

    // Length check
    if (password.length > 7) strength++;
    if (password.length > 11) strength++;

    // Character variety checks
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    // Return result based on strength
    if (password.length === 0) {
        return { text: '', class: '' };
    } else if (strength <= 2) {
        return { text: 'Weak', class: 'weak' };
    } else if (strength <= 4) {
        return { text: 'Moderate', class: 'moderate' };
    } else {
        return { text: 'Strong', class: 'strong' };
    }
}