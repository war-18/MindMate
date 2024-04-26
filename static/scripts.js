document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('searchForm');
    const resultsDiv = document.getElementById('searchResults');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        fetch('/search', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            resultsDiv.innerHTML = data;
        })
        .catch(error => console.error('Error:', error));
    });
});
