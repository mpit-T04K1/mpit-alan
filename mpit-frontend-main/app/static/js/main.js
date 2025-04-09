/**
 * Основной JavaScript-файл для Qwerty.town
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Qwerty.town - Бизнес-модуль загружен');
    
    // Установка текущего года в футере
    setCurrentYear();
    
    // Активация всех подсказок Bootstrap
    activateTooltips();
    
    // Добавление эффекта для карточек
    animateCards();
    
    // Инициализация модуля карты
    initMapModule();
    
    // Обработчик для выпадающих меню
    const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            // Получаем соответствующее дропдаун-меню
            const dropdownMenu = this.nextElementSibling;
            if (!dropdownMenu) return;
            
            // Устанавливаем правильные стили при открытии
            setTimeout(() => {
                if (dropdownMenu.classList.contains('show')) {
                    dropdownMenu.style.zIndex = '9999';
                    dropdownMenu.style.position = 'absolute';
                    
                    // Проверяем, не выходит ли меню за пределы экрана
                    const menuRect = dropdownMenu.getBoundingClientRect();
                    const windowWidth = window.innerWidth;
                    
                    if (menuRect.right > windowWidth) {
                        dropdownMenu.style.left = 'auto';
                        dropdownMenu.style.right = '0';
                    }
                }
            }, 0);
        });
    });
    
    // Инициализация всех тултипов
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length) {
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Инициализация всех поповеров
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (popoverTriggerList.length) {
        [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
    }
    
    // Обработчик для нажатий на кнопки с выпадающими меню
    document.addEventListener('click', function(event) {
        // Найдем все открытые выпадающие меню
        const openMenus = document.querySelectorAll('.dropdown-menu.show');
        
        if (openMenus.length) {
            openMenus.forEach(menu => {
                // Проверим, был ли клик внутри выпадающего меню или по переключателю
                const toggle = menu.previousElementSibling;
                if (!menu.contains(event.target) && !toggle.contains(event.target)) {
                    const dropdownInstance = bootstrap.Dropdown.getInstance(toggle);
                    if (dropdownInstance) {
                        dropdownInstance.hide();
                    }
                }
            });
        }
    });
});

/**
 * Установка текущего года в футере
 */
function setCurrentYear() {
    const year = new Date().getFullYear();
    const yearElements = document.querySelectorAll('.current-year');
    yearElements.forEach(el => {
        el.textContent = year;
    });
}

/**
 * Активация подсказок Bootstrap
 */
function activateTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Добавление анимации для карточек
 */
function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

/**
 * Отправка AJAX-запроса
 * @param {string} url - URL для запроса
 * @param {string} method - Метод запроса (GET, POST, PUT, DELETE)
 * @param {Object} data - Данные для отправки
 * @param {Function} callback - Функция обратного вызова
 */
function sendRequest(url, method, data, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');
    
    xhr.onload = function() {
        if (this.status >= 200 && this.status < 300) {
            callback(null, JSON.parse(this.responseText));
        } else {
            callback(new Error(`${this.status}: ${this.statusText}`), null);
        }
    };
    
    xhr.onerror = function() {
        callback(new Error('Ошибка сети'), null);
    };
    
    xhr.send(data ? JSON.stringify(data) : null);
}

/**
 * Отображение уведомления
 * @param {string} message - Сообщение для отображения
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Длительность отображения в мс
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fade-in`;
    notification.textContent = message;
    
    const container = document.querySelector('.notification-container');
    if (!container) {
        const newContainer = document.createElement('div');
        newContainer.className = 'notification-container';
        document.body.appendChild(newContainer);
        newContainer.appendChild(notification);
    } else {
        container.appendChild(notification);
    }
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Инициализация модуля карты
 */
function initMapModule() {
    // Находим кнопку активации модуля карты
    const mapButton = document.querySelector('.activate-map-module');
    
    if (mapButton) {
        mapButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Создаем модальное окно для карты
            createMapModal();
            
            // Загружаем и инициализируем карту
            loadYandexMapsScript().then(() => {
                initializeYandexMap();
            }).catch(error => {
                console.error('Ошибка при загрузке Яндекс.Карт:', error);
                showNotification('Не удалось загрузить карту. Пожалуйста, попробуйте позже.', 'error');
            });
        });
    }
}

/**
 * Создание модального окна для карты
 */
