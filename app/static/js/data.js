document.addEventListener('DOMContentLoaded', function() {
    // -------------------- Existing File Upload Handling --------------------
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileSize = this.files[0]?.size / 1024 / 1024; // MB
            const maxSize = 16; // MB

            if (fileSize > maxSize) {
                alert(`File size exceeds the maximum limit of ${maxSize}MB`);
                this.value = '';
            }
        });
    }

    // -------------------- Column Selection Toggles --------------------
    const selectAllBtn = document.getElementById('select-all-columns');
    const deselectAllBtn = document.getElementById('deselect-all-columns');
    const columnCheckboxes = document.querySelectorAll('input[name="columns"]');

    if (selectAllBtn && deselectAllBtn) {
        selectAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            columnCheckboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
        });

        deselectAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            columnCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
        });
    }

    // -------------------- AJAX Form Submission --------------------
    const analysisForm = document.getElementById('analysis-form');
    const predictionForm = document.getElementById('prediction-form');

    if (analysisForm) setupAjaxForm(analysisForm);
    if (predictionForm) setupAjaxForm(predictionForm);

    // -------------------- Dashboard: Search / Filter Tables --------------------
    function filterTable(inputId, tableId) {
        const input = document.getElementById(inputId);
        if (!input) return;
        input.addEventListener('keyup', function() {
            const filter = input.value.toLowerCase();
            const table = document.getElementById(tableId);
            if (!table) return;
            const rows = table.getElementsByTagName('tr');
            for (let i = 1; i < rows.length; i++) {
                rows[i].style.display = rows[i].textContent.toLowerCase().includes(filter) ? '' : 'none';
            }
        });
    }
    filterTable('searchFile', 'dataFilesTableContent');
    filterTable('searchReport', 'reportsTableContent');

    // -------------------- Dashboard: Sort Table --------------------
    function sortTable(colIndex, tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        const rows = Array.from(table.rows).slice(1);
        const asc = table.getAttribute('data-sort-asc') === 'true';
        rows.sort((a, b) => a.cells[colIndex].textContent.trim().localeCompare(b.cells[colIndex].textContent.trim()));
        if (asc) rows.reverse();
        rows.forEach(row => table.tBodies[0].appendChild(row));
        table.setAttribute('data-sort-asc', !asc);
    }

    // Add click events for sortable columns in Data Files table
    const dataFilesTable = document.getElementById('dataFilesTableContent');
    if (dataFilesTable) {
        const headers = dataFilesTable.querySelectorAll('th');
        headers.forEach((th, index) => {
            th.addEventListener('click', () => sortTable(index, 'dataFilesTableContent'));
        });
    }
});

// -------------------- AJAX Form Helper --------------------
function setupAjaxForm(form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (data.error) {
                showError(data.error);
            }
        })
        .catch(error => {
            showError('An error occurred. Please try again.');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        });
    });
}

// -------------------- Error Alert Helper --------------------
function showError(message) {
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger alert-dismissible fade show';
    errorAlert.role = 'alert';
    errorAlert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    const container = document.querySelector('.container.mt-4');
    if (container) {
        container.prepend(errorAlert);
    }
}
