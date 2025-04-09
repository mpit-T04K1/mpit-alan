/**
 * Скрипт для работы с динамическими формами
 * Позволяет генерировать HTML формы на основе JSON-конфигураций
 */

class DynamicForm {
    /**
     * Конструктор класса DynamicForm
     * @param {string} containerId - ID контейнера для формы
     * @param {Object} config - Конфигурация формы
     * @param {Object} values - Начальные значения полей (опционально)
     */
    constructor(containerId, config, values = {}) {
        this.container = document.getElementById(containerId);
        this.config = config;
        this.values = values;
        this.elements = {};
        this.validators = {};
        
        if (!this.container) {
            console.error(`Container with ID "${containerId}" not found`);
            return;
        }
        
        this.render();
        this.setupValidation();
    }
    
    /**
     * Отображает форму в контейнере
     */
    render() {
        if (!this.config || !this.config.fields) {
            console.error('Invalid form configuration');
            return;
        }
        
        // Очищаем контейнер
        this.container.innerHTML = '';
        
        // Создаем заголовок формы
        if (this.config.title) {
            const titleElement = document.createElement('h3');
            titleElement.className = 'mb-4';
            titleElement.textContent = this.config.title;
            this.container.appendChild(titleElement);
        }
        
        // Создаем описание формы
        if (this.config.description) {
            const descElement = document.createElement('p');
            descElement.className = 'text-muted mb-4';
            descElement.textContent = this.config.description;
            this.container.appendChild(descElement);
        }
        
        // Создаем форму
        const form = document.createElement('form');
        form.className = 'dynamic-form';
        form.id = 'dynamic-form-' + (Math.random().toString(36).substring(2, 9));
        this.formElement = form;
        
        // Сортируем поля по порядку
        const sortedFields = [...this.config.fields].sort((a, b) => (a.order || 0) - (b.order || 0));
        
        // Создаем поля формы
        sortedFields.forEach(field => {
            const fieldElement = this.createField(field);
            if (fieldElement) {
                form.appendChild(fieldElement);
            }
        });
        
        // Создаем кнопки действий
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'dynamic-form-actions';
        
        // Кнопка отмены
        if (this.config.cancel_label) {
            const cancelBtn = document.createElement('button');
            cancelBtn.type = 'button';
            cancelBtn.className = 'btn btn-outline-secondary';
            cancelBtn.textContent = this.config.cancel_label;
            cancelBtn.addEventListener('click', this.handleCancel.bind(this));
            actionsDiv.appendChild(cancelBtn);
        }
        
        // Кнопка сохранения
        const submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn btn-primary';
        submitBtn.textContent = this.config.submit_label || 'Сохранить';
        actionsDiv.appendChild(submitBtn);
        
        form.appendChild(actionsDiv);
        form.addEventListener('submit', this.handleSubmit.bind(this));
        
        this.container.appendChild(form);
    }
    
