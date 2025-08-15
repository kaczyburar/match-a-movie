document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search_name');
    const searchResults = document.getElementById('search-results');
    const roomPk = document.getElementById('room-pk');

    // Only initialize search functionality if all elements exist (host only)
    if (!searchInput || !searchResults || !roomPk) {
        return; // Exit if required elements are not found (non-host users)
    }

    const roomPkValue = roomPk.value;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        if (query.length < 3) {
            searchResults.style.display = 'none';
            searchResults.innerHTML = '';
            return;
        }

        // Show loading state
        searchResults.innerHTML = '<p>Searching...</p>';
        searchResults.style.display = 'block';

        fetch(`/rooms/${roomPkValue}/search/?q=${encodeURIComponent(query)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.users && data.users.length > 0) {
                    searchResults.innerHTML = '<ul>' +
                        data.users.map(user =>
                            `<li onclick="selectUser('${user.username}', ${user.id})" data-user-id="${user.id}">
                                ${user.username}
                            </li>`
                        ).join('') +
                        '</ul>';
                } else {
                    searchResults.innerHTML = '<p>No users found</p>';
                }
                searchResults.style.display = 'block';
            })
            .catch(error => {
                console.error('Search error:', error);
                searchResults.innerHTML = '<p>Search error occurred</p>';
                searchResults.style.display = 'block';
            });
    });

    // Hide search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });

    // Clear search results when input is focused
    searchInput.addEventListener('focus', function() {
        if (this.value.trim().length >= 3) {
            searchResults.style.display = 'block';
        }
    });

    // Handle form submission - only if form exists (host only)
    const inviteForm = document.querySelector('.invite-form');
    if (inviteForm) {
        inviteForm.addEventListener('submit', function(e) {
            const searchValue = searchInput.value.trim();
            if (!searchValue) {
                e.preventDefault();
                alert('Please select a user to invite');
                return false;
            }
        });
    }
});

function selectUser(username, userId) {
    const searchInput = document.getElementById('search_name');
    const searchResults = document.getElementById('search-results');

    if (searchInput && searchResults) {
        searchInput.value = username;
        searchResults.style.display = 'none';

        // Add visual feedback
        searchInput.style.borderColor = '#28a745';
        setTimeout(() => {
            searchInput.style.borderColor = '';
        }, 2000);
    }
}

// Function to toggle friends section
function toggleFriendsSection() {
    const friendsSection = document.getElementById('friends-section');
    const button = document.querySelector('.btn-friends');

    if (!friendsSection) return;

    const isVisible = friendsSection.style.display !== 'none';

    if (isVisible) {
        friendsSection.style.display = 'none';
        button.innerHTML = '<span class="emoji">👥</span>Friends';
    } else {
        friendsSection.style.display = 'block';
        button.innerHTML = '<span class="emoji">👥</span>Hide Friends';
    }
}