function createMapModal() {
    // Проверяем, существует ли уже модальное окно
    let mapModal = document.getElementById('mapModal');
    
    if (!mapModal) {
        // Создаем элементы модального окна
        mapModal = document.createElement('div');
        mapModal.className = 'modal fade';
        mapModal.id = 'mapModal';
        mapModal.tabIndex = '-1';
        mapModal.setAttribute('aria-labelledby', 'mapModalLabel');
        mapModal.setAttribute('aria-hidden', 'true');
        
        mapModal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="mapModalLabel">Карта компаний</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Закрыть"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-3">
                                <div class="map-filter-container">
                                    <h5 class="mb-3">Фильтры</h5>
                                    
                                    <div class="mb-3">
                                        <label for="business-type-filter" class="form-label">Тип бизнеса</label>
                                        <select class="form-select" id="business-type-filter">
                                            <option value="">Все типы</option>
                                        </select>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="city-filter" class="form-label">Город</label>
                                        <select class="form-select" id="city-filter">
                                            <option value="">Все города</option>
                                        </select>
                                    </div>
                                    
                                    <div class="mb-4">
                                        <label for="search-filter" class="form-label">Поиск по названию</label>
                                        <input type="text" class="form-control" id="search-filter" placeholder="Введите название компании">
                                    </div>
                                    
                                    <button id="apply-filters" class="btn btn-primary w-100">Применить</button>
                                    <button id="reset-filters" class="btn btn-outline-secondary w-100 mt-2">Сбросить</button>
                                    
                                    <div class="company-count mt-3">
                                        Найдено компаний: <span id="company-count">0</span>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-9">
                                <div class="map-container" style="height: 600px;">
                                    <div id="yandexMap" style="width: 100%; height: 100%; border-radius: 8px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Добавляем модальное окно в DOM
        document.body.appendChild(mapModal);
    }
    
    // Показываем модальное окно
    const bsModal = new bootstrap.Modal(mapModal);
    bsModal.show();
}

let center = [54.70805096669561,20.50560278768957]

function init (){
    let map = new ymaps.Map('demo-map' , {
        center: center,
        zoom: 39,
        controls:['routePanelControl']
    });

    // let placemark = new ymaps.Placemark(center,{
    //     balloonContentHeader: 'Хедер',
    //     balloonContentBody: 'боди',
    //     balloonContentFooter: 'футер'
    // },{
    //     iconLayout:'default#image',
    //     iconImageHref: "img/free-icon-map-location-7743571.png",
    //     iconImageSize: [40,40],
    //     iconImageOffset: [-20,-30]
    // });

    let placemark1 = new ymaps.Placemark(center,{
        balloonContent: `
            <div class=balloon>
                <div class="adress"> Мы сюда едем</div>
                <div class="contact">
                    <a href="">AAAAAA</a>
                </div>
            </div>
        `
    },{
        iconLayout:'default#image',
        iconImageHref: "img/free-icon-map-location-7743571.png",
        iconImageSize: [40,40],
        iconImageOffset: [-20,-30]
    });

    let control = map.controls.get('routePanelControl');
    // let location = ymaps.geolocation.get();

    // location.then(function(res){
    //     let locationText = res.geoObjects.get(0).properties.get('text');
    //     console.log(locationText);

    //     control.routePanel.state.set({
    //         type: 'auto',
    //         fromEnabled: true,
    //         from: locationText,
    //         toEnabled: true,
    //         to: center
    //     });
    
    //     control.routePanel.options.set({
    //         types:{
    //             masstransit: true,
    //             pedestrian: true,
    //             auto: true,
    //             taxi: true
    //         }
    //     });
    // });

    const options = {
        enableHighAccuracy: true,
        timeout: 10000,
    };
      
    function success(pos) {
        const crd = pos.coords;
      
        console.log(`Latitude : ${crd.latitude}`);
        console.log(`Longitude: ${crd.longitude}`);

        let reverseGeocoder = ymaps.geocode([crd.latitude, crd.longitude]);
        let locationText = null;

        reverseGeocoder.then(function(res){
            locationText = res.geoObjects.get(0).properties.get('text');

            control.routePanel.state.set({
                type: 'auto',
                fromEnabled: true,
                from: locationText,
                toEnabled: true,
                to: center
            });
        });


        control.routePanel.options.set({
            types:{
                masstransit: true,
                pedestrian: true,
                auto: true,
                taxi: true
            }
        });
    }
      
    function error(err) {
        console.warn(`ERROR(${err.code}): ${err.message}`);
    }
      
    navigator.geolocation.getCurrentPosition(success, error, options);

    

    // map.geoObjects.add(placemark1);
    placemark1.balloon.open();
}

ymaps.ready(init);



/**
 * Загрузка компаний для отображения на карте
 */
