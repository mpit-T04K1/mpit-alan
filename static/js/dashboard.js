/**
 * JavaScript для работы с трехпанельным "ситуационным центром"
 */

// Глобальные переменные
let companyData = [];
let currentView = 'dashboard';
let selectedCompanyId = null;

// Инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Загрузка данных компаний из JSON
    try {
        const companyDataJson = document.getElementById('company-data-json')?.textContent;
        if (companyDataJson) {
            companyData = JSON.parse(companyDataJson);
        }
    } catch (e) {
        console.error('Ошибка при парсинге данных компаний:', e);
    }
    
    // Инициализация трехпанельного интерфейса
    initPanelsLayout();
    
    // Загрузка начального содержимого панелей
    loadMainPanelContent('dashboard');
    loadRightPanelContent('companies-list');
    
    // Обработчик изменения размера окна
    window.addEventListener('resize', adjustPanelsHeight);
    
    // Инициализация маршрутизации
    initRouting();
    
    // Добавляем событие при первой загрузке
    addEventToLog('info', 'Ситуационный центр загружен');
});

/**
 * Инициализация трехпанельного интерфейса
 */
function initPanelsLayout() {
    // Устанавливаем первоначальные размеры панелей
    adjustPanelsHeight();
    
    // Обработчики для прокрутки внутри панелей
    const panelContents = document.querySelectorAll('.panel-content');
    panelContents.forEach(panel => {
        panel.addEventListener('wheel', function(e) {
            // Если контент панели прокручивается полностью, 
            // останавливаем дальнейшее распространение события прокрутки
            const atTop = this.scrollTop === 0;
            const atBottom = this.scrollHeight - this.scrollTop === this.clientHeight;
            
            if ((atTop && e.deltaY < 0) || (atBottom && e.deltaY > 0)) {
                e.preventDefault();
            }
        }, { passive: false });
    });
    
    // Инициализация обработчиков событий
    document.getElementById('clear-events').addEventListener('click', clearEvents);
}

/**
 * Корректировка высоты панелей в зависимости от высоты окна
 */
function adjustPanelsHeight() {
    // Если мы на мобильных устройствах, просто возвращаемся
    if (window.innerWidth <= 1199) {
        // Сбрасываем фиксированное позиционирование на мобильных устройствах
        document.querySelector('.situation-center-layout').style.position = 'static';
        document.querySelectorAll('.panel-content').forEach(panel => {
            panel.style.position = 'static';
        });
        return;
    }
    
    // Получаем высоту видимой области
    const viewportHeight = window.innerHeight;
    const layoutTop = 70; // Отступ сверху (высота верхней навигации)
    const layoutMargin = 20; // Отступ от краев экрана
    
    // Устанавливаем размеры контейнера ситуационного центра
    const layout = document.querySelector('.situation-center-layout');
    layout.style.position = 'fixed';
    layout.style.top = layoutTop + 'px';
    layout.style.height = (viewportHeight - layoutTop - layoutMargin) + 'px';
    
    // Восстанавливаем абсолютное позиционирование для контента панелей
    document.querySelectorAll('.panel-content').forEach(panel => {
        panel.style.position = 'absolute';
    });
}

/**
 * Инициализация маршрутизации и обработки кликов
 */
function initRouting() {
    // Делегирование событий для кликов в правой панели
    document.getElementById('right-panel-content').addEventListener('click', function(e) {
        // Выбор компании из списка
        if (e.target.closest('.company-item')) {
            const companyId = e.target.closest('.company-item').dataset.id;
            selectCompany(companyId);
            return;
        }
        
        // Создание новой компании
        if (e.target.closest('.create-company-btn')) {
            loadMainPanelContent('company-form');
            addEventToLog('info', 'Открыта форма создания компании');
            return;
        }
    });
    
    // Делегирование событий для основной панели
    document.getElementById('main-panel-content').addEventListener('click', function(e) {
        // Отправка формы компании
        if (e.target.closest('#submit-company-form')) {
            submitCompanyForm();
            return;
        }
        
        // Кнопка возврата к списку
        if (e.target.closest('.back-to-dashboard')) {
            loadMainPanelContent('dashboard');
            return;
        }
    });
    
    // Обработчик кнопки обновления данных
    document.querySelector('.refresh-data')?.addEventListener('click', function() {
        refreshData();
    });
}

