// =============================================
// main.js — Ninja Prompts (обновлённая версия)
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

// ====================== АВТОМАТИЧЕСКОЕ КОПИРОВАНИЕ ======================
function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const itemId = this.dataset.id;
            const originalText = this.innerHTML;

            this.disabled = true;
            this.innerHTML = 'Копируем...';

            try {
                const res = await fetch(`/api/copy/${itemId}/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCookie('csrftoken') },
                    credentials: 'same-origin'
                });

                const data = await res.json();

                if (data.success && data.text) {
                    await navigator.clipboard.writeText(data.text);
                    this.innerHTML = '✅ Скопировано!';
                    this.style.backgroundColor = '#22c55e';

                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.style.backgroundColor = '#111';
                        this.disabled = false;
                    }, 1800);
                } else {
                    throw new Error(data.error || 'Ошибка');
                }
            } catch (e) {
                console.error(e);
                this.innerHTML = '❌ Ошибка';
                this.style.backgroundColor = '#ef4444';

                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.style.backgroundColor = '#111';
                    this.disabled = false;
                }, 2000);
            }
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

// Глобальные обработчики
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

// ====================== ИНИЦИАЛИЗАЦИЯ ======================
document.addEventListener('DOMContentLoaded', () => {
    initCopyButtons();
    console.log('%cNinja Prompts — JS инициализирован', 'color: #2563eb; font-weight: 600');
});
