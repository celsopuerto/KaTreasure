document.addEventListener('DOMContentLoaded', () => {
    const adultCountDisplay = document.getElementById('adult-count-display');
    const childrenCountDisplay = document.getElementById('children-count-display');

    document.querySelectorAll('.plus, .minus').forEach(button => {
        button.addEventListener('click', (event) => {
            const buttonType = event.target.dataset.type;
            if (buttonType === 'adult') {
                updateCounter('adult', adultCountDisplay);
            } else if (buttonType === 'children') {
                updateCounter('children', childrenCountDisplay);
            }
        });
    });

    function updateCounter(type, display) {
        const count = parseInt(display.textContent);
        if (event.target.classList.contains('plus')) {
            display.textContent = count + 1;
        } else if (event.target.classList.contains('minus')) {
            if (count > 0) {
                display.textContent = count - 1;
            }
        }
        document.getElementById(`${type}-count`).value = display.textContent;
    }
});

