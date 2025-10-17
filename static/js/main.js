// static/js/main.js

// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    // This initializes our animations. We keep this code.
    AOS.init({
        once: true,
        offset: 50,
        delay: 100,
        duration: 800,
        easing: 'ease-in-out',
    });

    // --- New Contact Form Logic ---
    const contactForm = document.getElementById('contact-form');
    const formStatus = document.getElementById('form-status');
    const submitButton = document.getElementById('submit-button');

    // IMPORTANT: Replace this placeholder with your actual Google reCAPTCHA Site Key
    const recaptchaSiteKey = 'YOUR_RECAPTCHA_SITE_KEY_HERE';

    // We only run the form logic if the form element actually exists on the page
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            // Prevent the browser's default form submission behavior
            event.preventDefault();

            // Give the user visual feedback that something is happening
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';
            formStatus.textContent = '';
            formStatus.className = 'mt-6 text-center text-lg'; // Reset classes

            // Use the reCAPTCHA library to get a security token
            grecaptcha.ready(function() {
                grecaptcha.execute(recaptchaSiteKey, { action: 'submit' }).then(function(token) {

                    // Gather all the data from our form
                    const formData = new FormData(contactForm);
                    const data = Object.fromEntries(formData.entries());
                    data.recaptcha_token = token; // Add the token to our data payload

                    // Send the data to our backend API endpoint
                    fetch('/api/contact', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data),
                    })
                    .then(response => {
                        // If the server returns an error, handle it
                        if (!response.ok) {
                            return response.json().then(err => { throw new Error(err.detail || 'Something went wrong.') });
                        }
                        // Otherwise, process the successful response
                        return response.json();
                    })
                    .then(result => {
                        // Display the success message from the server
                        formStatus.textContent = result.message;
                        formStatus.classList.add('text-green-600');
                        contactForm.reset(); // Clear the form fields
                    })
                    .catch(error => {
                        // Display any errors to the user
                        formStatus.textContent = error.message;
                        formStatus.classList.add('text-red-600');
                    })
                    .finally(() => {
                        // No matter what, re-enable the button so the user can try again
                        submitButton.disabled = false;
                        submitButton.textContent = 'Send Inquiry';
                    });
                });
            });
        });
    }
});