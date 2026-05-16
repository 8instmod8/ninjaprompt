// =============================================
// main.js — Ninja Prompts (финальная стабильная версия 2026)
// =============================================

function getCookie(name) {
    let value = null;
    if (document.cookie) {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                value = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return value;
}

// ====================== БУРГЕР МЕНЮ ======================
function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    const icon = document.getElementById('burger-icon');
    if (!btn || !menu || !icon) return;

    btn.addEventListener('click', () => {
        const isOpen = menu.classList.toggle('open');
        btn.setAttribute('aria-expanded', isOpen);
        icon.classList.toggle('fa-bars', !isOpen);
        icon.classList.toggle('fa-xmark', isOpen);
    });

    menu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            menu.classList.remove('open');
            icon.classList.remove('fa-xmark');
            icon.classList.add('fa-bars');
            btn.setAttribute('aria-expanded', 'false');
        });
    });
}

// ====================== КОПИРОВАНИЕ ПРОМПТОВ (EVENT DELEGATION) ======================
function handleCopy(button) {
    const itemId = button.dataset.id;
    const type = button.dataset.type || 'content'; // content или video
    const originalText = button.innerHTML;

    if (button.disabled) return;

    button.disabled = true;
    button.innerHTML = 'Копируем...';

    const url = type === 'video' 
        ? `/api/copy-video/${itemId}/` 
        : `/api/copy/${itemId}/`;

    (async () => {
        try {
            const csrfToken = getCookie('csrftoken') ||
                document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

            const res = await fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                credentials: 'same-origin'
            });

            const data = await res.json();

            if (!data.success || !data.text) throw new Error('No text');

            await navigator.clipboard.writeText(data.text);

            button.innerHTML = 'Скопировано!';
            button.style.backgroundColor = '#22c55e';

            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.backgroundColor = '#111';
                button.disabled = false;
            }, 1600);

        } catch (e) {
            console.error('[NinjaPrompt] Copy error:', e);
            button.innerHTML = 'Ошибка';
            button.style.backgroundColor = '#ef4444';

            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.backgroundColor = '#111';
                button.disabled = false;
            }, 2400);
        }
    })();
}



// Инициализация делегирования (вызывается один раз)
function initCopyButtons() {
    if (window._copyDelegateInitialized) return;
    window._copyDelegateInitialized = true;

    document.addEventListener('click', (e) => {
        const button = e.target.closest('.copy-btn');
        if (button) {
            e.preventDefault();
            handleCopy(button);
        }
    }, { passive: false });
}

// ====================== ЗАЩИТА ОТ СКРИНШОТОВ ======================
let screenshotWarning = false;

function triggerScreenshotProtection() {
    if (screenshotWarning) return;
    screenshotWarning = true;

    document.body.classList.add('screenshot-detected');

    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.96); color: white; z-index: 99999;
        display: flex; align-items: center; justify-content: center;
        text-align: center; flex-direction: column; font-family: inherit;
    `;
    overlay.innerHTML = `
        <h1 style="font-size: 42px; margin: 0 0 20px 0;">Запрещено</h1>
        <p style="font-size: 20px; max-width: 620px;">
            Любое копирование контента запрещено.
        </p>
        <button onclick="this.parentElement.remove(); document.body.classList.remove('screenshot-detected');"
                style="margin-top: 30px; padding: 16px 48px; font-size: 18px; background: #e11d48; color: white; border: none; border-radius: 12px; cursor: pointer;">
            Понятно
        </button>
    `;
    document.body.appendChild(overlay);

    setTimeout(() => {
        screenshotWarning = false;
        document.body.classList.remove('screenshot-detected');
    }, 7000);
}

document.addEventListener('keydown', e => {
    if (e.key === 'PrintScreen' ||
        (e.ctrlKey && e.key.toLowerCase() === 's') ||
        (e.metaKey && e.key.toLowerCase() === 's')) {
        e.preventDefault();
        triggerScreenshotProtection();
    }
});

document.addEventListener('contextmenu', e => {
    if (e.target.closest('.card')) {
        e.preventDefault();
        triggerScreenshotProtection();
    }
});

// ====================== COMPARISON SLIDER (До/После) ======================
function initComparisonSliders(container = document) {
    container.querySelectorAll('.comparison-slider').forEach(slider => {
        const divider = slider.querySelector('.divider');
        const before = slider.querySelector('.before-img');
        if (!divider || !before) return;

        let isDragging = false;

        function move(clientX) {
            const rect = slider.getBoundingClientRect();
            let percent = ((clientX - rect.left) / rect.width) * 100;
            percent = Math.max(5, Math.min(95, percent));
            divider.style.left = percent + '%';
            before.style.clipPath = `polygon(0 0, ${percent}% 0, ${percent}% 100%, 0 100%)`;
        }

        divider.addEventListener('mousedown', () => isDragging = true);
        document.addEventListener('mouseup', () => isDragging = false);
        document.addEventListener('mousemove', e => isDragging && move(e.clientX));

        divider.addEventListener('touchstart', () => isDragging = true);
        document.addEventListener('touchend', () => isDragging = false);
        document.addEventListener('touchmove', e => isDragging && move(e.touches[0].clientX));

        // Начальная позиция 50%
        setTimeout(() => move(slider.getBoundingClientRect().left + slider.offsetWidth / 2), 100);
    });
}

// ====================== UGC SWIPER ======================
function initUgcSwipers(container = document) {
    container.querySelectorAll('.ugc-swiper').forEach(swiperEl => {
        if (swiperEl.swiper) return; // уже инициализирован

        new Swiper(swiperEl, {
            loop: true,
            speed: 600,
            pagination: {
                el: swiperEl.querySelector('.swiper-pagination'),
                clickable: true,
            },
            navigation: {
                nextEl: swiperEl.querySelector('.swiper-button-next'),
                prevEl: swiperEl.querySelector('.swiper-button-prev'),
            },
            lazy: true,
            preloadImages: false,
            watchSlidesProgress: true,
        });
    });
}

// ====================== FALLBACK КНОПКА ======================
function initLoadMoreFallback() {
    const btn = document.getElementById('load-more-btn');
    if (!btn) return;

    setTimeout(() => {
        const hasTrigger = document.querySelector('.infinite-scroll-trigger');
        if (hasTrigger && btn.style.display === 'none') {
            btn.style.display = 'block';
        }
    }, 4000);
}

// ====================== ГЛАВНАЯ ИНИЦИАЛИЗАЦИЯ ======================
document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initCopyButtons();           
    initComparisonSliders();
    initUgcSwipers();
    initLoadMoreFallback();

    const btn = document.getElementById('load-more-btn');
    if (btn && !document.querySelector('.infinite-scroll-trigger')) {
        btn.style.display = 'none';
    }

    console.log('%c[NinjaPrompt] Инициализация завершена (с event delegation)', 'color:#22c55e');
});

// Обработка после HTMX 
document.body.addEventListener('htmx:afterSwap', (event) => {
    if (event.detail.target.id === 'cards-grid') {
        const btn = document.getElementById('load-more-btn');
        if (btn) {
            const hasTrigger = event.detail.target.querySelector('.infinite-scroll-trigger');
            if (!hasTrigger) btn.style.display = 'none';
        }

        initComparisonSliders(event.detail.target);
        initUgcSwipers(event.detail.target);
    }
});