    /**
     * Создает HTML элемент для поля формы на основе его типа
     * @param {Object} field - Конфигурация поля
     * @returns {HTMLElement} - HTML элемент поля формы
     */
    createField(field) {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'dynamic-form-field';
        
        if (field.required) {
            fieldDiv.classList.add('required');
        }
        
        // Проверяем условия отображения поля
        if (field.conditional_display && !this.checkCondition(field.conditional_display)) {
            fieldDiv.style.display = 'none';
        }
        
        // Создаем метку поля
        const label = document.createElement('label');
        label.setAttribute('for', field.name);
        label.textContent = field.label;
        fieldDiv.appendChild(label);
        
        let inputElement;
        
        // Создаем поле в зависимости от его типа
        switch (field.field_type) {
            case 'text':
            case 'email':
            case 'password':
            case 'number':
            case 'date':
            case 'time':
            case 'tel':
            case 'url':
                inputElement = document.createElement('input');
                inputElement.type = field.field_type;
                inputElement.id = field.name;
                inputElement.name = field.name;
                inputElement.className = 'form-control';
                
                if (field.placeholder) {
                    inputElement.placeholder = field.placeholder;
                }
                
                if (field.required) {
                    inputElement.required = true;
                }
                
                if (field.default_value || this.values[field.name]) {
                    inputElement.value = this.values[field.name] || field.default_value;
                }
                
                fieldDiv.appendChild(inputElement);
                break;
                
            case 'textarea':
                inputElement = document.createElement('textarea');
                inputElement.id = field.name;
                inputElement.name = field.name;
                inputElement.className = 'form-control';
                inputElement.rows = field.rows || 3;
                
                if (field.placeholder) {
                    inputElement.placeholder = field.placeholder;
                }
                
                if (field.required) {
                    inputElement.required = true;
                }
                
                if (field.default_value || this.values[field.name]) {
                    inputElement.value = this.values[field.name] || field.default_value;
                }
                
                fieldDiv.appendChild(inputElement);
                break;
                
            case 'select':
                inputElement = document.createElement('select');
                inputElement.id = field.name;
                inputElement.name = field.name;
                inputElement.className = 'form-select';
                
                if (field.required) {
                    inputElement.required = true;
                }
                
                // Добавляем пустую опцию
                if (!field.required) {
                    const emptyOption = document.createElement('option');
                    emptyOption.value = '';
                    emptyOption.textContent = field.placeholder || 'Выберите...';
                    inputElement.appendChild(emptyOption);
                }
                
                // Добавляем опции
                if (field.options && Array.isArray(field.options)) {
                    field.options.forEach(option => {
                        const optionElement = document.createElement('option');
                        optionElement.value = option.value;
                        optionElement.textContent = option.label;
                        
                        const currentValue = this.values[field.name] || field.default_value;
                        if (currentValue === option.value) {
                            optionElement.selected = true;
                        }
                        
                        inputElement.appendChild(optionElement);
                    });
                }
                
                fieldDiv.appendChild(inputElement);
                break;
                
            case 'checkbox':
                const checkDiv = document.createElement('div');
                checkDiv.className = 'form-check';
                
                inputElement = document.createElement('input');
                inputElement.type = 'checkbox';
                inputElement.id = field.name;
                inputElement.name = field.name;
                inputElement.className = 'form-check-input';
                
                if (field.required) {
                    inputElement.required = true;
                }
                
                if ((field.default_value && field.default_value === true) || this.values[field.name] === true) {
                    inputElement.checked = true;
                }
                
                const checkLabel = document.createElement('label');
                checkLabel.className = 'form-check-label';
                checkLabel.setAttribute('for', field.name);
                checkLabel.textContent = field.label;
                
                checkDiv.appendChild(inputElement);
                checkDiv.appendChild(checkLabel);
                fieldDiv.removeChild(label); // Удаляем исходную метку
                fieldDiv.appendChild(checkDiv);
                break;
                
            case 'radio':
                const radioDiv = document.createElement('div');
                
                if (field.options && Array.isArray(field.options)) {
                    field.options.forEach((option, index) => {
                        const radioItemDiv = document.createElement('div');
                        radioItemDiv.className = 'form-check';
                        
                        const radioInput = document.createElement('input');
                        radioInput.type = 'radio';
                        radioInput.id = `${field.name}_${index}`;
                        radioInput.name = field.name;
                        radioInput.value = option.value;
                        radioInput.className = 'form-check-input';
                        
                        if (field.required) {
                            radioInput.required = true;
                        }
                        
                        const currentValue = this.values[field.name] || field.default_value;
                        if (currentValue === option.value) {
                            radioInput.checked = true;
                        }
                        
                        const radioLabel = document.createElement('label');
                        radioLabel.className = 'form-check-label';
                        radioLabel.setAttribute('for', `${field.name}_${index}`);
                        radioLabel.textContent = option.label;
                        
                        radioItemDiv.appendChild(radioInput);
                        radioItemDiv.appendChild(radioLabel);
                        radioDiv.appendChild(radioItemDiv);
                        
                        if (index === 0) {
                            inputElement = radioInput; // Сохраняем первый элемент как основной
                        }
                    });
                }
                
                fieldDiv.appendChild(radioDiv);
                break;
                
            case 'file':
                inputElement = document.createElement('input');
                inputElement.type = 'file';
                inputElement.id = field.name;
                inputElement.name = field.name;
                inputElement.className = 'form-control';
                
                if (field.required) {
                    inputElement.required = true;
                }
                
                // Дополнительные атрибуты для файлов
                if (field.validation && field.validation.accepted_types) {
                    inputElement.accept = field.validation.accepted_types.join(',');
                }
                
                fieldDiv.appendChild(inputElement);
                break;
            
            default:
                console.warn(`Unknown field type: ${field.field_type}`);
                return null;
        }
        
        // Сохраняем элемент ввода
        if (inputElement) {
            this.elements[field.name] = inputElement;
            
            // Добавляем обработчики событий для условных полей
            if (field.conditional_display && field.conditional_display.field) {
                const sourceField = field.conditional_display.field;
                const sourceElement = this.elements[sourceField];
                
                if (sourceElement) {
                    sourceElement.addEventListener('change', () => {
                        const isVisible = this.checkCondition(field.conditional_display);
                        fieldDiv.style.display = isVisible ? 'block' : 'none';
                    });
                }
            }
        }
        
        // Добавляем вспомогательный текст, если есть
        if (field.help_text) {
            const helpText = document.createElement('small');
            helpText.className = 'help-text';
            helpText.textContent = field.help_text;
            fieldDiv.appendChild(helpText);
        }
        
        // Добавляем контейнер для сообщений об ошибках
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.id = `${field.name}-error`;
        fieldDiv.appendChild(errorDiv);
        
        return fieldDiv;
    }
    
