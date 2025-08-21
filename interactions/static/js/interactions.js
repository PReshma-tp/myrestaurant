document.addEventListener('DOMContentLoaded', function() {
    async function sendAjaxRequest(form) {
        const url = form.action;
        const formData = new FormData(form);

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            throw error;
        }
    }

    async function handleFormSubmit(event) {
        event.preventDefault();

        const form = event.target;
        const button = form.querySelector('button[type="submit"]');

        try {
            const data = await sendAjaxRequest(form);
            if (data.status === 'success') {
                updateUI(form, button, data);
            }
        } catch (error) {
            console.error('Action failed:', error);
        }
    }

    function updateUI(form, button, data) {
        if (form.action.includes('toggle_bookmark')) {
            updateBookmarkUI(button, data.is_bookmarked);
        } else if (form.action.includes('toggle_visited')) {
            updateVisitedUI(button, data.is_visited);
        }
    }

    function updateBookmarkUI(button, isBookmarked) {
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.toggle('bi-bookmark-fill', isBookmarked);
            icon.classList.toggle('bi-bookmark', !isBookmarked);
            icon.classList.toggle('text-primary', isBookmarked);
            icon.classList.toggle('text-secondary', !isBookmarked);
        } else {
            button.textContent = isBookmarked ? 'Bookmarked' : 'Bookmark';
            button.classList.toggle('btn-primary', isBookmarked);
            button.classList.toggle('btn-outline-primary', !isBookmarked);
        }
    }

    function updateVisitedUI(button, isVisited) {
        console.log('updateVisited UI function called')
        button.textContent = isVisited ? 'Visited' : 'Mark as Visited';
        button.classList.toggle('btn-success', isVisited);
        button.classList.toggle('btn-outline-secondary', !isVisited);
    }

    document.querySelectorAll('form[action*="toggle"]').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
});
