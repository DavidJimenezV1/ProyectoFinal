/**
 * TEJOS OLÍMPICA - CUSTOM ADMIN JAVASCRIPT
 * Modern, Interactive & Playful Features
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        
        // Initialize all features
        initWelcomeAnimation();
        initCardAnimations();
        initTableEnhancements();
        initFormEnhancements();
        initSearchEnhancements();
        initTooltips();
        initConfetti();
        
        console.log('🎯 Tejos Olímpica Admin Panel - Loaded!');
    });

    /**
     * Welcome Animation
     */
    function initWelcomeAnimation() {
        const header = document.querySelector('#header');
        if (header) {
            header.style.opacity = '0';
            setTimeout(() => {
                header.style.transition = 'opacity 0.5s ease-in';
                header.style.opacity = '1';
            }, 100);
        }
    }

    /**
     * Card Animations
     */
    function initCardAnimations() {
        const modules = document.querySelectorAll('.module');
        
        modules.forEach((module, index) => {
            module.style.opacity = '0';
            module.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                module.style.transition = 'all 0.5s ease-out';
                module.style.opacity = '1';
                module.style.transform = 'translateY(0)';
            }, 100 * index);
        });

        // Add hover effects
        modules.forEach(module => {
            module.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
            });
            
            module.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    /**
     * Table Enhancements
     */
    function initTableEnhancements() {
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach((row, index) => {
                // Alternating row animations
                row.style.opacity = '0';
                row.style.transform = 'translateX(-20px)';
                
                setTimeout(() => {
                    row.style.transition = 'all 0.3s ease-out';
                    row.style.opacity = '1';
                    row.style.transform = 'translateX(0)';
                }, 50 * index);

                // Row click highlight
                row.addEventListener('click', function(e) {
                    // Don't trigger on input/button clicks
                    if (e.target.tagName === 'INPUT' || 
                        e.target.tagName === 'BUTTON' || 
                        e.target.tagName === 'A') {
                        return;
                    }
                    
                    rows.forEach(r => r.classList.remove('selected-row'));
                    this.classList.add('selected-row');
                });
            });
        });

        // Add CSS for selected row
        const style = document.createElement('style');
        style.textContent = `
            .selected-row {
                background: linear-gradient(135deg, #4ECDC4 0%, #44AF69 100%) !important;
                color: white !important;
                transform: scale(1.02) !important;
            }
            .selected-row a {
                color: white !important;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Form Enhancements
     */
    function initFormEnhancements() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"], textarea, select');
        
        inputs.forEach(input => {
            // Add floating label effect
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
                
                // Add sparkle effect
                createSparkle(this);
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });

            // Add validation feedback
            input.addEventListener('input', function() {
                if (this.validity.valid && this.value) {
                    this.style.borderColor = '#44AF69';
                    addCheckmark(this);
                } else if (!this.validity.valid && this.value) {
                    this.style.borderColor = '#E74C3C';
                    removeCheckmark(this);
                }
            });
        });
    }

    /**
     * Create sparkle effect
     */
    function createSparkle(element) {
        const sparkle = document.createElement('span');
        sparkle.innerHTML = '✨';
        sparkle.style.cssText = `
            position: absolute;
            font-size: 20px;
            pointer-events: none;
            animation: sparkleFloat 1s ease-out forwards;
            z-index: 1000;
        `;
        
        const rect = element.getBoundingClientRect();
        sparkle.style.left = rect.right + 'px';
        sparkle.style.top = rect.top + 'px';
        
        document.body.appendChild(sparkle);
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes sparkleFloat {
                0% {
                    opacity: 1;
                    transform: translateY(0) scale(0.5);
                }
                100% {
                    opacity: 0;
                    transform: translateY(-30px) scale(1.5);
                }
            }
        `;
        if (!document.querySelector('#sparkle-animation-style')) {
            style.id = 'sparkle-animation-style';
            document.head.appendChild(style);
        }
        
        setTimeout(() => sparkle.remove(), 1000);
    }

    /**
     * Add checkmark to valid inputs
     */
    function addCheckmark(input) {
        removeCheckmark(input);
        
        const checkmark = document.createElement('span');
        checkmark.className = 'input-checkmark';
        checkmark.innerHTML = '✓';
        checkmark.style.cssText = `
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #44AF69;
            font-size: 20px;
            font-weight: bold;
            pointer-events: none;
        `;
        
        if (input.parentElement.style.position !== 'relative') {
            input.parentElement.style.position = 'relative';
        }
        
        input.parentElement.appendChild(checkmark);
    }

    /**
     * Remove checkmark
     */
    function removeCheckmark(input) {
        const checkmark = input.parentElement.querySelector('.input-checkmark');
        if (checkmark) {
            checkmark.remove();
        }
    }

    /**
     * Search Enhancements
     */
    function initSearchEnhancements() {
        const searchInput = document.querySelector('#searchbar');
        
        if (searchInput) {
            // Add search icon
            const icon = document.createElement('span');
            icon.innerHTML = '🔍';
            icon.style.cssText = `
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 18px;
                pointer-events: none;
            `;
            
            const wrapper = searchInput.parentElement;
            if (wrapper) {
                wrapper.style.position = 'relative';
                wrapper.insertBefore(icon, searchInput);
                searchInput.style.paddingLeft = '40px';
            }

            // Animate on type
            searchInput.addEventListener('input', function() {
                this.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 200);
            });
        }
    }

    /**
     * Tooltips
     */
    function initTooltips() {
        const buttons = document.querySelectorAll('.button, input[type="submit"]');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function(e) {
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = this.title || this.value || 'Click para continuar';
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(44, 62, 80, 0.95);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 14px;
                    pointer-events: none;
                    z-index: 10000;
                    white-space: nowrap;
                    animation: tooltipFade 0.3s ease-in;
                `;
                
                document.body.appendChild(tooltip);
                
                // Position tooltip
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
                
                // Store tooltip reference
                this._tooltip = tooltip;
            });
            
            button.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
            });
        });

        // Add tooltip animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes tooltipFade {
                from {
                    opacity: 0;
                    transform: translateY(-5px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        if (!document.querySelector('#tooltip-animation-style')) {
            style.id = 'tooltip-animation-style';
            document.head.appendChild(style);
        }
    }

    /**
     * Confetti on Success
     */
    function initConfetti() {
        const successMessages = document.querySelectorAll('.success');
        
        successMessages.forEach(message => {
            if (message.textContent.includes('exitoso') || 
                message.textContent.includes('guardó') ||
                message.textContent.includes('añadió')) {
                launchConfetti();
            }
        });
    }

    /**
     * Launch confetti effect
     */
    function launchConfetti() {
        const colors = ['#FF6B35', '#4ECDC4', '#44AF69', '#9B59B6', '#FF6B9D'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.cssText = `
                position: fixed;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                top: -10px;
                left: ${Math.random() * 100}%;
                opacity: 1;
                transform: rotate(${Math.random() * 360}deg);
                pointer-events: none;
                z-index: 10000;
                animation: confettiFall ${2 + Math.random() * 2}s ease-out forwards;
                animation-delay: ${Math.random() * 0.5}s;
            `;
            
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 4000);
        }

        // Add confetti animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes confettiFall {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 1;
                }
                100% {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
        `;
        if (!document.querySelector('#confetti-animation-style')) {
            style.id = 'confetti-animation-style';
            document.head.appendChild(style);
        }
    }

    /**
     * Button Click Effects
     */
    document.addEventListener('click', function(e) {
        if (e.target.matches('.button, input[type="submit"], button')) {
            createRipple(e);
        }
    });

    /**
     * Create ripple effect
     */
    function createRipple(e) {
        const button = e.target;
        const ripple = document.createElement('span');
        
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
            animation: rippleEffect 0.6s ease-out;
        `;
        
        if (button.style.position !== 'absolute' && button.style.position !== 'relative') {
            button.style.position = 'relative';
        }
        button.style.overflow = 'hidden';
        
        button.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);

        // Add ripple animation if not exists
        const style = document.createElement('style');
        style.textContent = `
            @keyframes rippleEffect {
                0% {
                    transform: scale(0);
                    opacity: 1;
                }
                100% {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        if (!document.querySelector('#ripple-animation-style')) {
            style.id = 'ripple-animation-style';
            document.head.appendChild(style);
        }
    }

    /**
     * Add emojis to navigation items
     */
    function addEmojiToNavigation() {
        const navItems = document.querySelectorAll('.model-description a');
        const emojiMap = {
            'usuario': '👥',
            'producto': '📦',
            'pedido': '🛒',
            'factura': '📄',
            'cotizacion': '💰',
            'categoria': '🏷️',
            'cliente': '👤',
            'inventario': '📊'
        };

        navItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            for (const [key, emoji] of Object.entries(emojiMap)) {
                if (text.includes(key)) {
                    item.textContent = `${emoji} ${item.textContent}`;
                    break;
                }
            }
        });
    }

    // Call emoji function
    setTimeout(addEmojiToNavigation, 500);

})();
