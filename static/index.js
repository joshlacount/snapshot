function update_playlists() {
	const request = new XMLHttpRequest();
	request.open('GET', '/api/playlists');
	request.onload = () => {
		const response = request.responseText;
		const playlists = JSON.parse(response);
		
	}
	request.send();
}

document.addEventListener('DOMContentLoaded', () => {
	update_playlists();
}
