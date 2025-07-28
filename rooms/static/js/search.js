document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search_name');
    const searchResults = document.getElementById('search-results');

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        if (query.length < 3) {
            searchResults.style.display = 'none';
            return;
        }

        const filteredUsers = usersData.filter(user =>
            user.username.toLowerCase().includes(query.toLowerCase())
        );

        if (filteredUsers.length > 0) {
            searchResults.innerHTML = '<ul>' +
                filteredUsers.map(user =>
                    `<li onclick="selectUser('${user.username}', ${user.id})">
                        ${user.username}
                    </li>`
                ).join('') +
            '</ul>';
        } else {
            searchResults.innerHTML = '<p>Nie znaleziono użytkowników</p>';
        }

        searchResults.style.display = 'block';
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

    console.log('Wybrano użytkownika:', username, 'ID:', userId);
}