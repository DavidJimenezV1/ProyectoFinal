/* ================================
   TEJOS OLÍMPICA - ADMIN CUSTOM JAVASCRIPT
   Funciones interactivas para el admin
   ================================ */

(function() {
    'use strict';

    // ================================
    // INICIALIZACIÓN
    // ================================
    
    document.addEventListener('DOMContentLoaded', function() {
        initAnimations();
        initCounters();
        initTooltips();
        initSmoothScroll();
        initTableHovers();
        initNotifications();
        initSidebarCollapse();
    });

    // ================================
    // ANIMACIONES DE ENTRADA
    // ================================
    
    function initAnimations() {
        // Animar elementos cuando entran en el viewport
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observar módulos y tarjetas
        document.querySelectorAll('.module, .dashboard-card').forEach(function(el) {
            observer.observe(el);
        });
    }

    // ================================
    // CONTADORES ANIMADOS
    // ================================
    
    function initCounters() {
        const counters = document.querySelectorAll('.dashboard-card-value');
        
        counters.forEach(function(counter) {
            const target = parseInt(counter.textContent.replace(/[^0-9]/g, '')) || 0;
            
            if (target === 0) return;
            
            let current = 0;
            const increment = target / 50; // 50 pasos
            const duration = 1500; // 1.5 segundos
            const stepTime = duration / 50;
            
            counter.textContent = '0';
            
            const timer = setInterval(function() {
                current += increment;
                
                if (current >= target) {
                    counter.textContent = formatNumber(target);
                    clearInterval(timer);
                } else {
                    counter.textContent = formatNumber(Math.floor(current));
                }
            }, stepTime);
        });
    }

    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }

    // ================================
    // TOOLTIPS
    // ================================
    
    function initTooltips() {
        // Crear tooltips simples para elementos con título
        const elements = document.querySelectorAll('[title]');
        
        elements.forEach(function(el) {
            el.addEventListener('mouseenter', function(e) {
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = this.title;
                tooltip.style.cssText = `
                    position: absolute;
                    background: rgba(0, 0, 0, 0.9);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    font-size: 0.85rem;
                    z-index: 10000;
                    pointer-events: none;
                    white-space: nowrap;
                `;
                
                document.body.appendChild(tooltip);
                
                // Posicionar tooltip
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
                
                // Guardar referencia
                this._tooltip = tooltip;
                
                // Remover el título original
                this._originalTitle = this.title;
                this.title = '';
            });
            
            el.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
                if (this._originalTitle) {
                    this.title = this._originalTitle;
                }
            });
        });
    }

    // ================================
    // SMOOTH SCROLL
    // ================================
    
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '#!') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // ================================
    // TABLE HOVERS MEJORADOS
    // ================================
    
    function initTableHovers() {
        const rows = document.querySelectorAll('#result_list tbody tr');
        
        rows.forEach(function(row) {
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.01)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        });
    }

    // ================================
    // NOTIFICACIONES TOAST
    // ================================
    
    function initNotifications() {
        // Animar mensajes existentes
        const messages = document.querySelectorAll('.messagelist li');
        
        messages.forEach(function(msg, index) {
            setTimeout(function() {
                msg.classList.add('notification-enter');
            }, index * 100);
            
            // Auto-cerrar después de 5 segundos
            setTimeout(function() {
                msg.classList.add('notification-exit');
                setTimeout(function() {
                    msg.remove();
                }, 500);
            }, 5000 + (index * 100));
        });
    }

    // Función para mostrar notificaciones programáticamente
    window.showNotification = function(message, type) {
        type = type || 'info';
        
        const container = document.querySelector('.messagelist') || createMessageContainer();
        
        const notification = document.createElement('li');
        notification.className = type + ' notification-enter';
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // Auto-cerrar
        setTimeout(function() {
            notification.classList.add('notification-exit');
            setTimeout(function() {
                notification.remove();
            }, 500);
        }, 5000);
    };

    function createMessageContainer() {
        const container = document.createElement('ul');
        container.className = 'messagelist';
        
        const content = document.getElementById('content');
        if (content) {
            content.insertBefore(container, content.firstChild);
        } else {
            document.body.appendChild(container);
        }
        
        return container;
    }

    // ================================
    // SIDEBAR COLAPSABLE
    // ================================
    
    function initSidebarCollapse() {
        // Si existe un sidebar, agregar funcionalidad de colapso
        const sidebar = document.querySelector('#changelist-filter, .nav-sidebar');
        
        if (!sidebar) return;
        
        // Crear botón de toggle
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'sidebar-toggle';
        toggleBtn.innerHTML = '☰';
        toggleBtn.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #FF6B35 0%, #E63946 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            z-index: 1000;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            display: none;
        `;
        
        // Mostrar solo en móvil
        if (window.innerWidth <= 768) {
            toggleBtn.style.display = 'block';
        }
        
        document.body.appendChild(toggleBtn);
        
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            if (sidebar.classList.contains('collapsed')) {
                sidebar.style.display = 'none';
                this.innerHTML = '☰';
            } else {
                sidebar.style.display = 'block';
                this.innerHTML = '✕';
            }
        });
        
        // Actualizar al cambiar tamaño de ventana
        window.addEventListener('resize', function() {
            if (window.innerWidth <= 768) {
                toggleBtn.style.display = 'block';
            } else {
                toggleBtn.style.display = 'none';
                sidebar.style.display = '';
                sidebar.classList.remove('collapsed');
            }
        });
    }

    // ================================
    // LOADING OVERLAY
    // ================================
    
    window.showLoading = function() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
        return overlay;
    };

    window.hideLoading = function(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.remove();
        }
    };

    // ================================
    // CONFIRMACIÓN DE ELIMINACIÓN
    // ================================
    
    document.addEventListener('click', function(e) {
        const deleteLink = e.target.closest('.deletelink, .deletelink-box a');
        
        if (deleteLink) {
            const confirmed = confirm('¿Está seguro de que desea eliminar este elemento?');
            if (!confirmed) {
                e.preventDefault();
                return false;
            }
        }
    });

    // ================================
    // BÚSQUEDA EN TIEMPO REAL (opcional)
    // ================================
    
    const searchInput = document.querySelector('#searchbar input[type="text"]');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(function() {
                // Aquí se podría implementar búsqueda AJAX
                console.log('Buscando:', searchInput.value);
            }, 500);
        });
    }

    // ================================
    // TECLADO SHORTCUTS
    // ================================
    
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K para focus en búsqueda
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#searchbar input[type="text"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape para cerrar modales o notificaciones
        if (e.key === 'Escape') {
            const notifications = document.querySelectorAll('.messagelist li');
            notifications.forEach(function(notif) {
                notif.classList.add('notification-exit');
                setTimeout(function() {
                    notif.remove();
                }, 500);
            });
        }
    });

    // ================================
    // ANALYTICS (opcional)
    // ================================
    
    window.trackEvent = function(category, action, label) {
        console.log('Event tracked:', category, action, label);
        // Aquí se podría integrar con Google Analytics o similar
    };

    // ================================
    // HELPERS
    // ================================
    
    window.AdminHelpers = {
        formatCurrency: function(value) {
            return new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 0
            }).format(value);
        },
        
        formatDate: function(date) {
            return new Intl.DateTimeFormat('es-CO', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }).format(new Date(date));
        },
        
        formatNumber: formatNumber
    };

})();
