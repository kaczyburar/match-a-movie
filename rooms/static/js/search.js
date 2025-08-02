document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search_name');
    const searchResults = document.getElementById('search-results');
    const roomPk = document.getElementById('room-pk').value;

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        if (query.length < 3) {
            searchResults.style.display = 'none';
            return;
        }


        fetch(`/rooms/${roomPk}/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.users && data.users.length > 0) {
                    searchResults.innerHTML = '<ul>' +
                        data.users.map(user =>
                            `<li onclick="selectUser('${user.username}', ${user.id})">
                                ${user.username}
                            </li>`
                        ).join('') +
                    '</ul>';
                } else {
                    searchResults.innerHTML = '<p>Users not found</p>';
                }

                searchResults.style.display = 'block';
            })
            .catch(error => {
                searchResults.innerHTML = '<p>Search error</p>';
                searchResults.style.display = 'block';
            });
    });

    document.addEventListener('click', function(e) {
        if (e.target !== searchInput) {
            searchResults.style.display = 'none';
        }
    });
});

function selectUser(username, userId) {
    document.getElementById('search_name').value = username;
    document.getElementById('search-results').style.display = 'none';

}