// admin_custom.js

// Function for sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

// Functions for toast notifications
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Functions for counters
let counter = 0;
function incrementCounter() {
    counter++;
    document.getElementById('counterDisplay').innerText = counter;
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!');
    });
}

// Export to CSV functionality
function exportToCSV(filename) {
    const data = ...; // Your data here
    const csvContent = ...; // Create CSV from data
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

// Live search functionality
function liveSearch() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const items = document.querySelectorAll('.search-item');
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(filter) ? '' : 'none';
    });
}

// Example usage of functions
// toggleSidebar(); // Call to toggle sidebar
// incrementCounter(); // Call to increment counter