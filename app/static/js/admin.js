/**
 * CineBook Admin Dashboard Management Scripts
 */

function openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('active');
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove('active');
}

// Close modal on click outside content
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

/**
 * Admin: Create Movie
 */
async function handleCreateMovie(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
        title: form.title.value.trim(),
        genre: form.genre.value.trim(),
        language: form.language.value.trim(),
        duration_mins: parseInt(form.duration_mins.value, 10),
        rating: parseFloat(form.rating.value),
        release_date: form.release_date.value,
        description: form.description.value.trim(),
        poster_url: form.poster_url.value.trim() || null,
        backdrop_url: form.backdrop_url.value.trim() || null,
        is_active: true
    };

    try {
        const res = await fetch('/api/movies', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert('Movie created successfully!');
            window.location.reload();
        } else {
            const err = await res.json();
            alert(err.detail || 'Failed to create movie.');
        }
    } catch (e) {
        alert('Network error while creating movie.');
    }
}

/**
 * Admin: Delete Movie
 */
async function deleteMovie(movieId) {
    if (!confirm('Are you sure you want to delete this movie? This will also remove associated shows.')) return;
    try {
        const res = await fetch(`/api/movies/${movieId}`, { method: 'DELETE' });
        if (res.ok) {
            alert('Movie deleted.');
            window.location.reload();
        } else {
            alert('Failed to delete movie.');
        }
    } catch (e) {
        alert('Error communicating with server.');
    }
}

/**
 * Admin: Create Event
 */
async function handleCreateEvent(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
        title: form.title.value.trim(),
        category: form.category.value.trim(),
        location: form.location.value.trim(),
        event_date: form.event_date.value,
        event_time: form.event_time.value.trim(),
        description: form.description.value.trim(),
        price: parseFloat(form.price.value),
        total_seats: parseInt(form.total_seats.value, 10),
        available_seats: parseInt(form.total_seats.value, 10),
        poster_url: form.poster_url.value.trim() || null,
        is_active: true
    };

    try {
        const res = await fetch('/api/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert('Event created successfully!');
            window.location.reload();
        } else {
            const err = await res.json();
            alert(err.detail || 'Failed to create event.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

/**
 * Admin: Delete Event
 */
async function deleteEvent(eventId) {
    if (!confirm('Delete this event?')) return;
    try {
        const res = await fetch(`/api/events/${eventId}`, { method: 'DELETE' });
        if (res.ok) {
            alert('Event deleted.');
            window.location.reload();
        } else {
            alert('Failed to delete event.');
        }
    } catch (e) {
        alert('Error communicating with server.');
    }
}

/**
 * Admin: Create Theatre
 */
async function handleCreateTheatre(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
        name: form.name.value.trim(),
        city: form.city.value.trim(),
        address: form.address.value.trim()
    };

    try {
        const res = await fetch('/api/theatres', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert('Theatre and default screen with 40 seats created!');
            window.location.reload();
        } else {
            const err = await res.json();
            alert(err.detail || 'Failed to create theatre.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

/**
 * Admin: Delete Theatre
 */
async function deleteTheatre(theatreId) {
    if (!confirm('Delete this theatre and all its screens and shows?')) return;
    try {
        const res = await fetch(`/api/theatres/${theatreId}`, { method: 'DELETE' });
        if (res.ok) {
            alert('Theatre deleted.');
            window.location.reload();
        } else {
            alert('Failed to delete theatre.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

/**
 * Admin: Create Show
 */
async function handleCreateShow(event) {
    event.preventDefault();
    const form = event.target;
    const payload = {
        movie_id: parseInt(form.movie_id.value, 10),
        theatre_id: parseInt(form.theatre_id.value, 10),
        screen_id: parseInt(form.screen_id.value, 10),
        show_date: form.show_date.value,
        show_time: form.show_time.value.trim(),
        base_price: parseFloat(form.base_price.value),
        is_active: true
    };

    try {
        const res = await fetch('/api/shows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert('Show scheduled successfully!');
            window.location.reload();
        } else {
            const err = await res.json();
            alert(err.detail || 'Failed to schedule show.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

/**
 * Admin: Delete Show
 */
async function deleteShow(showId) {
    if (!confirm('Delete this scheduled show?')) return;
    try {
        const res = await fetch(`/api/shows/${showId}`, { method: 'DELETE' });
        if (res.ok) {
            alert('Show removed.');
            window.location.reload();
        } else {
            alert('Failed to delete show.');
        }
    } catch (e) {
        alert('Network error.');
    }
}

/**
 * Admin: Run DSA Live Micro-Benchmarks
 */
async function runDsaBenchmark() {
    const outputElem = document.getElementById('benchmark-output');
    const btn = document.getElementById('run-benchmark-btn');
    if (outputElem) outputElem.innerHTML = '<em>Running micro-benchmarks on sample data...</em>';
    if (btn) btn.disabled = true;

    try {
        const res = await fetch('/api/admin/dsa-benchmark?size=10000');
        const data = await res.json();

        if (outputElem) {
            outputElem.innerHTML = `
                <div style="background: var(--bg-primary); border-radius: 8px; padding: 1.2rem; border: 1px solid var(--card-border);">
                    <h4 style="color: #38bdf8; margin-bottom: 0.8rem;">Benchmark Results (Sample Size: ${data.sample_size.toLocaleString()} items)</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 6px;">
                            <strong style="color: #34d399;">Merge Sort vs Quick Sort</strong>
                            <p style="margin-top: 0.4rem; font-size: 0.85rem;">Merge Sort: <strong>${data.sorting.merge_sort_ms} ms</strong> (${data.sorting.merge_sort_complexity})</p>
                            <p style="font-size: 0.85rem;">Quick Sort: <strong>${data.sorting.quick_sort_ms} ms</strong> (${data.sorting.quick_sort_complexity})</p>
                        </div>
                        <div style="background: var(--bg-secondary); padding: 1rem; border-radius: 6px;">
                            <strong style="color: #fbbf24;">Linear Search vs Binary Search</strong>
                            <p style="margin-top: 0.4rem; font-size: 0.85rem;">Linear Search: <strong>${data.searching.linear_search_microseconds} µs</strong> (${data.searching.linear_search_complexity})</p>
                            <p style="font-size: 0.85rem;">Binary Search: <strong>${data.searching.binary_search_microseconds} µs</strong> (${data.searching.binary_search_complexity})</p>
                        </div>
                    </div>
                    <span style="font-size: 0.8rem; color: var(--text-dim);">Algorithms executed dynamically in pure Python via <code>app/dsa/</code> modules.</span>
                </div>
            `;
        }
    } catch (e) {
        if (outputElem) outputElem.innerHTML = '<span style="color: #f87171;">Failed to run benchmark.</span>';
    } finally {
        if (btn) btn.disabled = false;
    }
}
