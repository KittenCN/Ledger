(function() {
    const STORAGE_KEY = 'ledgerActivated';
    const query = new URLSearchParams(window.location.search);
    const activated = query.get('activated');

    if (activated !== null) {
        localStorage.setItem(STORAGE_KEY, activated === '1' ? 'true' : 'false');
    }

    function showDemoOverlay() {
        if (localStorage.getItem(STORAGE_KEY) === 'true') {
            return;
        }

        if (document.getElementById('activation-demo-overlay')) {
            return;
        }

        const overlay = document.createElement('div');
        overlay.id = 'activation-demo-overlay';
        overlay.textContent = 'DEMO';
        Object.assign(overlay.style, {
            position: 'fixed',
            inset: '0',
            zIndex: '2147483647',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: 'none',
            background: 'rgba(255, 0, 0, 0.16)',
            color: 'rgba(255, 0, 0, 0.42)',
            fontSize: 'min(36vw, 280px)',
            fontWeight: '900',
            letterSpacing: '0',
            lineHeight: '1',
            transform: 'rotate(-24deg)',
            userSelect: 'none'
        });

        document.body.appendChild(overlay);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', showDemoOverlay);
    } else {
        showDemoOverlay();
    }
})();
