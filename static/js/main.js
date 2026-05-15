// =============================================
// main.js — Ninja Prompts (полная стабильная версия)
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

// ====================== КОПИРОВАНИЕ ПРОМПТОВ (финальная версия 2026, без data-text) ======================
function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const itemId = this.dataset.id;
            const originalText = this.innerHTML;

            this.disabled = true;
            this.innerHTML = 'Копируем...';

            let success = false;

            try {
                const csrfToken = getCookie('csrftoken') || 
                    document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

                // === ГЛАВНЫЙ ФИКС ДЛЯ iOS SAFARI ===
                if (navigator.clipboard && navigator.clipboard.write) {
                    await navigator.clipboard.write([
                        new ClipboardItem({
                            "text/plain": fetch(`/api/copy/${itemId}/`, {
                                method: 'POST',
                                headers: { 'X-CSRFToken': csrfToken },
                                credentials: 'same-origin'
                            })
                            .then(res => {
                                if (!res.ok) throw new Error('Server error');
                                return res.json();
                            })
                            .then(data => {
                                if (!data.success || !data.text) throw new Error('No text');
                                return new Blob([data.text], { type: "text/plain" });
                            })
                        })
                    ]);
                    success = true;
                } 
                else {
                    // Fallback для совсем старых браузеров (редко в 2026)
                    const res = await fetch(`/api/copy/${itemId}/`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': csrfToken },
                        credentials: 'same-origin'
                    });
                    const data = await res.json();
                    if (!data.success || !data.text) throw new Error('No text');

                    const ta = document.createElement('textarea');
                    ta.value = data.text;
                    ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0';
                    document.body.appendChild(ta);
                    ta.focus();
                    ta.select();
                    success = document.execCommand('copy');
                    document.body.removeChild(ta);
                }

            } catch (e) {
                console.error('[NinjaPrompt] Copy error:', e);
            }

            if (success) {
                this.innerHTML = 'Скопировано!';
                this.style.backgroundColor = '#22c55e';
            } else {
                this.innerHTML = 'Ошибка';
                this.style.backgroundColor = '#ef4444';
            }

            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.backgroundColor = '#111';
                this.disabled = false;
            }, success ? 1600 : 2400);
        });
    });
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

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.comparison-slider').forEach(slider => {
        const divider = slider.querySelector('.divider');
        const before = slider.querySelector('.before-img');
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
});

// Fallback: показать кнопку через 4 секунды
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('load-more-btn');
    if (!btn) return;

    setTimeout(() => {
        if (getComputedStyle(btn).display === 'none') {
            btn.style.display = 'block';
        }
    }, 4000);
});

// ====================== ИНИЦИАЛИЗАЦИЯ ======================
document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initCopyButtons();
    console.log('%c[NinjaPrompt] Инициализация завершена', 'color:#22c55e');
});