/**
 * Загрузка содержимого основной панели
 * @param {string} view - Имя представления для загрузки
 * @param {Object} data - Дополнительные данные для представления
 */
function loadMainPanelContent(view, data = {}) {
    currentView = view;
    const mainPanel = document.getElementById('main-panel-content');
    
    // Очистка содержимого
    mainPanel.innerHTML = '';
    
    // Загрузка соответствующего HTML-фрагмента
    switch (view) {
        case 'dashboard':
            mainPanel.innerHTML = generateDashboardHTML();
            initCharts();
            break;
            
        case 'company-form':
            mainPanel.innerHTML = generateCompanyFormHTML(data.company);
            // Инициализируем форму
            initCompanyForm();
            break;
            
        case 'company-details':
            if (data.company) {
                mainPanel.innerHTML = generateCompanyDetailsHTML(data.company);
            }
            break;
            
        default:
            mainPanel.innerHTML = '<div class="alert alert-info">Выберите действие в правой панели</div>';
    }
    
    // Добавляем событие
    addEventToLog('info', `Загружен интерфейс: ${view}`);
}

/**
 * Загрузка содержимого правой панели
 * @param {string} view - Имя представления для загрузки
 * @param {Object} data - Дополнительные данные для представления
 */
function loadRightPanelContent(view, data = {}) {
    const rightPanel = document.getElementById('right-panel-content');
    
    // Очистка содержимого
    rightPanel.innerHTML = '';
    
    // Загрузка соответствующего HTML-фрагмента
    switch (view) {
        case 'companies-list':
            rightPanel.innerHTML = generateCompaniesListHTML();
            break;
            
        case 'user-profile':
            rightPanel.innerHTML = generateUserProfileHTML();
            break;
            
        default:
            rightPanel.innerHTML = generateCompaniesListHTML();
    }
}

/**
 * Генерация HTML для обзорной панели
 */
function generateDashboardHTML() {
    return `
        <div class="dashboard-container">
            <h3>Обзор системы</h3>
            
            <div class="row mt-4">
                <div class="col-md-4 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-header">Компании</div>
                        <div class="stat-card-value">${companyData.length}</div>
                        <div class="stat-card-info">Всего компаний</div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-header">Активные</div>
                        <div class="stat-card-value">${companyData.filter(c => c.moderation_status === 'approved').length}</div>
                        <div class="stat-card-info">Одобренные компании</div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div class="stat-card">
                        <div class="stat-card-header">На модерации</div>
                        <div class="stat-card-value">${companyData.filter(c => c.moderation_status === 'pending').length}</div>
                        <div class="stat-card-info">Ожидающие проверки</div>
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Статистика компаний</h5>
                </div>
                <div class="card-body">
                    <canvas id="companiesStatusChart" height="300"></canvas>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Активность по дням</h5>
                </div>
                <div class="card-body">
                    <canvas id="activityChart" height="250"></canvas>
                </div>
            </div>
        </div>
    `;
}

/**
 * Генерация HTML для формы создания/редактирования компании
 * @param {Object} company - Компания для редактирования (или null для создания)
 */
