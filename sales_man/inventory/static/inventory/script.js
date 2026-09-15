document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.target;

            tabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');

            panels.forEach(panel => {
                if (panel.id === targetId) {
                    panel.hidden = false;
                    panel.classList.add('active');
                } else {
                    panel.hidden = true;
                    panel.classList.remove('active');
                }
            });
        });
    });
});
