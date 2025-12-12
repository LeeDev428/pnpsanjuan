// Toast Notification System
function showToast(message, type = 'info', title = '') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '⚠'
    };
    
    const titles = {
        success: title || 'Success',
        error: title || 'Error',
        info: title || 'Information',
        warning: title || 'Warning'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <div class="toast-content">
            <div class="toast-title">${titles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="closeToast(this)">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        closeToast(toast.querySelector('.toast-close'));
    }, 5000);
}

function closeToast(button) {
    const toast = button.closest('.toast');
    toast.classList.add('hide');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Show flash messages as toasts on page load
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert-message');
    flashMessages.forEach(msg => {
        const type = msg.dataset.category || 'info';
        const message = msg.textContent.trim();
        showToast(message, type);
    });
});
