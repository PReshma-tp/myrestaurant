import { showToast } from './toast.js';

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
        const interactionType = form.dataset.interactionType;

        try {
            const data = await sendAjaxRequest(form);
            if (data.status === 'success') {
                updateUI(interactionType, button, data);
            }
            else{
                showToast("Action failed. Please try again.", "warning");
            }
        } catch (error) {
            showToast("Network error. Please try again.", "danger");
        }
    }

    function updateUI(interactionType, button, data) {
        if (interactionType === 'bookmark') {
            updateBookmarkUI(button, data.is_bookmarked);
        } else if (interactionType === 'visited') {
            updateVisitedUI(button, data.is_visited);
        }
    }

    function updateBookmarkUI(button, isBookmarked) {
        const restaurantId = button.closest('form').dataset.restaurantId;
        const allButtons = document.querySelectorAll(
            `form[data-restaurant-id="${restaurantId}"][data-interaction-type="bookmark"] button`
        );

        allButtons.forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-bookmark-fill', isBookmarked);
                icon.classList.toggle('bi-bookmark', !isBookmarked);
                icon.classList.toggle('text-primary', isBookmarked);
                icon.classList.toggle('text-secondary', !isBookmarked);
            } else {
                btn.textContent = isBookmarked ? 'Bookmarked' : 'Bookmark';
                btn.classList.toggle('btn-primary', isBookmarked);
                btn.classList.toggle('btn-outline-primary', !isBookmarked);
            }
        });
    }

    function updateVisitedUI(button, isVisited) {
        button.textContent = isVisited ? 'Visited' : 'Mark as Visited';
        button.classList.toggle('btn-success', isVisited);
        button.classList.toggle('btn-outline-secondary', !isVisited);
    }

    document.querySelectorAll('form[action*="toggle"]').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
});