function generateCompanyFormHTML(company = null) {
    const isEdit = company !== null;
    return `
        <div class="company-form-container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3>${isEdit ? 'Редактирование компании' : 'Создание новой компании'}</h3>
                <button class="btn btn-outline-secondary back-to-dashboard">
                    <i class="fas fa-arrow-left"></i> Назад
                </button>
            </div>
            
            <form id="company-form" class="needs-validation">
                <div class="mb-3">
                    <label for="companyName" class="form-label">Название компании*</label>
                    <input type="text" class="form-control" id="companyName" name="name" required 
                           value="${isEdit ? company.name : ''}">
                </div>
                
                <div class="mb-3">
                    <label for="companyDescription" class="form-label">Описание компании*</label>
                    <textarea class="form-control" id="companyDescription" name="description" rows="3" required>${isEdit ? company.description : ''}</textarea>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="companyPhone" class="form-label">Телефон*</label>
                        <input type="tel" class="form-control" id="companyPhone" name="phone" required 
                               value="${isEdit ? company.phone : ''}">
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="companyEmail" class="form-label">Email*</label>
                        <input type="email" class="form-control" id="companyEmail" name="email" required 
                               value="${isEdit ? company.email : ''}">
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="companyWebsite" class="form-label">Веб-сайт</label>
                    <input type="url" class="form-control" id="companyWebsite" name="website" 
                           value="${isEdit && company.website ? company.website : ''}">
                </div>
                
                <div class="mb-3">
                    <label for="companyLogo" class="form-label">Логотип компании</label>
                    <input type="file" class="form-control" id="companyLogo" name="logo" accept="image/*">
                    ${isEdit && company.logo ? `<div class="mt-2"><img src="${company.logo}" alt="Текущий логотип" height="50"></div>` : ''}
                </div>
                
                <div class="mb-3">
                    <label for="companyCategory" class="form-label">Категория*</label>
                    <select class="form-select" id="companyCategory" name="category_id" required>
                        <option value="" disabled ${!isEdit ? 'selected' : ''}>Выберите категорию</option>
                        <option value="1" ${isEdit && company.category_id === 1 ? 'selected' : ''}>Рестораны</option>
                        <option value="2" ${isEdit && company.category_id === 2 ? 'selected' : ''}>Салоны красоты</option>
                        <option value="3" ${isEdit && company.category_id === 3 ? 'selected' : ''}>Медицинские услуги</option>
                        <option value="4" ${isEdit && company.category_id === 4 ? 'selected' : ''}>Фитнес и спорт</option>
                    </select>
                </div>
                
                <h5 class="mt-4">Адрес</h5>
                <hr>
                
                <div class="mb-3">
                    <label for="companyAddress" class="form-label">Адрес*</label>
                    <input type="text" class="form-control" id="companyAddress" name="location.address" required 
                           value="${isEdit && company.location ? company.location.address : ''}">
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="companyCity" class="form-label">Город*</label>
                        <input type="text" class="form-control" id="companyCity" name="location.city" required 
                               value="${isEdit && company.location ? company.location.city : ''}">
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="companyZipcode" class="form-label">Почтовый индекс</label>
                        <input type="text" class="form-control" id="companyZipcode" name="location.zipcode" 
                               value="${isEdit && company.location && company.location.zipcode ? company.location.zipcode : ''}">
                    </div>
                </div>
                
                <div class="d-flex justify-content-end mt-4">
                    <button type="button" class="btn btn-secondary me-2 back-to-dashboard">Отмена</button>
                    <button type="button" class="btn btn-primary" id="submit-company-form">
                        ${isEdit ? 'Сохранить изменения' : 'Создать компанию'}
                    </button>
                </div>
            </form>
        </div>
    `;
}

/**
 * Генерация HTML для детальной информации о компании
 * @param {Object} company - Объект компании
 */
