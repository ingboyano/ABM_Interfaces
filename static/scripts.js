/**
 * VM Management System JavaScript
 * Handles UI interactions, form validations, and dynamic elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle backup frequency field visibility based on backup required checkbox
    const backupCheckbox = document.getElementById('backup_required');
    const backupFrequencyGroup = document.getElementById('backup_frequency_group');
    
    if (backupCheckbox && backupFrequencyGroup) {
        // Initial state
        toggleBackupFrequency();
        
        // Add event listener
        backupCheckbox.addEventListener('change', toggleBackupFrequency);
        
        function toggleBackupFrequency() {
            if (backupCheckbox.checked) {
                backupFrequencyGroup.classList.remove('d-none');
            } else {
                backupFrequencyGroup.classList.add('d-none');
            }
        }
    }
    
    // VM deletion confirmation
    const deleteButtons = document.querySelectorAll('.btn-delete-vm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this VM? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Search form submission on input change with debounce
    const searchInput = document.getElementById('search');
    if (searchInput) {
        let debounceTimer;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                document.getElementById('search-form').submit();
            }, 500);
        });
    }
    
    // Initialize Select2 for VLAN dropdowns
    $(document).ready(function() {
        // Dynamic form fields for VLANs
        if (typeof $.fn.select2 !== 'undefined') {
            $('.select2-vlans').select2({
                theme: 'bootstrap-5',
                placeholder: 'Seleccione VLANs',
                allowClear: true,
                width: '100%'
            });
            
            console.log("Select2 and VLAN modal handlers initialized successfully");
        } else {
            console.error("Select2 library not loaded");
        }
    });
    
    // Form validation - Bootstrap custom validation
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
    
    // Responsive tables - Add data attributes for mobile view
    const tables = document.querySelectorAll('.table-responsive-cards table');
    tables.forEach(table => {
        const headerCells = table.querySelectorAll('thead th');
        const headerTexts = Array.from(headerCells).map(cell => cell.textContent.trim());
        
        const bodyRows = table.querySelectorAll('tbody tr');
        bodyRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                if (index < headerTexts.length) {
                    cell.setAttribute('data-label', headerTexts[index]);
                }
            });
        });
    });
});