function loadCompaniesForMap(objectManager) {
    // Получаем значения фильтров
    const typeFilter = document.getElementById('business-type-filter')?.value || '';
    const cityFilter = document.getElementById('city-filter')?.value || '';
    const searchFilter = document.getElementById('search-filter')?.value || '';
    
    // Формируем URL с параметрами
    let url = '/api/map/locations';
    const params = [];
    
    if (typeFilter) params.push(`type=${encodeURIComponent(typeFilter)}`);
    if (cityFilter) params.push(`city=${encodeURIComponent(cityFilter)}`);
    if (searchFilter) params.push(`search=${encodeURIComponent(searchFilter)}`);
    
    if (params.length > 0) {
        url += '?' + params.join('&');
    }
    
    // Отправляем запрос на получение компаний
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Преобразуем данные в формат для ObjectManager
            const features = [];
            
            data.forEach(company => {
                if (company.latitude && company.longitude) {
                    features.push({
                        type: 'Feature',
                        id: company.id,
                        geometry: {
                            type: 'Point',
                            coordinates: [company.latitude, company.longitude]
                        },
                        properties: {
                            balloonContentHeader: company.name,
                            balloonContentBody: `
                                <p><strong>Тип:</strong> ${company.business_type_display}</p>
                                <p><strong>Адрес:</strong> ${company.address}</p>
                                ${company.phone ? `<p><strong>Телефон:</strong> <a href="tel:${company.phone}">${company.phone}</a></p>` : ''}
                                ${company.email ? `<p><strong>Email:</strong> <a href="mailto:${company.email}">${company.email}</a></p>` : ''}
                                <a href="/business/${company.id}" class="btn btn-primary btn-sm">Подробнее</a>
                            `,
                            clusterCaption: company.name,
                            iconCaption: company.name
                        },
                        options: {
                            preset: getPresetByBusinessType(company.business_type)
                        }
                    });
                }
            });
            
            // Очищаем и добавляем новые объекты
            objectManager.removeAll();
            objectManager.add({
                type: 'FeatureCollection',
                features: features
            });
            
            // Обновляем счетчик компаний
            document.getElementById('company-count').textContent = features.length;
            
            // Масштабируем карту, чтобы видеть все объекты
            if (features.length > 0) {
                const yandexMap = objectManager.getMap();
                yandexMap.setBounds(yandexMap.geoObjects.getBounds(), {
                    checkZoomRange: true,
                    zoomMargin: 30
                });
            }
        })
        .catch(error => {
            console.error('Ошибка при загрузке компаний:', error);
            showNotification('Не удалось загрузить данные компаний', 'error');
        });
}

/**
 * Получение пресета иконки в зависимости от типа бизнеса
 */
function getPresetByBusinessType(type) {
    const presets = {
        'restaurant': 'islands#redFoodIcon',
        'beauty': 'islands#pinkBeautyIcon',
        'medical': 'islands#darkBlueHospitalIcon',
        'fitness': 'islands#greenSportIcon',
        'service': 'islands#orangeAutoIcon',
        'education': 'islands#blueEducationIcon',
        'entertainment': 'islands#violetTheaterIcon',
        'retail': 'islands#yellowShoppingIcon',
        'other': 'islands#blueCircleDotIcon'
    };
    
    return presets[type] || 'islands#blueCircleDotIcon';
}

/**
 * Загрузка городов для фильтра
 */
function loadCitiesForFilter() {
    fetch('/api/map/cities')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('city-filter');
            if (!select) return;
            
            // Очищаем селект, оставляя только первый элемент "Все города"
            select.innerHTML = '<option value="">Все города</option>';
            
            // Добавляем города в селект
            data.forEach(city => {
                const option = document.createElement('option');
                option.value = city.value;
                option.textContent = city.label;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке городов:', error);
        });
}

/**
 * Загрузка типов бизнеса для фильтра
 */
function loadBusinessTypesForFilter() {
    fetch('/api/map/business-types')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('business-type-filter');
            if (!select) return;
            
            // Очищаем селект, оставляя только первый элемент "Все типы"
            select.innerHTML = '<option value="">Все типы</option>';
            
            // Добавляем типы бизнеса в селект
            data.forEach(type => {
                const option = document.createElement('option');
                option.value = type.value;
                option.textContent = type.label;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Ошибка при загрузке типов бизнеса:', error);
        });
}

/**
 * Настройка обработчиков событий для фильтров карты
 */
