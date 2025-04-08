/**
 * Ситуационный центр - JavaScript для динамической загрузки контента
 */

// Глобальные переменные
let companyData = [];
let currentSection = 'dashboard';
let selectedCompanyId = null;

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация данных
    initializeData();
    
    // Настройка обработчиков событий
    setupEventHandlers();
    
    // Загрузка начального экрана
    loadSection('dashboard');
    
    // Добавляем первое событие
    addEvent('info', 'Система инициализирована');
    
    // Настройка кнопки очистки событий
    document.getElementById('clear-events').addEventListener('click', function() {
        document.getElementById('events-list').innerHTML = '';
        addEvent('info', 'Журнал событий очищен');
    });
    
    // Подгоняем размеры панелей к размеру окна
    adjustPanelSizes();
    
    // Добавляем обработчик изменения размера окна
    window.addEventListener('resize', function() {
        adjustPanelSizes();
    });
});

/**
 * Инициализация данных компаний из JSON
 */
function initializeData() {
    try {
        const companyDataJson = document.getElementById('company-data-json')?.textContent;
        if (companyDataJson) {
            companyData = JSON.parse(companyDataJson);
            
            // Обновляем счетчики уведомлений
            updateNotificationCounters();
        } else {
            // Если данных нет, инициализируем пустым массивом
            companyData = [];
            console.log('Данные компаний не найдены, инициализирован пустой массив');
            addEvent('warning', 'Данные компаний не найдены');
        }
    } catch (e) {
        console.error('Ошибка при парсинге данных компаний:', e);
        companyData = [];
        addEvent('danger', 'Ошибка загрузки данных компаний');
    }
}

/**
 * Обновление счетчиков уведомлений
 */
function updateNotificationCounters() {
    // Счетчик новых бронирований
    const newBookingsCount = 2; // Будет заменено на реальные данные с API
    const newBookingsCounter = document.getElementById('new-bookings-count');
    if (newBookingsCounter) {
        newBookingsCounter.textContent = newBookingsCount;
        if (newBookingsCount === 0) {
            newBookingsCounter.style.display = 'none';
        } else {
            newBookingsCounter.style.display = 'inline-block';
        }
    }
    
    // Счетчик заявок на модерацию
    const moderationCount = companyData.filter(c => c.moderation_status === 'pending').length || 0;
    const moderationCounter = document.getElementById('moderation-count');
    if (moderationCounter) {
        moderationCounter.textContent = moderationCount;
        if (moderationCount === 0) {
            moderationCounter.style.display = 'none';
        } else {
            moderationCounter.style.display = 'inline-block';
        }
    }
}

/**
 * Настройка обработчиков событий
 */
function setupEventHandlers() {
    // Обработчик переключения секций (навигация)
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            const title = this.getAttribute('data-title');
            
            loadSection(section, title);
            
            // Выделяем активный пункт
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Обработчик кнопки обновления
    document.querySelector('.refresh-data')?.addEventListener('click', function() {
        refreshData();
    });
    
    // Обработчик кнопки очистки событий
    document.getElementById('clear-events')?.addEventListener('click', function() {
        document.getElementById('events-list').innerHTML = '';
        addEvent('info', 'Журнал событий очищен');
    });
    
    // Делегирование событий для всех динамически создаваемых элементов
    document.addEventListener('click', function(e) {
        // Обработка создания компании
        if (e.target.classList.contains('create-company-btn') || e.target.closest('.create-company-btn')) {
            loadCompanyForm();
            return;
        }
        
        // Обработка отправки формы компании
        if (e.target.id === 'save-company-btn') {
            handleCompanySubmit();
            return;
        }
        
        // Кнопка возврата в список компаний
        if (e.target.classList.contains('back-to-companies') || e.target.closest('.back-to-companies')) {
            loadSection('companies');
            return;
        }
    });
}

/**
 * Загрузка раздела
 * @param {string} section - Идентификатор раздела
 * @param {string} title - Заголовок раздела (опционально)
 */
