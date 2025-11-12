/* ============================================
   THEME SWITCHER - Manages theme selection and persistence
   ============================================ */

// Initialize theme from localStorage or use default
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'dark-purple';
    applyTheme(savedTheme);
    updateThemeButtons(savedTheme);
});

/**
 * Set the active theme and save to localStorage
 * @param {string} themeName - 'dark-purple', 'dark-red', or 'light'
 */
function setTheme(themeName) {
    localStorage.setItem('theme', themeName);
    applyTheme(themeName);
    updateThemeButtons(themeName);
}

/**
 * Apply theme by adding/removing class from body
 * @param {string} themeName - Theme class name
 */
function applyTheme(themeName) {
    // Remove all theme classes
    document.body.classList.remove('theme-light', 'theme-dark-purple', 'theme-dark-red');
    
    // Add selected theme class (default dark-purple needs no class)
    if (themeName !== 'dark-purple') {
        document.body.classList.add('theme-' + themeName);
    }
}

/**
 * Update theme button active states
 * @param {string} themeName - Currently active theme
 */
function updateThemeButtons(themeName) {
    const buttons = document.querySelectorAll('.theme-btn');
    buttons.forEach(function(btn) {
        btn.classList.remove('active');
    });
    
    // Find and mark the active button
    buttons.forEach(function(btn) {
        if (btn.getAttribute('onclick').includes(themeName)) {
            btn.classList.add('active');
        }
    });
}

// Support for dynamically added theme buttons
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('theme-btn')) {
        const onclickAttr = event.target.getAttribute('onclick');
        const match = onclickAttr.match(/setTheme\('([^']+)'\)/);
        if (match) {
            setTheme(match[1]);
        }
    }
});
