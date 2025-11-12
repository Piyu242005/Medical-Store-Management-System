// Toggle sidebar
const menuToggle = document.getElementById('menu-toggle');
const wrapper = document.getElementById('wrapper');

if (menuToggle) {
    menuToggle.addEventListener('click', function(e) {
        e.preventDefault();
        wrapper.classList.toggle('toggled');
        // Store sidebar state in localStorage
        const isToggled = wrapper.classList.contains('toggled');
        localStorage.setItem('sidebarToggled', isToggled);
    });
}

// Check for saved user preference, if any, on page load
window.addEventListener('DOMContentLoaded', function() {
    // Apply saved sidebar state
    if (localStorage.getItem('sidebarToggled') === 'true') {
        wrapper.classList.add('toggled');
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Format currency inputs
const currencyInputs = document.querySelectorAll('input[data-type="currency"]');
currencyInputs.forEach(function(input) {
    input.addEventListener('input', function(e) {
        // Remove all non-digit characters
        let value = this.value.replace(/\D/g, '');
        // Format as currency (2 decimal places)
        value = (value / 100).toFixed(2);
        // Update the input value
        this.value = formatCurrency(value);
    });
});

function formatCurrency(value) {
    // Format number with 2 decimal places and comma as thousand separator
    return parseFloat(value).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Form validation
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

// Auto-calculate total price based on quantity and unit price
function calculateTotal() {
    const quantity = parseFloat(document.getElementById('quantity').value) || 0;
    const unitPrice = parseFloat(document.getElementById('unit_price').value) || 0;
    const total = quantity * unitPrice;
    document.getElementById('total_price').value = total.toFixed(2);
}

// If we have quantity and unit price fields, add event listeners
const quantityInput = document.getElementById('quantity');
const unitPriceInput = document.getElementById('unit_price');

if (quantityInput && unitPriceInput) {
    quantityInput.addEventListener('input', calculateTotal);
    unitPriceInput.addEventListener('input', calculateTotal);
}

// Initialize DataTables if present
if (typeof $ !== 'undefined' && $.fn.DataTable) {
    $(document).ready(function() {
        $('#dataTable').DataTable({
            responsive: true,
            pageLength: 10,
            lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "All"]]
        });
    });
}

// Search functionality for medicine list
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = document.querySelectorAll('#medicineTable tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

// Auto-format phone numbers
const phoneInputs = document.querySelectorAll('input[type="tel"]');
phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
        let x = this.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
        this.value = !x[2] ? x[1] : x[1] + '-' + x[2] + (x[3] ? '-' + x[3] : '');
    });
});

// Auto-format date inputs
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set minimum date to today for expiry dates
        if (input.id === 'expiry_date') {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('min', today);
        }
    });
});
