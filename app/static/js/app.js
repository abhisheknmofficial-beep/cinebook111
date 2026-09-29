/**
 * CineBook Frontend Application Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // City selection helper
    const citySelector = document.getElementById('city-selector');
    if (citySelector) {
        citySelector.addEventListener('change', (e) => {
            const city = e.target.value;
            const url = new URL(window.location.href);
            if (city) {
                url.searchParams.set('city', city);
            } else {
                url.searchParams.delete('city');
            }
            window.location.href = url.toString();
        });
    }

    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(al => {
        setTimeout(() => {
            al.style.opacity = '0';
            al.style.transition = 'opacity 0.5s ease';
            setTimeout(() => al.remove(), 500);
        }, 5000);
    });
});

/**
 * Auto-populates credentials in the login page
 */
function fillDemoCredentials(email, password) {
    const emailInput = document.getElementById('email');
    const pwdInput = document.getElementById('password');
    if (emailInput && pwdInput) {
        emailInput.value = email;
        pwdInput.value = password;
    }
}

/**
 * Submits user login via API
 */
async function handleLoginSubmit(event) {
    event.preventDefault();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const errorBox = document.getElementById('login-error');

    if (errorBox) errorBox.style.display = 'none';

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();

        if (!res.ok) {
            if (errorBox) {
                errorBox.innerText = data.detail || 'Login failed. Please check credentials.';
                errorBox.style.display = 'block';
            }
            return;
        }

        // Token is stored in HTTP-only cookie by backend, also save in localStorage for API usage
        localStorage.setItem('cinebook_token', data.access_token);
        localStorage.setItem('cinebook_user', JSON.stringify(data.user));

        // Redirect to intended page or home
        const urlParams = new URLSearchParams(window.location.search);
        const nextUrl = urlParams.get('next') || (data.user.role === 'ADMIN' ? '/admin' : '/');
        window.location.href = nextUrl;
    } catch (err) {
        if (errorBox) {
            errorBox.innerText = 'Network error. Please try again.';
            errorBox.style.display = 'block';
        }
    }
}

/**
 * Submits user registration via API
 */
async function handleRegisterSubmit(event) {
    event.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const confirm_password = document.getElementById('confirm_password').value;
    const errorBox = document.getElementById('register-error');

    if (errorBox) errorBox.style.display = 'none';

    if (password !== confirm_password) {
        if (errorBox) {
            errorBox.innerText = 'Passwords do not match.';
            errorBox.style.display = 'block';
        }
        return;
    }

    try {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, password, confirm_password })
        });
        const data = await res.json();

        if (!res.ok) {
            if (errorBox) {
                errorBox.innerText = data.detail || 'Registration failed.';
                errorBox.style.display = 'block';
            }
            return;
        }

        localStorage.setItem('cinebook_token', data.access_token);
        localStorage.setItem('cinebook_user', JSON.stringify(data.user));
        window.location.href = '/';
    } catch (err) {
        if (errorBox) {
            errorBox.innerText = 'Network error. Please try again.';
            errorBox.style.display = 'block';
        }
    }
}

/**
 * User booking cancellation
 */
async function cancelBooking(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking? This will release your seats.')) {
        return;
    }

    try {
        const res = await fetch(`/api/bookings/${bookingId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (res.ok) {
            alert('Booking cancelled successfully.');
            window.location.reload();
        } else {
            alert(data.detail || 'Failed to cancel booking.');
        }
    } catch (err) {
        alert('Network error while cancelling booking.');
    }
}