function generateCompanyDetailsHTML(company) {
    return `
        <div class="company-details-container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3>Информация о компании</h3>
                <button class="btn btn-outline-secondary back-to-dashboard">
                    <i class="fas fa-arrow-left"></i> Назад
                </button>
            </div>
            
            <div class="company-info-card">
                <div class="company-logo text-center mb-3">
                    <img src="${company.logo || '/static/img/default-company-logo.png'}" alt="${company.name}" 
                         class="company-logo-img">
                </div>
                
                <h4 class="company-name">${company.name}</h4>
                <div class="mb-2">
                    ${getStatusBadgeHtml(company.moderation_status)}
                </div>
                <p class="company-description">${company.description}</p>
                
                <div class="company-meta mt-4">
                    <div class="company-contacts">
                        <div><i class="fas fa-phone"></i> ${company.phone}</div>
                        <div><i class="fas fa-envelope"></i> ${company.email}</div>
                        ${company.website ? `<div><i class="fas fa-globe"></i> <a href="${company.website}" target="_blank">${company.website}</a></div>` : ''}
                    </div>
                    
                    ${company.location ? `
                    <div class="company-address mt-3">
                        <i class="fas fa-map-marker-alt"></i> ${company.location.address}, ${company.location.city} 
                        ${company.location.zipcode ? company.location.zipcode : ''}
                    </div>` : ''}
                </div>
                
                <div class="d-flex justify-content-end mt-4">
                    <button class="btn btn-outline-primary me-2" onclick="loadMainPanelContent('company-form', {company: ${JSON.stringify(company)}})">
                        <i class="fas fa-edit"></i> Редактировать
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteCompany(${company.id})">
                        <i class="fas fa-trash"></i> Удалить
                    </button>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h5>Услуги компании</h5>
                </div>
                <div class="card-body">
                    <div id="company-services-list">
                        <div class="alert alert-info">Загрузка услуг...</div>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-outline-primary" onclick="loadServiceForm(${company.id})">
                        <i class="fas fa-plus"></i> Добавить услугу
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Генерация HTML для списка компаний (правая панель)
 */
function generateCompaniesListHTML() {
    let html = `
        <div class="companies-list-container">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>Мои компании</h4>
                <button class="btn btn-sm btn-primary create-company-btn">
                    <i class="fas fa-plus"></i> Создать
                </button>
            </div>
            
            <div class="search-bar mb-3">
                <input type="text" class="form-control form-control-sm" placeholder="Поиск компаний..." 
                       id="company-search">
            </div>
            
            <div class="companies-list" id="companies-list">
    `;
    
    if (companyData && companyData.length > 0) {
        companyData.forEach(company => {
            html += `
                <div class="company-item ${selectedCompanyId === company.id ? 'active' : ''}" data-id="${company.id}">
                    <div class="company-item-header">
                        <h5>${company.name}</h5>
                        ${getStatusBadgeHtml(company.moderation_status)}
                    </div>
                    <div class="company-item-body">
                        <p>${truncateText(company.description, 100)}</p>
                    </div>
                </div>
            `;
        });
    } else {
        html += `
            <div class="alert alert-info">
                У вас пока нет компаний. Создайте свою первую компанию с помощью кнопки "Создать".
            </div>
        `;
    }
    
    html += `
            </div>
        </div>
        
        <div class="user-profile-card mt-4">
            <div class="user-profile">
                <div class="user-avatar">
                    <img src="/static/img/default-avatar.png" alt="Аватар пользователя">
                </div>
                <div class="user-info">
                    <div class="user-name">{{ user.full_name }}</div>
                    <div class="user-email">{{ user.email }}</div>
                    <div class="user-role">
                        <span class="badge bg-danger">Администратор</span>
                    </div>
                </div>
            </div>
            <div class="user-actions mt-3">
                <button class="btn btn-sm btn-outline-secondary w-100">
                    <i class="fas fa-user-edit"></i> Редактировать профиль
                </button>
            </div>
        </div>
    `;
    
    return html;
}

/**
 * Генерация HTML для профиля пользователя
 */
function generateUserProfileHTML() {
    return `
        <div class="user-profile-container">
            <h4>Мой профиль</h4>
            
            <div class="user-profile-card mt-3">
                <div class="text-center mb-3">
                    <div class="user-avatar mx-auto">
                        <img src="/static/img/default-avatar.png" alt="Аватар пользователя">
                    </div>
                    <button class="btn btn-sm btn-outline-secondary mt-2">
                        <i class="fas fa-camera"></i> Изменить фото
                    </button>
                </div>
                
                <div class="user-info">
                    <div class="mb-3">
                        <label class="form-label">Имя</label>
                        <input type="text" class="form-control" value="{{ user.full_name }}">
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-control" value="{{ user.email }}" readonly>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Роль</label>
                        <input type="text" class="form-control" value="Администратор" readonly>
                    </div>
                    
                    <div class="d-grid mt-4">
                        <button class="btn btn-primary">Сохранить изменения</button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Добавление события в журнал
 * @param {string} type - Тип события (info, success, warning, danger)
 * @param {string} message - Сообщение события
 */
function addEventToLog(type, message) {
    const eventsContainer = document.getElementById('events-list');
    const now = new Date();
    const timeString = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    const eventItem = document.createElement('div');
    eventItem.className = 'event-item';
    eventItem.innerHTML = `
        <div class="event-icon ${type}">
            <i class="fas fa-${getEventIcon(type)}"></i>
        </div>
        <div class="event-content">
            <div class="event-title">${message}</div>
            <div class="event-time">${timeString}</div>
        </div>
    `;
    
    eventsContainer.prepend(eventItem);
}

/**
 * Получение иконки для типа события
 * @param {string} type - Тип события
 * @returns {string} Название иконки
 */
function getEventIcon(type) {
    switch (type) {
        case 'info': return 'info-circle';
        case 'success': return 'check-circle';
        case 'warning': return 'exclamation-triangle';
        case 'danger': return 'times-circle';
        default: return 'bell';
    }
}

/**
 * Очистка журнала событий
 */
function clearEvents() {
    document.getElementById('events-list').innerHTML = '';
    addEventToLog('info', 'Журнал событий очищен');
}

/**
 * Получение HTML для значка статуса компании
 * @param {string} status - Статус компании
 * @returns {string} HTML для значка
 */
function getStatusBadgeHtml(status) {
    let badge = '';
    switch (status) {
        case 'approved':
            badge = '<span class="badge bg-success">Одобрено</span>';
            break;
        case 'pending':
            badge = '<span class="badge bg-warning text-dark">На модерации</span>';
            break;
        case 'rejected':
            badge = '<span class="badge bg-danger">Отклонено</span>';
            break;
        default:
            badge = '<span class="badge bg-secondary">Неизвестно</span>';
    }
    return badge;
}

/**
 * Усечение текста до указанной длины
 * @param {string} text - Исходный текст
 * @param {number} maxLength - Максимальная длина
 * @returns {string} Усеченный текст
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength) + '...';
}

/**
 * Выбор компании из списка
 * @param {number} companyId - ID компании
 */
function selectCompany(companyId) {
    selectedCompanyId = parseInt(companyId);
    
    // Обновляем список компаний в правой панели
    loadRightPanelContent('companies-list');
    
    // Загружаем детальную информацию о компании
    const company = companyData.find(c => c.id === selectedCompanyId);
    if (company) {
        loadMainPanelContent('company-details', { company });
        addEventToLog('info', `Выбрана компания: ${company.name}`);
    }
}

/**
 * Инициализация формы компании
 */
function initCompanyForm() {
    // Здесь можно добавить валидацию и другую логику для формы
    document.getElementById('submit-company-form')?.addEventListener('click', function() {
        submitCompanyForm();
    });
}

/**
 * Отправка формы компании
 */
function submitCompanyForm() {
    const form = document.getElementById('company-form');
    
    // Базовая валидация
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        addEventToLog('warning', 'Пожалуйста, заполните все обязательные поля');
        return;
    }
    
    // В реальном приложении здесь был бы AJAX-запрос к API
    addEventToLog('success', 'Компания успешно сохранена');
    loadMainPanelContent('dashboard');
}

