document.addEventListener('DOMContentLoaded', function() {
    function initStarRating() {
        const starContainer = document.getElementById('star-rating-container');
        if (!starContainer) return;

        const ratingInput = document.getElementById('id_rating');

        function updateStars(rating) {
            starContainer.querySelectorAll('i').forEach(star => {
                const starRating = parseInt(star.getAttribute('data-rating'));
                if (starRating <= rating) {
                    star.classList.remove('bi-star', 'text-secondary');
                    star.classList.add('bi-star-fill', 'text-warning');
                } else {
                    star.classList.remove('bi-star-fill', 'text-warning');
                    star.classList.add('bi-star', 'text-secondary');
                }
            });
        }

        const initialRating = parseInt(starContainer.getAttribute('data-initial-rating'));
        if (!isNaN(initialRating)) {
            updateStars(initialRating);
            if (ratingInput) {
                ratingInput.value = initialRating;
            }
        }

        starContainer.addEventListener('click', function(event) {
            const star = event.target.closest('i');
            if (star) {
                const newRating = parseInt(star.getAttribute('data-rating'));
                if (ratingInput) {
                    ratingInput.value = newRating;
                }
                updateStars(newRating);
            }
        });
    }

    function initReviewForm() {
        const reviewForm = document.getElementById("review-form");
        if (!reviewForm) return;

        reviewForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(reviewForm);
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

            try {
                const response = await fetch(reviewForm.action, {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest"
                    }
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                const data = await response.json();
                document.querySelector(".reviews-section").innerHTML = data.html;
                initStarRating();
                initReviewForm();
            } catch (error) {
                console.error("Error submitting review:", error);
            }
        });
    }

    initStarRating();
    initReviewForm();
});
