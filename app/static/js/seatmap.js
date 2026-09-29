/**
 * CineBook Interactive Seat Map & Dynamic Pricing Engine
 */

let selectedSeats = new Map(); // seatId -> { code, price, type }

function toggleSeatSelection(element, seatId, seatCode, price, seatType) {
    if (element.classList.contains('booked')) {
        return;
    }

    if (element.classList.contains('selected')) {
        element.classList.remove('selected');
        selectedSeats.delete(seatId);
    } else {
        element.classList.add('selected');
        selectedSeats.set(seatId, { code: seatCode, price: parseFloat(price), type: seatType });
    }

    updateSeatSummary();
}

function updateSeatSummary() {
    const listElem = document.getElementById('selected-seats-list');
    const countElem = document.getElementById('selected-seats-count');
    const totalElem = document.getElementById('total-price-display');
    const proceedBtn = document.getElementById('proceed-btn');

    const seatCodes = Array.from(selectedSeats.values()).map(s => s.code);
    const totalPrice = Array.from(selectedSeats.values()).reduce((sum, s) => sum + s.price, 0);

    if (listElem) {
        listElem.innerText = seatCodes.length > 0 ? seatCodes.join(', ') : 'None';
    }
    if (countElem) {
        countElem.innerText = seatCodes.length;
    }
    if (totalElem) {
        totalElem.innerText = `₹${totalPrice.toFixed(2)}`;
    }
    if (proceedBtn) {
        proceedBtn.disabled = selectedSeats.size === 0;
    }
}

/**
 * DSA Feature: Calls backend Sliding Window contiguous seat recommender
 */
async function autoRecommendContiguousSeats(showId) {
    const countInput = document.getElementById('contiguous-count');
    const count = parseInt(countInput ? countInput.value : '2', 10);
    const feedback = document.getElementById('recommendation-feedback');

    try {
        const res = await fetch(`/api/shows/${showId}/seats?recommend_count=${count}`);
        const data = await res.json();

        if (data.recommended_seats && data.recommended_seats.length > 0) {
            // Clear current selections
            document.querySelectorAll('.seat.selected').forEach(el => el.classList.remove('selected'));
            selectedSeats.clear();

            data.recommended_seats.forEach(s => {
                const el = document.querySelector(`.seat[data-seat-id="${s.seat_id}"]`);
                if (el && !el.classList.contains('booked')) {
                    el.classList.add('selected');
                    selectedSeats.set(s.seat_id, { code: s.code, price: s.price, type: s.type });
                }
            });

            updateSeatSummary();
            if (feedback) {
                const codes = data.recommended_seats.map(s => s.code).join(', ');
                feedback.innerHTML = `<span style="color: #34d399;">✓ DSA Sliding Window recommended contiguous seats: <strong>${codes}</strong></span>`;
            }
        } else {
            if (feedback) {
                feedback.innerHTML = `<span style="color: #f87171;">✕ No contiguous block of ${count} seats available together in this show.</span>`;
            }
        }
    } catch (err) {
        console.error('Error fetching contiguous seats:', err);
    }
}

/**
 * Submits the confirmed booking to backend API
 */
async function proceedToBooking(showId) {
    if (selectedSeats.size === 0) {
        alert('Please select at least one seat.');
        return;
    }

    const seatIds = Array.from(selectedSeats.keys());
    const errBox = document.getElementById('booking-error-box');
    if (errBox) errBox.style.display = 'none';

    try {
        const res = await fetch('/api/bookings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                show_id: showId,
                seat_ids: seatIds
            })
        });

        const data = await res.json();

        if (res.status === 409) {
            // Double booking collision handled cleanly
            if (errBox) {
                errBox.innerText = data.detail || 'One or more of the selected seats were just booked. Please reselect.';
                errBox.style.display = 'block';
            } else {
                alert(data.detail);
            }
            return;
        }

        if (!res.ok) {
            if (errBox) {
                errBox.innerText = data.detail || 'Failed to initiate booking.';
                errBox.style.display = 'block';
            } else {
                alert(data.detail || 'Booking failed.');
            }
            return;
        }

        // Successfully initiated booking -> proceed to booking summary / payment
        window.location.href = `/booking/${data.booking_id}`;
    } catch (err) {
        if (errBox) {
            errBox.innerText = 'Network error while booking. Please try again.';
            errBox.style.display = 'block';
        }
    }
}