/**
 * Удаление компании
 * @param {number} companyId - ID компании
 */
function deleteCompany(companyId) {
    if (confirm('Вы уверены, что хотите удалить эту компанию?')) {
        // В реальном приложении здесь был бы AJAX-запрос к API
        addEventToLog('success', 'Компания успешно удалена');
        
        // Удаляем из списка
        companyData = companyData.filter(c => c.id !== companyId);
        
        // Обновляем интерфейс
        loadMainPanelContent('dashboard');
        loadRightPanelContent('companies-list');
    }
}

/**
 * Обновление данных
 */
function refreshData() {
    // В реальном приложении здесь был бы AJAX-запрос к API
    addEventToLog('info', 'Данные обновлены');
    
    // Перезагружаем текущее представление
    loadMainPanelContent(currentView);
    loadRightPanelContent('companies-list');
}

/**
 * Инициализация графиков
 */
function initCharts() {
    // Если на странице есть элемент для графика статусов компаний
    const statusChartElement = document.getElementById('companiesStatusChart');
    if (statusChartElement) {
        // Подсчет компаний по статусам
        const approved = companyData.filter(c => c.moderation_status === 'approved').length;
        const pending = companyData.filter(c => c.moderation_status === 'pending').length;
        const rejected = companyData.filter(c => c.moderation_status === 'rejected').length;
        
        // Создание графика
        new Chart(statusChartElement, {
            type: 'pie',
            data: {
                labels: ['Одобрено', 'На модерации', 'Отклонено'],
                datasets: [{
                    data: [approved, pending, rejected],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                }]
            }
        });
    }
    
    // График активности по дням
    const activityChartElement = document.getElementById('activityChart');
    if (activityChartElement) {
        new Chart(activityChartElement, {
            type: 'line',
            data: {
                labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
                datasets: [{
                    label: 'Активность',
                    data: [65, 59, 80, 81, 56, 55, 40],
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderColor: '#0d6efd',
                    tension: 0.1
                }]
            }
        });
    }
} 