function loadSection(section, title = null) {
    currentSection = section;
    
    // Обновляем заголовок в панели
    if (title) {
        document.getElementById('main-panel-title').textContent = title;
    }
    
    // Обновляем индикатор текущего раздела
    const currentSectionIndicator = document.getElementById('current-section-indicator');
    if (currentSectionIndicator) {
        currentSectionIndicator.textContent = 
            title || document.querySelector(`.nav-item[data-section="${section}"]`)?.getAttribute('data-title') || 'Обзор';
    }
    
    // Показываем индикатор загрузки
    const mainPanel = document.getElementById('main-panel-content');
    if (!mainPanel) {
        console.error('Элемент main-panel-content не найден');
        return;
    }
    
    mainPanel.innerHTML = `
        <div id="loading-placeholder" class="loading-placeholder">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
            <p>Загрузка данных...</p>
        </div>
    `;
    
    // Устанавливаем таймаут для защиты от бесконечной загрузки
    const loadingTimeout = setTimeout(() => {
        const loadingPlaceholder = document.getElementById('loading-placeholder');
        if (loadingPlaceholder) {
            mainPanel.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Превышено время ожидания загрузки. Пожалуйста, <a href="javascript:void(0)" onclick="refreshData()">обновите страницу</a>.
                </div>
            `;
            addEvent('danger', 'Превышено время загрузки раздела ' + section);
        }
    }, 10000); // 10 секунд таймаут
    
    // Загружаем соответствующее содержимое в основную панель
    try {
        switch (section) {
            case 'dashboard':
                loadDashboard();
                break;
                
            case 'companies':
                loadCompanies();
                break;
                
            case 'services':
                loadServices();
                break;
                
            case 'schedule':
                loadSchedule();
                break;
                
            case 'bookings':
                loadBookings();
                break;
                
            case 'new-bookings':
                loadNewBookings();
                break;
                
            case 'analytics':
                loadAnalytics();
                break;
                
            case 'reports':
                loadReports();
                break;
                
            case 'moderation':
                loadModeration();
                break;
                
            case 'telegram':
                loadTelegramSettings();
                break;
                
            case 'profile':
                loadUserProfile();
                break;
                
            default:
                clearTimeout(loadingTimeout);
                mainPanel.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Раздел "${section}" находится в разработке
                    </div>
                `;
        }
    } catch (error) {
        clearTimeout(loadingTimeout);
        console.error(`Ошибка при загрузке раздела ${section}:`, error);
        mainPanel.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Произошла ошибка при загрузке раздела: ${error.message || 'Неизвестная ошибка'}
            </div>
            <button class="btn btn-primary mt-3" onclick="refreshData()">
                <i class="fas fa-sync-alt me-2"></i>Попробовать снова
            </button>
        `;
        addEvent('danger', `Ошибка загрузки раздела ${section}: ${error.message || 'Неизвестная ошибка'}`);
    }
    
    // Обновляем нижнюю панель в соответствии с разделом
    try {
        loadBottomPanel(section);
    } catch (error) {
        console.error(`Ошибка при загрузке нижней панели для раздела ${section}:`, error);
        addEvent('warning', `Ошибка загрузки панели информации: ${error.message || 'Неизвестная ошибка'}`);
    }
    
    // Очищаем таймаут после успешной загрузки
    clearTimeout(loadingTimeout);
    
    // Добавляем событие в журнал
    addEvent('info', `Загружен раздел: ${title || section}`);
}

/**
 * Загрузка нижней панели в зависимости от раздела
 * @param {string} section - Идентификатор раздела
 */
function loadBottomPanel(section) {
    const bottomPanelContent = document.getElementById('bottom-panel-content');
    const bottomPanelTitle = document.getElementById('bottom-panel-title');
    
    if (!bottomPanelContent || !bottomPanelTitle) {
        console.error('Элементы нижней панели не найдены');
        return;
    }
    
    // Устанавливаем заголовок и содержимое в зависимости от раздела
    switch (section) {
        case 'dashboard':
            bottomPanelTitle.textContent = 'Динамика бронирований';
            const statsTemplate = document.getElementById('bottom-panel-stats-template');
            if (statsTemplate) {
                bottomPanelContent.innerHTML = statsTemplate.innerHTML;
                initBottomPanelStats();
            }
            break;
            
        case 'companies':
            bottomPanelTitle.textContent = 'Статистика компаний';
            const companyStatsTemplate = document.getElementById('bottom-panel-stats-template');
            if (companyStatsTemplate) {
                bottomPanelContent.innerHTML = companyStatsTemplate.innerHTML;
                initCompaniesStats();
            }
            break;
            
        case 'bookings':
        case 'new-bookings':
        case 'schedule':
            bottomPanelTitle.textContent = 'Ближайшие бронирования';
            const calendarTemplate = document.getElementById('bottom-panel-calendar-template');
            if (calendarTemplate) {
                bottomPanelContent.innerHTML = calendarTemplate.innerHTML;
                initMiniCalendar();
            }
            break;
            
        default:
            // Для остальных разделов показываем общую статистику
            bottomPanelTitle.textContent = 'Общая статистика';
            const defaultTemplate = document.getElementById('bottom-panel-stats-template');
            if (defaultTemplate) {
                bottomPanelContent.innerHTML = defaultTemplate.innerHTML;
                initBottomPanelStats();
            }
    }
    
    // Настраиваем обработчик кнопки обновления
    const refreshButton = bottomPanelContent.parentElement.querySelector('.refresh-bottom-panel');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            loadBottomPanel(section);
        });
    }
}

/**
 * Инициализация графиков и статистики для нижней панели
 */
function initBottomPanelStats() {
    // Инициализация графика динамики бронирований
    const bookingsTrendCanvas = document.getElementById('bookings-trend-chart');
    if (bookingsTrendCanvas) {
        initBookingsTrendChart(bookingsTrendCanvas);
    }
    
    // Инициализация графика распределения услуг
    const servicesDistCanvas = document.getElementById('services-distribution-chart');
    if (servicesDistCanvas) {
        initServicesDistributionChart(servicesDistCanvas);
    }
}

/**
 * Инициализация графика тренда бронирований
 * @param {HTMLCanvasElement} canvas - Элемент canvas для графика
 */
function initBookingsTrendChart(canvas) {
    // Генерируем тестовые данные для графика
    const labels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    const data = {
        labels: labels,
        datasets: [{
            label: 'Бронирования',
            data: [15, 21, 18, 24, 23, 12, 8],
            borderColor: '#4e73df',
            backgroundColor: 'rgba(78, 115, 223, 0.2)',
            tension: 0.3,
            fill: true
        }]
    };
    
    // Настройки графика
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                mode: 'index',
                intersect: false
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
    };
    
    // Создаем график
    if (window.bookingsTrendChart) {
        window.bookingsTrendChart.destroy();
    }
    
    window.bookingsTrendChart = new Chart(canvas, {
        type: 'line',
        data: data,
        options: options
    });
}

/**
 * Инициализация графика распределения услуг
 * @param {HTMLCanvasElement} canvas - Элемент canvas для графика
 */
function initServicesDistributionChart(canvas) {
    // Генерируем тестовые данные для графика
    const data = {
        labels: ['Стрижка', 'Маникюр', 'Массаж', 'Консультация', 'Другое'],
        datasets: [{
            data: [30, 25, 20, 15, 10],
            backgroundColor: [
                '#4e73df',
                '#1cc88a',
                '#36b9cc',
                '#f6c23e',
                '#e74a3b'
            ],
            borderWidth: 1
        }]
    };
    
    // Настройки графика
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    boxWidth: 12,
                    padding: 10
                }
            }
        }
    };
    
    // Создаем график
    if (window.servicesDistributionChart) {
        window.servicesDistributionChart.destroy();
    }
    
    window.servicesDistributionChart = new Chart(canvas, {
        type: 'pie',
        data: data,
        options: options
    });
}

/**
 * Инициализация статистики для компаний
 */
function initCompaniesStats() {
    // Этот метод вызывается для раздела компаний
    // В этом случае мы инициализируем разные графики
    
    // Инициализация графика динамики бронирований
    const bookingsTrendCanvas = document.getElementById('bookings-trend-chart');
    if (bookingsTrendCanvas) {
        // Другие данные для раздела компаний
        initBookingsTrendChart(bookingsTrendCanvas);
    }
    
    // Инициализация графика распределения услуг
    const servicesDistCanvas = document.getElementById('services-distribution-chart');
    if (servicesDistCanvas) {
        // Для раздела компаний показываем распределение компаний по категориям
        const data = {
            labels: ['Рестораны', 'Салоны красоты', 'Медицина', 'Спорт', 'Авто'],
            datasets: [{
                data: [35, 25, 15, 15, 10],
                backgroundColor: [
                    '#4e73df',
                    '#1cc88a',
                    '#36b9cc',
                    '#f6c23e',
                    '#e74a3b'
                ],
                borderWidth: 1
            }]
        };
        
        const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10
                    }
                },
                title: {
                    display: true,
                    text: 'Распределение компаний по категориям'
                }
            }
        };
        
        if (window.servicesDistributionChart) {
            window.servicesDistributionChart.destroy();
        }
        
        window.servicesDistributionChart = new Chart(servicesDistCanvas, {
            type: 'pie',
            data: data,
            options: options
        });
    }
}

/**
 * Инициализация мини-календаря бронирований
 */
function initMiniCalendar() {
    const calendarContainer = document.getElementById('mini-calendar');
    
    if (!calendarContainer) {
        console.error('Контейнер календаря не найден');
        return;
    }
    
    // Здесь был бы код для инициализации календаря
    // Вместо этого просто покажем список ближайших бронирований
    
    setTimeout(() => {
        calendarContainer.innerHTML = `
            <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">Стрижка</div>
                        <small>Иванов Иван</small>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-primary">Сегодня, 15:00</div>
                    </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">Маникюр</div>
                        <small>Петрова Анна</small>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-primary">Сегодня, 16:30</div>
                    </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">Массаж</div>
                        <small>Сидоров Петр</small>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-secondary">Завтра, 10:00</div>
                    </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">Консультация</div>
                        <small>Кузнецова Ольга</small>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-secondary">Завтра, 14:15</div>
                    </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">Стрижка + укладка</div>
                        <small>Морозова Елена</small>
                    </div>
                    <div class="text-end">
                        <div class="badge bg-secondary">Послезавтра, 11:30</div>
                    </div>
                </div>
            </div>
        `;
    }, 1000); // Имитация загрузки данных
}

/**
 * Инициализация графика услуг компании
 * @param {string} companyId - ID компании
 */
function initCompanyServicesChart(companyId) {
    const canvas = document.getElementById('company-services-chart');
    
    if (!canvas) {
        console.error('Canvas для графика услуг компании не найден');
        return;
    }
    
    // Генерируем тестовые данные для графика
    const data = {
        labels: ['Стрижка', 'Маникюр', 'Укладка', 'Окрашивание', 'Другое'],
        datasets: [{
            data: [45, 25, 15, 10, 5],
            backgroundColor: [
                '#4e73df',
                '#1cc88a',
                '#36b9cc',
                '#f6c23e',
                '#e74a3b'
            ],
            borderWidth: 1
        }]
    };
    
    // Настройки графика
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    boxWidth: 12,
                    padding: 8
                }
            }
        }
    };
    
    // Создаем график
    if (window.companyServicesChart) {
        window.companyServicesChart.destroy();
    }
    
    window.companyServicesChart = new Chart(canvas, {
        type: 'pie',
        data: data,
        options: options
    });
    
    // Обновляем текстовую статистику компании
    document.getElementById('company-total-bookings').textContent = '128';
    document.getElementById('company-avg-booking-time').textContent = '45 мин';
    document.getElementById('company-occupancy-rate').textContent = '67%';
    document.getElementById('company-active-services').textContent = '12';
}

/**
 * Загрузка содержимого панели управления
 */
function loadDashboard() {
    const mainPanel = document.getElementById('main-panel-content');
    if (!mainPanel) {
        console.error('Элемент main-panel-content не найден');
        return;
    }
    
    try {
        // Загружаем шаблон дашборда
        const dashboardTemplate = document.getElementById('dashboard-template');
        if (dashboardTemplate) {
            mainPanel.innerHTML = dashboardTemplate.innerHTML;
        } else {
            throw new Error('Шаблон дашборда не найден');
        }
        
        // Получаем данные для дашборда
        fetchDashboardData();
        
        // Инициализируем график активности
        initActivityChart();
        
        // Загружаем недавние бронирования
        loadRecentBookings();
        
        // Загружаем недавние события в блок активности
        loadRecentEvents();
        
        // Загружаем нижнюю панель
        loadBottomPanel('dashboard');
        
    } catch (error) {
        console.error('Ошибка при загрузке дашборда:', error);
        mainPanel.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Ошибка загрузки дашборда: ${error.message}
            </div>
        `;
        addEvent('danger', 'Ошибка загрузки дашборда: ' + error.message);
    }
}

/**
 * Добавление события в журнал событий
 * @param {string} type - Тип события (info, success, warning, danger)
 * @param {string} message - Сообщение события
 */
function addEvent(type, message) {
    // Теперь добавляем события в блок активности на главной панели
    const eventsContainer = document.getElementById('latest-activity');
    
    if (!eventsContainer) {
        console.warn('Контейнер событий не найден, событие не будет записано');
        return;
    }
    
    // Если в контейнере загрузчик - удаляем его
    const loadingPlaceholder = eventsContainer.querySelector('.loading-placeholder');
    if (loadingPlaceholder) {
        loadingPlaceholder.remove();
    }
    
    // Создаем элемент события
    const eventItem = document.createElement('div');
    eventItem.className = `event-item ${type}`;
    
    // Добавляем содержимое события
    eventItem.innerHTML = `
        <div class="event-icon ${type}">
            <i class="${getEventIcon(type)}"></i>
        </div>
        <div class="event-content">
            <div class="event-message">${message}</div>
            <div class="event-time">${new Date().toLocaleTimeString('ru-RU')}</div>
        </div>
    `;
    
    // Вставляем событие в начало списка
    eventsContainer.prepend(eventItem);
    
    // Ограничиваем количество отображаемых событий
    const maxEvents = 5;
    const events = eventsContainer.querySelectorAll('.event-item');
    if (events.length > maxEvents) {
        for (let i = maxEvents; i < events.length; i++) {
            events[i].remove();
        }
    }
}

/**
 * Загрузка недавних событий
 */
function loadRecentEvents() {
    const eventsContainer = document.getElementById('latest-activity');
    
    if (!eventsContainer) {
        console.error('Контейнер событий не найден');
        return;
    }
    
    // Отображаем тестовые события
    eventsContainer.innerHTML = `
        <div class="event-item info">
            <div class="event-icon info">
                <i class="fas fa-info-circle"></i>
            </div>
            <div class="event-content">
                <div class="event-message">Система инициализирована</div>
                <div class="event-time">${new Date().toLocaleTimeString('ru-RU')}</div>
            </div>
        </div>
        <div class="event-item success">
            <div class="event-icon success">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="event-content">
                <div class="event-message">Бронирование #12345 подтверждено</div>
                <div class="event-time">${new Date().toLocaleTimeString('ru-RU')}</div>
            </div>
        </div>
        <div class="event-item warning">
            <div class="event-icon warning">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="event-content">
                <div class="event-message">Получено новое бронирование #12346</div>
                <div class="event-time">${new Date().toLocaleTimeString('ru-RU')}</div>
            </div>
        </div>
    `;
}

/**
 * Загрузка списка компаний
 */
function loadCompanies() {
    const mainPanel = document.getElementById('main-panel-content');
    const companiesTemplate = document.getElementById('companies-template');
    
    if (companiesTemplate) {
        mainPanel.innerHTML = companiesTemplate.innerHTML;
        
        // Загрузка списка компаний
        const companiesList = document.getElementById('companies-list');
        if (companiesList) {
            if (companyData && companyData.length > 0) {
                let companiesHtml = '';
                
                companyData.forEach(company => {
                    companiesHtml += `
                        <div class="company-card" data-id="${company.id}" data-status="${company.moderation_status}">
                            <div class="company-card-header">
                                <h5>${company.name}</h5>
                                ${getStatusBadgeHTML(company.moderation_status)}
                            </div>
                            <div class="company-card-body">
                                <p class="company-description">${truncateText(company.description, 100)}</p>
                                <div class="company-meta">
                                    <div><i class="fas fa-phone"></i> ${company.phone}</div>
                                    <div><i class="fas fa-envelope"></i> ${company.email}</div>
                                    <div><i class="fas fa-map-marker-alt"></i> ${company.location?.city || ''}</div>
                                </div>
                            </div>
                            <div class="company-card-footer">
                                <button class="btn btn-sm btn-outline-primary view-company" data-id="${company.id}">
                                    <i class="fas fa-eye"></i> Просмотр
                                </button>
                                <button class="btn btn-sm btn-outline-secondary edit-company" data-id="${company.id}">
                                    <i class="fas fa-edit"></i> Изменить
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                companiesList.innerHTML = companiesHtml;
                
                // Добавляем обработчики событий для карточек компаний
                addCompanyCardEventListeners();
            } else {
                companiesList.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        У вас пока нет компаний. Создайте первую компанию, нажав кнопку "Создать компанию"
                    </div>
                `;
            }
        }
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Ошибка загрузки шаблона списка компаний
            </div>
        `;
    }
}

/**
 * Загрузка формы создания/редактирования компании
 * @param {object} company - Объект компании для редактирования (null для создания)
 */
function loadCompanyForm(company = null) {
    const mainPanel = document.getElementById('main-panel-content');
    const formTemplate = document.getElementById('company-form-template');
    
    if (formTemplate) {
        mainPanel.innerHTML = formTemplate.innerHTML;
        
        // Обновляем заголовок
        document.getElementById('main-panel-title').textContent = company ? 'Редактирование компании' : 'Создание компании';
        
        // Заполняем форму данными компании, если это редактирование
        if (company) {
            document.getElementById('company-form-title').textContent = 'Редактирование компании';
            
            // Заполняем поля формы
            document.getElementById('company-id').value = company.id;
            document.getElementById('company-name').value = company.name;
            document.getElementById('company-description').value = company.description;
            document.getElementById('company-phone').value = company.phone;
            document.getElementById('company-email').value = company.email;
            document.getElementById('company-website').value = company.website || '';
            
            if (company.category_id) {
                document.getElementById('company-category').value = company.category_id;
            }
            
            if (company.location) {
                document.getElementById('company-address').value = company.location.address || '';
                document.getElementById('company-city').value = company.location.city || '';
                document.getElementById('company-region').value = company.location.region || '';
                document.getElementById('company-postal-code').value = company.location.zipcode || '';
            }
            
            // Изменяем текст кнопки
            document.getElementById('save-company-btn').textContent = 'Сохранить изменения';
        }
        
        // Добавляем обработчик отправки формы
        const form = document.getElementById('company-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                handleCompanySubmit();
            });
        }
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Ошибка загрузки шаблона формы компании
            </div>
        `;
    }
}

/**
 * Обработка отправки формы компании
 */
function handleCompanySubmit() {
    const form = document.getElementById('company-form');
    
    // Базовая валидация
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        addEvent('warning', 'Пожалуйста, заполните все обязательные поля');
        return;
    }
    
    const companyId = document.getElementById('company-id')?.value;
    const isEditing = companyId && companyId !== '';
    
    // Сбор данных из формы
    const companyData = {
        id: isEditing ? parseInt(companyId) : Date.now(),
        name: document.getElementById('company-name').value,
        description: document.getElementById('company-description').value,
        phone: document.getElementById('company-phone').value,
        email: document.getElementById('company-email').value,
        website: document.getElementById('company-website').value || null,
        category_id: parseInt(document.getElementById('company-category').value),
        moderation_status: isEditing ? 'approved' : 'pending',
        location: {
            address: document.getElementById('company-address').value,
            city: document.getElementById('company-city').value,
            region: document.getElementById('company-region').value || '',
            zipcode: document.getElementById('company-postal-code').value || ''
        }
    };
    
    // В реальном приложении здесь был бы AJAX-запрос к API
    addEvent('info', 'Отправка данных компании...');
    
    // Имитация задержки сети для демонстрации
    setTimeout(() => {
        if (isEditing) {
            // Обновляем существующую компанию
            const index = companyData.findIndex(c => c.id === parseInt(companyId));
            if (index !== -1) {
                companyData[index] = companyData;
                addEvent('success', 'Компания успешно обновлена');
            } else {
                addEvent('danger', 'Ошибка при обновлении: компания не найдена');
            }
        } else {
            // Добавляем новую компанию
            companyData.push(companyData);
            addEvent('success', 'Компания успешно создана и отправлена на модерацию');
        }
        
        // Возвращаемся к списку компаний
        loadSection('companies');
    }, 1000);
}

/**
 * Загрузка данных для панели управления
 */
function fetchDashboardData() {
    // В реальном приложении здесь был бы AJAX-запрос к API
    
    // Заполняем статистические карточки
    const totalCompanies = document.getElementById('total-companies');
    const activeCompanies = document.getElementById('active-companies');
    const pendingCompanies = document.getElementById('pending-companies');
    
    if (totalCompanies) totalCompanies.textContent = companyData.length;
    if (activeCompanies) activeCompanies.textContent = companyData.filter(c => c.moderation_status === 'approved').length;
    if (pendingCompanies) pendingCompanies.textContent = companyData.filter(c => c.moderation_status === 'pending').length;
    
    // Загружаем данные для карточек последних событий
    const latestActivity = document.getElementById('latest-activity');
    if (latestActivity) {
        latestActivity.innerHTML = `
            <div class="activity-item">
                <div class="activity-icon bg-primary">
                    <i class="fas fa-users"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">Новая компания</div>
                    <div class="activity-subtitle">Создана новая компания</div>
                    <div class="activity-time">2 часа назад</div>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-icon bg-success">
                    <i class="fas fa-calendar-check"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">Новое бронирование</div>
                    <div class="activity-subtitle">Клиент выполнил бронирование услуги</div>
                    <div class="activity-time">4 часа назад</div>
                </div>
            </div>
        `;
    }
}

/**
 * Загрузка последних бронирований
 */
function loadRecentBookings() {
    const recentBookings = document.getElementById('recent-bookings');
    if (!recentBookings) return;
    
    // В реальном приложении здесь был бы AJAX-запрос к API
    // Пример заполнения демо-данными
    recentBookings.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Клиент</th>
                        <th>Услуга</th>
                        <th>Дата</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Иван Петров</td>
                        <td>Стрижка</td>
                        <td>24.07.2023 15:00</td>
                        <td><span class="badge bg-success">Подтверждено</span></td>
                    </tr>
                    <tr>
                        <td>Анна Смирнова</td>
                        <td>Маникюр</td>
                        <td>24.07.2023 16:30</td>
                        <td><span class="badge bg-warning">В ожидании</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

/**
 * Инициализация графика активности на панели управления
 */
function initActivityChart() {
    const activityChart = document.getElementById('activity-chart');
    if (!activityChart) {
        console.error('Элемент для графика активности не найден');
        return;
    }
    
    try {
        // Получаем контекст для рисования
        const ctx = activityChart.getContext('2d');
        if (!ctx) {
            console.error('Не удалось получить 2D контекст для графика');
            return;
        }
        
        // Генерируем метки для последних 7 дней
        const labels = [];
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
        }
        
        // Проверяем наличие Chart перед созданием
        if (typeof Chart === 'undefined') {
            throw new Error('Chart.js не найден или не загружен');
        }
        
        // Создаем график
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Бронирования',
                        data: [5, 8, 12, 7, 10, 15, 9],
                        borderColor: '#4e73df',
                        backgroundColor: 'rgba(78, 115, 223, 0.1)',
                        borderWidth: 2,
                        pointBackgroundColor: '#4e73df',
                        pointBorderColor: '#fff',
                        pointRadius: 4,
                        fill: true,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        bodyFont: {
                            size: 13
                        },
                        titleFont: {
                            size: 14
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Ошибка при инициализации графика активности:', error);
        throw error; // Перебрасываем ошибку для обработки на уровне выше
    }
}

/**
 * Добавление обработчиков событий для карточек компаний
 */
function addCompanyCardEventListeners() {
    // Обработчик кнопки просмотра
    document.querySelectorAll('.view-company').forEach(btn => {
        btn.addEventListener('click', function() {
            const companyId = parseInt(this.getAttribute('data-id'));
            viewCompanyDetails(companyId);
        });
    });
    
    // Обработчик кнопки редактирования
    document.querySelectorAll('.edit-company').forEach(btn => {
        btn.addEventListener('click', function() {
            const companyId = parseInt(this.getAttribute('data-id'));
            editCompany(companyId);
        });
    });
}

/**
 * Просмотр деталей компании
 * @param {number} companyId - ID компании
 */
function viewCompanyDetails(companyId) {
    // Находим компанию по ID
    const company = companyData.find(c => c.id === companyId);
    
    if (!company) {
        addEvent('danger', 'Компания не найдена');
        return;
    }
    
    // Загружаем шаблон деталей компании
    const mainPanel = document.getElementById('main-panel-content');
    const companyDetailsTemplate = document.getElementById('company-details-template');
    
    if (companyDetailsTemplate) {
        mainPanel.innerHTML = companyDetailsTemplate.innerHTML;
        
        // Заполняем данными
        document.getElementById('company-name-display').textContent = company.name;
        document.getElementById('company-status-badge').innerHTML = getStatusBadgeHTML(company.moderation_status);
        document.getElementById('company-description-display').textContent = company.description;
        
        // Контактная информация
        document.getElementById('company-phone-display').textContent = company.phone;
        document.getElementById('company-email-display').textContent = company.email;
        if (company.website) {
            document.getElementById('company-website-display').innerHTML = `
                <a href="${company.website}" target="_blank">${company.website}</a>
            `;
        } else {
            document.getElementById('company-website-row').style.display = 'none';
        }
        
        // Адрес
        if (company.location) {
            let addressText = company.location.address;
            if (company.location.city) addressText += `, ${company.location.city}`;
            if (company.location.region) addressText += `, ${company.location.region}`;
            if (company.location.zipcode) addressText += `, ${company.location.zipcode}`;
            
            document.getElementById('company-address-display').textContent = addressText;
        } else {
            document.getElementById('company-address-row').style.display = 'none';
        }
        
        // Настраиваем кнопку редактирования
        document.querySelector('.edit-company-btn')?.setAttribute('data-id', company.id);
        
        // Добавляем обработчики
        document.querySelector('.edit-company-btn')?.addEventListener('click', function() {
            editCompany(company.id);
        });
        
        // Загружаем информацию об услугах компании
        loadCompanyServices(company.id);
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Ошибка загрузки шаблона деталей компании
            </div>
        `;
    }
    
    // Обновляем заголовок
    document.getElementById('main-panel-title').textContent = 'Информация о компании';
    
    // Обновляем индикатор раздела
    document.getElementById('current-section-indicator').textContent = 'Просмотр компании';
    
    // Добавляем событие в журнал
    addEvent('info', `Загружены детали компании: ${company.name}`);
}

/**
 * Редактирование компании
 * @param {number} companyId - ID компании
 */
function editCompany(companyId) {
    // Находим компанию по ID
    const company = companyData.find(c => c.id === companyId);
    
    if (!company) {
        addEvent('danger', 'Компания не найдена');
        return;
    }
    
    // Загружаем форму редактирования
    loadCompanyForm(company);
    
    // Добавляем событие в журнал
    addEvent('info', `Редактирование компании: ${company.name}`);
}

/**
 * Загрузка услуг компании
 * @param {number} companyId - ID компании
 */
function loadCompanyServices(companyId) {
    const servicesContainer = document.getElementById('company-services');
    if (!servicesContainer) return;
    
    // В реальном приложении здесь был бы AJAX-запрос к API
    
    // Пример заполнения демо-данными
    servicesContainer.innerHTML = `
        <div class="alert alert-info">
            <i class="fas fa-info-circle me-2"></i>
            У компании пока нет услуг. Нажмите "Добавить услугу" для создания первой услуги.
        </div>
    `;
}

/**
 * Загрузка раздела "Услуги"
 */
function loadServices() {
    const mainPanel = document.getElementById('main-panel-content');
    const servicesTemplate = document.getElementById('services-template');
    
    if (servicesTemplate) {
        mainPanel.innerHTML = servicesTemplate.innerHTML;
        // Дополнительная инициализация...
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Услуги" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка раздела "Расписание"
 */
function loadSchedule() {
    const mainPanel = document.getElementById('main-panel-content');
    const scheduleTemplate = document.getElementById('schedule-template');
    
    if (scheduleTemplate) {
        mainPanel.innerHTML = scheduleTemplate.innerHTML;
        // Дополнительная инициализация...
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Расписание" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка раздела "Бронирования"
 */
function loadBookings() {
    const mainPanel = document.getElementById('main-panel-content');
    const bookingsTemplate = document.getElementById('bookings-template');
    
    if (bookingsTemplate) {
        mainPanel.innerHTML = bookingsTemplate.innerHTML;
        // Дополнительная инициализация...
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Бронирования" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка раздела "Новые бронирования"
 */
function loadNewBookings() {
    const mainPanel = document.getElementById('main-panel-content');
    const newBookingsTemplate = document.getElementById('new-bookings-template');
    
    if (newBookingsTemplate) {
        mainPanel.innerHTML = newBookingsTemplate.innerHTML;
        // Дополнительная инициализация...
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Новые бронирования" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка раздела "Аналитика"
 */
function loadAnalytics() {
    const mainPanel = document.getElementById('main-panel-content');
    const analyticsTemplate = document.getElementById('analytics-template');
    
    if (analyticsTemplate) {
        mainPanel.innerHTML = analyticsTemplate.innerHTML;
        
        // Инициализация графиков
        initBookingsChart();
        initRevenueChart();
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Аналитика" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка раздела "Отчеты"
 */
function loadReports() {
    const mainPanel = document.getElementById('main-panel-content');
    const reportsTemplate = document.getElementById('reports-template');
    
    if (reportsTemplate) {
        mainPanel.innerHTML = reportsTemplate.innerHTML;
        // Дополнительная инициализация...
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Отчеты" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка раздела "Модерация"
 */
function loadModeration() {
    const mainPanel = document.getElementById('main-panel-content');
    const moderationTemplate = document.getElementById('moderation-template');
    
    if (moderationTemplate) {
        mainPanel.innerHTML = moderationTemplate.innerHTML;
        
        // Загружаем компании, ожидающие модерации
        loadCompaniesForModeration();
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Модерация" находится в разработке
            </div>
        `;
    }
}

/**
 * Загрузка компаний, ожидающих модерации
 */
function loadCompaniesForModeration() {
    const moderationList = document.getElementById('moderation-companies-list');
    if (!moderationList) return;
    
    // Фильтруем компании, ожидающие модерации
    const pendingCompanies = companyData.filter(c => c.moderation_status === 'pending');
    
    if (pendingCompanies && pendingCompanies.length > 0) {
        let html = '';
        
        pendingCompanies.forEach(company => {
            html += `
                <div class="moderation-card" data-id="${company.id}">
                    <div class="moderation-card-header">
                        <h5>${company.name}</h5>
                        <span class="badge bg-warning">На модерации</span>
                    </div>
                    <div class="moderation-card-body">
                        <p class="company-description">${company.description}</p>
                        <div class="company-meta">
                            <div><i class="fas fa-phone"></i> ${company.phone}</div>
                            <div><i class="fas fa-envelope"></i> ${company.email}</div>
                            <div><i class="fas fa-map-marker-alt"></i> ${company.location?.city || ''}</div>
                        </div>
                    </div>
                    <div class="moderation-card-footer">
                        <button class="btn btn-sm btn-success approve-company" data-id="${company.id}">
                            <i class="fas fa-check"></i> Одобрить
                        </button>
                        <button class="btn btn-sm btn-danger reject-company" data-id="${company.id}">
                            <i class="fas fa-times"></i> Отклонить
                        </button>
                        <button class="btn btn-sm btn-secondary view-moderation-company" data-id="${company.id}">
                            <i class="fas fa-eye"></i> Подробнее
                        </button>
                    </div>
                </div>
            `;
        });
        
        moderationList.innerHTML = html;
        
        // Добавляем обработчики событий
        document.querySelectorAll('.approve-company').forEach(btn => {
            btn.addEventListener('click', function() {
                const companyId = parseInt(this.getAttribute('data-id'));
                approveCompany(companyId);
            });
        });
        
        document.querySelectorAll('.reject-company').forEach(btn => {
            btn.addEventListener('click', function() {
                const companyId = parseInt(this.getAttribute('data-id'));
                rejectCompany(companyId);
            });
        });
        
        document.querySelectorAll('.view-moderation-company').forEach(btn => {
            btn.addEventListener('click', function() {
                const companyId = parseInt(this.getAttribute('data-id'));
                viewCompanyDetails(companyId);
            });
        });
    } else {
        moderationList.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Нет компаний, ожидающих модерации
            </div>
        `;
    }
}

/**
 * Одобрение компании (модерация)
 * @param {number} companyId - ID компании
 */
function approveCompany(companyId) {
    // Находим компанию по ID
    const index = companyData.findIndex(c => c.id === companyId);
    
    if (index === -1) {
        addEvent('danger', 'Компания не найдена');
        return;
    }
    
    // Изменяем статус
    companyData[index].moderation_status = 'approved';
    
    // Добавляем событие в журнал
    addEvent('success', `Компания "${companyData[index].name}" одобрена`);
    
    // Обновляем список компаний на модерации
    loadCompaniesForModeration();
    
    // Обновляем счетчики уведомлений
    updateNotificationCounters();
}

/**
 * Отклонение компании (модерация)
 * @param {number} companyId - ID компании
 */
function rejectCompany(companyId) {
    // Находим компанию по ID
    const index = companyData.findIndex(c => c.id === companyId);
    
    if (index === -1) {
        addEvent('danger', 'Компания не найдена');
        return;
    }
    
    // Изменяем статус
    companyData[index].moderation_status = 'rejected';
    
    // Добавляем событие в журнал
    addEvent('warning', `Компания "${companyData[index].name}" отклонена`);
    
    // Обновляем список компаний на модерации
    loadCompaniesForModeration();
    
    // Обновляем счетчики уведомлений
    updateNotificationCounters();
}

/**
 * Загрузка раздела "Настройки Telegram"
 */
function loadTelegramSettings() {
    const mainPanel = document.getElementById('main-panel-content');
    const telegramTemplate = document.getElementById('telegram-template');
    
    if (telegramTemplate) {
        mainPanel.innerHTML = telegramTemplate.innerHTML;
        
        // Добавляем обработчик формы настроек
        document.getElementById('telegram-settings-form')?.addEventListener('submit', function(e) {
            e.preventDefault();
            saveTelegramSettings();
        });
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Настройки Telegram" находится в разработке
            </div>
        `;
    }
}

/**
 * Сохранение настроек Telegram
 */
function saveTelegramSettings() {
    const token = document.getElementById('telegram-token').value;
    const notifications = document.getElementById('telegram-notifications').checked;
    
    // В реальном приложении здесь был бы AJAX-запрос к API
    addEvent('success', 'Настройки Telegram успешно сохранены');
}

/**
 * Загрузка раздела "Профиль пользователя"
 */
function loadUserProfile() {
    const mainPanel = document.getElementById('main-panel-content');
    const profileTemplate = document.getElementById('profile-template');
    
    if (profileTemplate) {
        mainPanel.innerHTML = profileTemplate.innerHTML;
        
        // Добавляем обработчик формы профиля
        document.getElementById('profile-form')?.addEventListener('submit', function(e) {
            e.preventDefault();
            saveProfile();
        });
    } else {
        mainPanel.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Раздел "Профиль пользователя" находится в разработке
            </div>
        `;
    }
}

/**
 * Сохранение профиля пользователя
 */
function saveProfile() {
    const name = document.getElementById('profile-name').value;
    const email = document.getElementById('profile-email').value;
    
    // В реальном приложении здесь был бы AJAX-запрос к API
    addEvent('success', 'Профиль успешно обновлен');
}

/**
 * Инициализация графика бронирований для аналитики
 */
function initBookingsChart() {
    const bookingsChartCanvas = document.getElementById('bookings-chart');
    if (!bookingsChartCanvas) return;
    
    // Контекст для рисования
    const ctx = bookingsChartCanvas.getContext('2d');
    
    // Генерируем метки для последних 30 дней
    const labels = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }));
    }
    
    // Пример данных (в реальном приложении должны приходить с сервера)
    const bookingsData = [
        12, 15, 18, 14, 13, 16, 19, 21, 17, 15, 
        14, 13, 16, 20, 18, 17, 19, 22, 20, 18, 
        16, 17, 19, 21, 18, 16, 15, 17, 19, 22
    ];
    
    // Создаем график
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Бронирования',
                data: bookingsData,
                backgroundColor: 'rgba(78, 115, 223, 0.05)',
                borderColor: 'rgba(78, 115, 223, 1)',
                borderWidth: 2,
                pointRadius: 3,
                pointBackgroundColor: 'rgba(78, 115, 223, 1)',
                pointBorderColor: 'rgba(255, 255, 255, 1)',
                pointHoverRadius: 5,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Инициализация графика выручки для аналитики
 */
function initRevenueChart() {
    const revenueChartCanvas = document.getElementById('revenue-chart');
    if (!revenueChartCanvas) return;
    
    // Контекст для рисования
    const ctx = revenueChartCanvas.getContext('2d');
    
    // Пример данных по месяцам (в реальном приложении должны приходить с сервера)
    const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
    const revenueData = [
        42000, 38000, 47000, 51000, 54000, 57000, 
        65000, 68000, 71000, 66000, 62000, 75000
    ];
    
    // Создаем график
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [{
                label: 'Выручка, ₽',
                data: revenueData,
                backgroundColor: 'rgba(40, 167, 69, 0.6)',
                borderColor: 'rgba(40, 167, 69, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Обновление данных
 */
function refreshData() {
    // В реальном приложении здесь был бы AJAX-запрос для обновления данных с сервера
    addEvent('info', 'Данные обновлены');
    
    // Перезагружаем текущий раздел
    loadSection(currentSection);
}

/**
 * Получение HTML для бейджа статуса
 * @param {string} status - Статус модерации
 * @returns {string} HTML бейджа
 */
function getStatusBadgeHTML(status) {
    switch (status) {
        case 'approved':
            return '<span class="badge bg-success">Активна</span>';
        case 'pending':
            return '<span class="badge bg-warning">На модерации</span>';
        case 'rejected':
            return '<span class="badge bg-danger">Отклонена</span>';
        default:
            return '<span class="badge bg-secondary">Неизвестно</span>';
    }
}

/**
 * Обрезка текста до заданной длины
 * @param {string} text - Исходный текст
 * @param {number} maxLength - Максимальная длина
 * @returns {string} Обрезанный текст
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

/**
 * Инициализация ситуационного центра
 */
function initSituationCenter() {
    console.log('Инициализация ситуационного центра...');
    
    // Проверяем наличие необходимых элементов
    const requiredElements = ['situation-center', 'panel-right', 'panel-main', 'panel-bottom'];
    for (const id of requiredElements) {
        if (!document.getElementById(id)) {
            console.error(`Не найден обязательный элемент с ID: ${id}`);
            addEvent('danger', `Ошибка инициализации: Не найден элемент ${id}`);
        }
    }
}

/**
 * Настройка обработчиков навигации
 */
function setupNavigation() {
    console.log('Настройка навигации...');
    
    // Обработчики для навигационных элементов
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            const title = this.getAttribute('data-title');
            
            // Убираем активный класс со всех элементов
            document.querySelectorAll('.nav-item').forEach(navItem => {
                navItem.classList.remove('active');
            });
            
            // Добавляем активный класс на текущий элемент
            this.classList.add('active');
            
            // Устанавливаем заголовок панели
            document.getElementById('main-panel-title').textContent = title;
            document.getElementById('current-section-indicator').textContent = title;
            
            // Загружаем соответствующий раздел
            loadSection(section);
            
            // Добавляем событие в журнал
            addEvent('info', `Загружен раздел: ${title}`);
        });
    });
    
    // Кнопка обновления данных
    document.querySelector('.refresh-data').addEventListener('click', function() {
        refreshData();
    });
}

/**
 * Корректировка размеров панелей для фиксированной структуры
 */
function adjustPanelSizes() {
    // Проверяем, что мы не на мобильном устройстве
    if (window.innerWidth <= 768) {
        return;
    }
    
    const situationCenter = document.getElementById('situation-center');
    if (!situationCenter) return;
    
    // Обеспечиваем, чтобы все панели были правильного размера с возможностью скроллинга
    const panels = ['panel-main', 'panel-right', 'panel-bottom'];
    
    panels.forEach(panelId => {
        const panel = document.getElementById(panelId);
        const panelContent = panel.querySelector('.panel-content');
        
        if (panel && panelContent) {
            // Убеждаемся, что контент имеет правильный режим прокрутки
            panelContent.style.overflowY = 'auto';
            panelContent.style.overflowX = 'hidden';
        }
    });
    
    // Добавляем сообщение в журнал
    console.log('Размеры панелей скорректированы');
}

/**
 * Получение иконки для типа события
 * @param {string} type - Тип события
 * @returns {string} Название иконки
 */
function getEventIcon(type) {
    switch (type) {
        case 'info': return 'fas fa-info-circle';
        case 'success': return 'fas fa-check-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'danger': return 'fas fa-times-circle';
        default: return 'fas fa-bell';
    }
} 