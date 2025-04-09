

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Инициализация выпадающих списков
    const dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
    dropdownTriggerList.map(function (dropdownTriggerEl) {
        return new bootstrap.Dropdown(dropdownTriggerEl);
    });

    // Обработка переключения сайдбара
    const sidebarToggleBtn = document.getElementById('sidebarCollapse');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('active');
        });
    }

    // Настройка активных ссылок в меню
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href)) {
            link.classList.add('active');
        }
    });

    // Обработка подтверждения удаления
    const confirmDeleteBtns = document.querySelectorAll('.confirm-delete');
    confirmDeleteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    });

    // Инициализация графиков, если они есть
    initCharts();
});

/**
 * Форматирование даты и времени
 * @param {string|Date} dateString - Строка или объект даты
 * @param {boolean} includeTime - Включать ли время
 * @returns {string} Отформатированная дата
 */
function formatDate(dateString, includeTime = false) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleString('ru-RU', options);
}

/**
 * Форматирование валюты
 * @param {number} amount - Сумма
 * @returns {string} Отформатированная сумма
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    }).format(amount);
}

/**
 * Инициализация графиков
 */
function initCharts() {
    // График доходов
    const revenueChartEl = document.getElementById('revenueChart');
    if (revenueChartEl) {
        const ctx = revenueChartEl.getContext('2d');
        const revenueData = JSON.parse(revenueChartEl.dataset.values || '[]');
        const revenueLabels = JSON.parse(revenueChartEl.dataset.labels || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: revenueLabels,
                datasets: [{
                    label: 'Доход',
                    data: revenueData,
                    backgroundColor: 'rgba(63, 81, 181, 0.1)',
                    borderColor: 'rgba(63, 81, 181, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.raw);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }
    
    // График бронирований
    const bookingsChartEl = document.getElementById('bookingsChart');
    if (bookingsChartEl) {
        const ctx = bookingsChartEl.getContext('2d');
        const bookingsData = JSON.parse(bookingsChartEl.dataset.values || '[]');
        const bookingsLabels = JSON.parse(bookingsChartEl.dataset.labels || '[]');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: bookingsLabels,
                datasets: [{
                    label: 'Количество бронирований',
                    data: bookingsData,
                    backgroundColor: 'rgba(76, 175, 80, 0.8)',
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    }
    
    // График популярности услуг
    const servicesChartEl = document.getElementById('servicesChart');
    if (servicesChartEl) {
        const ctx = servicesChartEl.getContext('2d');
        const servicesData = JSON.parse(servicesChartEl.dataset.values || '[]');
        const servicesLabels = JSON.parse(servicesChartEl.dataset.labels || '[]');
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: servicesLabels,
                datasets: [{
                    data: servicesData,
                    backgroundColor: [
                        'rgba(63, 81, 181, 0.8)',
                        'rgba(245, 0, 87, 0.8)',
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(156, 39, 176, 0.8)',
                        'rgba(0, 150, 136, 0.8)',
                        'rgba(255, 87, 34, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }
}

/**
 * Обработка загрузки изображений
 * @param {HTMLInputElement} input - Элемент ввода файла
 * @param {HTMLImageElement} preview - Элемент предпросмотра
 */
function handleImageUpload(input, preview) {
    input.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                preview.src = e.target.result;
            };
            
            reader.readAsDataURL(this.files[0]);
        }
    });
}

/**
 * Динамическое добавление полей
 * @param {string} containerId - ID контейнера
 * @param {string} templateId - ID шаблона
 */
function addDynamicField(containerId, templateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);
    
    if (container && template) {
        const clone = template.content.cloneNode(true);
        const index = container.children.length;
        
        // Обновляем индексы в полях клона
        const inputs = clone.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const name = input.getAttribute('name');
            if (name) {
                input.setAttribute('name', name.replace('INDEX', index));
            }
            
            const id = input.getAttribute('id');
            if (id) {
                input.setAttribute('id', id.replace('INDEX', index));
            }
        });
        
        const labels = clone.querySelectorAll('label');
        labels.forEach(label => {
            const forAttr = label.getAttribute('for');
            if (forAttr) {
                label.setAttribute('for', forAttr.replace('INDEX', index));
            }
        });
        
        // Добавляем кнопку удаления
        const removeBtn = clone.querySelector('.remove-field');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                this.closest('.dynamic-field').remove();
            });
        }
        
        container.appendChild(clone);
    }
}

/**
 * Отправка API запроса
 * @param {string} url - URL запроса
 * @param {string} method - Метод запроса (GET, POST, PUT, DELETE)
 * @param {Object} data - Данные для отправки
 * @returns {Promise} Промис с результатом
 */
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Accept': 'application/json'
        }
    };
    
    // Получаем токен из localStorage и добавляем его в заголовки, если он существует
    localStorage.setItem('token', 'ffff');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        if (data instanceof FormData) {
            options.body = data;
        } else {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        }
    }
    
    const response = await fetch(url, options);
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Произошла ошибка при выполнении запроса');
    }
    
    return response.json();
}

/**
 * Отображение уведомления
 * @param {string} message - Текст сообщения
 * @param {string} type - Тип уведомления (success, danger, warning, info)
 * @param {number} duration - Продолжительность отображения в мс
 */
function showNotification(message, type = 'success', duration = 3000) {
    const alertContainer = document.getElementById('alertContainer') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Закрыть"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Автоматическое скрытие
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, duration);
}

/**
 * Создание контейнера для уведомлений
 * @returns {HTMLElement} Контейнер для уведомлений
 */
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
} 