    /**
     * Проверяет выполнение условия для отображения поля
     * @param {Object} condition - Условие отображения
     * @returns {boolean} - Результат проверки условия
     */
    checkCondition(condition) {
        if (!condition || !condition.field || !condition.operator || condition.value === undefined) {
            return true;
        }
        
        const sourceElement = this.elements[condition.field];
        if (!sourceElement) {
            return true;
        }
        
        let sourceValue = sourceElement.type === 'checkbox' ? sourceElement.checked : sourceElement.value;
        
        switch (condition.operator) {
            case 'equals':
                return sourceValue == condition.value;
            case 'not_equals':
                return sourceValue != condition.value;
            case 'contains':
                return String(sourceValue).includes(String(condition.value));
            case 'not_contains':
                return !String(sourceValue).includes(String(condition.value));
            case 'empty':
                return !sourceValue || sourceValue.length === 0;
            case 'not_empty':
                return sourceValue && sourceValue.length > 0;
            default:
                console.warn(`Unknown condition operator: ${condition.operator}`);
                return true;
        }
    }
    
    /**
     * Настраивает валидацию полей формы
     */
    setupValidation() {
        this.config.fields.forEach(field => {
            if (!field.validation) return;
            
            const element = this.elements[field.name];
            if (!element) return;
            
            const validator = {
                field: field,
                validate: (value) => {
                    const errors = [];
                    const validation = field.validation;
                    
                    // Проверка обязательных полей
                    if (field.required && (!value || value.length === 0)) {
                        errors.push('Это поле обязательно для заполнения');
                    }
                    
                    if (!value || value.length === 0) {
                        return errors; // Не продолжаем проверку, если поле пустое
                    }
                    
                    // Проверка минимальной длины
                    if (validation.min_length && value.length < validation.min_length) {
                        errors.push(`Минимальная длина: ${validation.min_length} символов`);
                    }
                    
                    // Проверка максимальной длины
                    if (validation.max_length && value.length > validation.max_length) {
                        errors.push(`Максимальная длина: ${validation.max_length} символов`);
                    }
                    
                    // Проверка регулярного выражения
                    if (validation.pattern) {
                        const regex = new RegExp(validation.pattern);
                        if (!regex.test(value)) {
                            errors.push(validation.pattern_error || 'Значение не соответствует формату');
                        }
                    }
                    
                    // Дополнительные проверки
                    if (field.field_type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                        errors.push('Неверный формат email');
                    }
                    
                    return errors;
                }
            };
            
            this.validators[field.name] = validator;
            
            // Добавляем обработчик события input для проверки в реальном времени
            element.addEventListener('input', () => {
                this.validateField(field.name);
            });
            
            element.addEventListener('blur', () => {
                this.validateField(field.name);
            });
        });
    }
    
    /**
     * Проверяет одно поле формы
     * @param {string} fieldName - Имя поля
     * @returns {boolean} - Результат проверки
     */
    validateField(fieldName) {
        const validator = this.validators[fieldName];
        const element = this.elements[fieldName];
        const errorContainer = document.getElementById(`${fieldName}-error`);
        
        if (!validator || !element || !errorContainer) {
            return true;
        }
        
        const value = element.type === 'checkbox' ? element.checked : element.value;
        const errors = validator.validate(value);
        
        const fieldContainer = element.closest('.dynamic-form-field');
        
        if (errors.length > 0) {
            errorContainer.textContent = errors[0];
            fieldContainer.classList.add('has-error');
            return false;
        } else {
            errorContainer.textContent = '';
            fieldContainer.classList.remove('has-error');
            return true;
        }
    }
    
    /**
     * Проверяет всю форму
     * @returns {boolean} - Результат проверки
     */
    validateForm() {
        let isValid = true;
        
        for (const fieldName in this.validators) {
            const isFieldValid = this.validateField(fieldName);
            isValid = isValid && isFieldValid;
        }
        
        return isValid;
    }
    
