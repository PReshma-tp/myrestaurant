document.addEventListener('DOMContentLoaded', function() {

    function initStarRating(container = document) {
        const starContainer = container.querySelector('#star-rating-container');
        if (!starContainer) return;

        const ratingInput = container.querySelector('#id_rating');

        function updateStars(rating) {
            starContainer.querySelectorAll('i').forEach(star => {
                const starRating = parseInt(star.getAttribute('data-rating'), 10);
                star.classList.toggle('bi-star-fill', starRating <= rating);
                star.classList.toggle('text-warning', starRating <= rating);
                star.classList.toggle('bi-star', starRating > rating);
                star.classList.toggle('text-secondary', starRating > rating);
            });
        }

        const initialRating = parseInt(starContainer.getAttribute('data-initial-rating'), 10);
        if (!isNaN(initialRating)) {
            updateStars(initialRating);
            if (ratingInput) ratingInput.value = initialRating;
        }

        starContainer.addEventListener('click', function(event) {
            const star = event.target.closest('i');
            if (!star || !ratingInput) return;

            const newRating = parseInt(star.getAttribute('data-rating'), 10);
            ratingInput.value = newRating;
            updateStars(newRating);
        });
    }

    initStarRating();

    document.body.addEventListener('submit', async (e) => {
        const reviewForm = e.target.closest('#review-form');
        if (!reviewForm) return;

        e.preventDefault();

        const formData = new FormData(reviewForm);
        const csrfToken = reviewForm.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch(reviewForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const data = await response.json();
            const reviewsSection = document.querySelector('.reviews-section');
            if (reviewsSection) {
                reviewsSection.innerHTML = data.html;
                initStarRating(reviewsSection);
            }

        } catch (error) {
            console.error('Error submitting review:', error);
        }
    });

});
