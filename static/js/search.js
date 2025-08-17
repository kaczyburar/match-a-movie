document.getElementById('search_name').addEventListener('input', function() {
    const query = this.value;

    if (query.length < 3) return;

    const roomId = document.getElementById('room-pk').value;

    fetch(`/rooms/${roomId}/search/?q=${query}`)  //
        .then(response => response.json())
        .then(data => {
            const results = data.users.map(user => `<li>${user.username}</li>`).join('');
            document.getElementById('search-results').innerHTML = results;
        });
});