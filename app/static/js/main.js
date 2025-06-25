document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Dashboard file actions
    const fileActionButtons = document.querySelectorAll('.file-action-btn');
    fileActionButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const fileId = this.dataset.fileId;
            const action = this.dataset.action;

            // You can implement specific actions here
            console.log(`Action ${action} for file ${fileId}`);
        });
    });

    // Logout confirmation
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to log out?')) {
                e.preventDefault();
            }
        });
    }
});