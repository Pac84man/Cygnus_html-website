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

    // This is your actual reCAPTCHA Site Key
    const recaptchaSiteKey = '6LctiewrAAAAALn-KJfqW-0XICvX4NAiRUqSWMSS';

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

                    // --- THIS IS THE UPDATED FETCH BLOCK ---
                    fetch('/api/contact', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data),
                    })
                    .then(response => {
                        // If the server returns an error, handle it
                        if (!response.ok) {
                            // We need to parse the JSON body of the error response
                            return response.json().then(err => {
                                // Dig into the response to find the real message from FastAPI
                                if (err.detail && Array.isArray(err.detail) && err.detail[0]) {
                                    throw new Error(err.detail[0].msg);
                                }
                                // Fallback for other types of errors
                                throw new Error(err.detail || 'An unexpected error occurred.');
                            });
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
                        // Display the clean, human-readable error message
                        formStatus.textContent = error.message;
                        formStatus.classList.add('text-red-600');
                    })
                    .finally(() => {
                        // No matter what, re-enable the button so the user can try again
                        submitButton.disabled = false;
                        submitButton.textContent = 'Send Inquiry';
                    });
                    // --- END OF UPDATED FETCH BLOCK ---
                });
            });
        });
    }
});