function setupMapFilters(objectManager) {
    // Кнопка применения фильтров
    const applyButton = document.getElementById('apply-filters');
    if (applyButton) {
        applyButton.addEventListener('click', function() {
            loadCompaniesForMap(objectManager);
        });
    }
    
    // Кнопка сброса фильтров
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            // Сбрасываем значения фильтров
            document.getElementById('business-type-filter').value = '';
            document.getElementById('city-filter').value = '';
            document.getElementById('search-filter').value = '';
            
            // Загружаем компании без фильтров
            loadCompaniesForMap(objectManager);
        });
    }
    
    // Обработка нажатия Enter в поле поиска
    const searchInput = document.getElementById('search-filter');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                loadCompaniesForMap(objectManager);
            }
        });
    }
} 


        /**
         * Базовый класс для модульного интерфейса
         */
        class ModularInterface {
            constructor() {
                this.activeSection = null;
                this.activeInfoSection = null;
                
                // Инициализация обработчиков событий
                this.initNavigation();
                this.initSubmenuToggle();
                this.showDefaultSections();
            }
            
            // Инициализация основной навигации
            initNavigation() {
                const navItems = document.querySelectorAll('.nav-item:not(.has-submenu)');
                
                navItems.forEach(item => {
                    item.addEventListener('click', () => {
                        // Проверяем, есть ли у элемента атрибут data-target
                        if (item.dataset.target) {
                            const targetSection = item.dataset.target;
                            
                            // Если есть атрибут data-item, значит это подпункт меню
                            if (item.dataset.item) {
                                // Обработка подпунктов меню, если необходимо
                            } else {
                                // Переключаем на соответствующую секцию
                                this.switchToSection(targetSection);
                                
                                // Обновляем активный пункт меню
                                navItems.forEach(nav => nav.classList.remove('active'));
                                item.classList.add('active');
                            }
                        }
                    });
                });
            }
            
            // Инициализация переключателей подменю
            initSubmenuToggle() {
                const submenuToggles = document.querySelectorAll('.nav-item.has-submenu');
                
                submenuToggles.forEach(toggle => {
                    toggle.addEventListener('click', () => {
                        // Переключаем класс expanded
                        toggle.classList.toggle('expanded');
                        
                        // Находим следующий элемент (должен быть submenu)
                        const submenu = toggle.nextElementSibling;
                        if (submenu && submenu.classList.contains('submenu')) {
                            if (submenu.style.display === 'block') {
                                submenu.style.display = 'none';
                            } else {
                                submenu.style.display = 'block';
                            }
                        }
                        
                        // Если у переключателя есть атрибут data-target, переключаемся на эту секцию
                        if (toggle.dataset.target) {
                            this.switchToSection(toggle.dataset.target);
                        }
                    });
                });
            }
            
            // Показываем секции по умолчанию при загрузке страницы
            showDefaultSections() {
                // Находим все секции
                const sections = document.querySelectorAll('.section');
                const infoSections = document.querySelectorAll('.info-section');
                
                // Показываем первую секцию
                if (sections.length > 0) {
                    const firstSection = sections[0];
                    this.activeSection = firstSection.id;
                    firstSection.style.display = 'block';
                }
                
                // Показываем первую информационную секцию
                if (infoSections.length > 0) {
                    const firstInfoSection = infoSections[0];
                    this.activeInfoSection = firstInfoSection.id;
                    firstInfoSection.style.display = 'block';
                }
                
                // Устанавливаем активный пункт меню
                const firstNavItem = document.querySelector('.nav-item:not(.has-submenu)');
                if (firstNavItem) {
                    firstNavItem.classList.add('active');
                }
            }
            
            // Переключение на выбранную секцию
            switchToSection(sectionId) {
                // Скрываем все секции
                const sections = document.querySelectorAll('.section');
                sections.forEach(section => {
                    section.style.display = 'none';
                });
                
                // Показываем выбранную секцию
                const targetSection = document.getElementById(`${sectionId}-section`);
                if (targetSection) {
                    targetSection.style.display = 'block';
                    this.activeSection = `${sectionId}-section`;
                    
                    // Вызываем метод для обработки смены секции
                    this.onSectionChange(sectionId);
                }
                
                // Скрываем все информационные секции
                const infoSections = document.querySelectorAll('.info-section');
                infoSections.forEach(section => {
                    section.style.display = 'none';
                });
                
                // Показываем соответствующую информационную секцию
                const targetInfoSection = document.getElementById(`${sectionId}-info`);
                if (targetInfoSection) {
                    targetInfoSection.style.display = 'block';
                    this.activeInfoSection = `${sectionId}-info`;
                }
            }
            
            // Метод для обработки смены секции
            onSectionChange(sectionId) {
                console.log(`Переключение на секцию: ${sectionId}`);
                
                // Показываем/скрываем категории меню
                const menuCategories = document.getElementById('menu-categories');
                if (menuCategories) {
                    menuCategories.style.display = sectionId === 'menu' ? 'block' : 'none';
                }
            }
        }
        
        // Инициализация модульного интерфейса при загрузке страницы
        document.addEventListener('DOMContentLoaded', () => {
            window.modularInterface = new ModularInterface();
        });