    /**
     * Обработчик отправки формы
     * @param {Event} event - Событие отправки формы
     */
    handleSubmit(event) {
        event.preventDefault();
        
        if (!this.validateForm()) {
            return;
        }
        
        const formData = new FormData(this.formElement);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Дополнительно обрабатываем чекбоксы (они не попадают в FormData, если не отмечены)
        this.config.fields.forEach(field => {
            if (field.field_type === 'checkbox' && !formData.has(field.name)) {
                data[field.name] = false;
            }
        });
        
        // Вызываем callback с данными формы
        if (typeof this.config.onSubmit === 'function') {
            this.config.onSubmit(data);
        }
    }
    
    /**
     * Обработчик отмены формы
     */
    handleCancel() {
        if (typeof this.config.onCancel === 'function') {
            this.config.onCancel();
        }
    }
    
    /**
     * Устанавливает значения полей формы
     * @param {Object} values - Объект со значениями полей
     */
    setValues(values) {
        this.values = values || {};
        this.render();
        this.setupValidation();
    }
    
    /**
     * Получает текущие значения полей формы
     * @returns {Object} - Объект со значениями полей
     */
    getValues() {
        const data = {};
        
        for (const fieldName in this.elements) {
            const element = this.elements[fieldName];
            data[fieldName] = element.type === 'checkbox' ? element.checked : element.value;
        }
        
        return data;
    }
}

// Инициализация формы
function initDynamicForm(containerId, configUrl, defaultValues = null) {
    fetch(configUrl)
        .then(response => response.json())
        .then(config => {
            // Добавляем обработчики событий
            config.onSubmit = function(data) {
                console.log('Form submitted:', data);
                showNotification('Форма успешно отправлена', 'success');
                
                // Здесь будет отправка данных на сервер
                // submitFormData(data, formSubmitUrl);
            };
            
            config.onCancel = function() {
                console.log('Form cancelled');
                if (confirm('Вы уверены, что хотите отменить заполнение формы?')) {
                    // Действия при отмене формы
                    window.history.back();
                }
            };
            
            // Создаем экземпляр формы
            const form = new DynamicForm(containerId, config, defaultValues);
            window.currentForm = form; // Сохраняем ссылку на форму для доступа из других скриптов
        })
        .catch(error => {
            console.error('Error loading form configuration:', error);
            showNotification('Ошибка загрузки конфигурации формы', 'danger');
        });
}

// Вспомогательная функция для отображения уведомлений
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

// Создание контейнера для уведомлений
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alertContainer';
    container.className = 'alert-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Инициализация навигации ситуационного центра для мобильных устройств
function initSituationCenterNavigation() {
    const centerElement = document.querySelector('.situation-center');
    if (!centerElement) return;
    
    // Добавляем навигацию для мобильных устройств
    if (window.innerWidth <= 767) {
        const mobileNav = document.createElement('div');
        mobileNav.className = 'mobile-nav';
        
        const panels = ['left', 'main', 'right'];
        
        panels.forEach(panel => {
            const btn = document.createElement('div');
            btn.className = 'mobile-nav-btn';
            btn.setAttribute('data-panel', panel);
            btn.textContent = panel === 'left' ? 'Список' : (panel === 'main' ? 'Основное' : 'Детали');
            
            btn.addEventListener('click', () => {
                // Прокрутка к выбранной панели
                const panelElement = centerElement.querySelector(`.situation-panel-${panel}`);
                if (panelElement) {
                    panelElement.scrollIntoView({ behavior: 'smooth' });
                }
                
                // Установка активной кнопки
                document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
            
            mobileNav.appendChild(btn);
        });
        
        // Активируем первую кнопку
        mobileNav.querySelector('.mobile-nav-btn').classList.add('active');
        
        centerElement.parentNode.appendChild(mobileNav);
    }
    
    // Обработка переключения панелей для планшетов
    if (window.innerWidth > 767 && window.innerWidth < 1200) {
        const backBtn = document.createElement('button');
        backBtn.className = 'btn btn-outline-secondary mb-3 back-to-main-btn';
        backBtn.textContent = 'Назад';
        backBtn.style.display = 'none';
        
        backBtn.addEventListener('click', () => {
            centerElement.classList.remove('show-left', 'show-right');
            backBtn.style.display = 'none';
        });
        
        centerElement.parentNode.insertBefore(backBtn, centerElement);
        
        // Обработчики для переключения на левую или правую панель
        document.querySelectorAll('[data-show-panel]').forEach(el => {
            el.addEventListener('click', () => {
                const panel = el.getAttribute('data-show-panel');
                centerElement.classList.remove('show-left', 'show-right');
                centerElement.classList.add(`show-${panel}`);
                backBtn.style.display = 'block';
            });
        });
    }
} 