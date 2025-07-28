document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search_name');
    const searchResults = document.getElementById('search-results');
    const roomPk = document.getElementById('room-pk').value; // Ukryte pole z PK pokoju

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
                    searchResults.innerHTML = '<p>Nie znaleziono użytkowników</p>';
                }

                searchResults.style.display = 'block';
            })
            .catch(error => {
                console.error('Błąd AJAX:', error);
                searchResults.innerHTML = '<p>Błąd wyszukiwania</p>';
                searchResults.style.display = 'block';
            });
    });

    // Ukryj wyniki po kliknięciu poza pole
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