function update_playlist_select() {
	const request = new XMLHttpRequest();
	request.open('GET', '/api/playlists');
	request.onload = () => {
		const response = request.responseText;
		const playlists = JSON.parse(response);
		
		const select = document.getElementById('playlist');
		for (i = select.options.length-1; i >= 0; i--) {
			select.options[i] = null;
		}
		for (i = 0; i < playlists.length; i++) {
			const playlist = playlists[i];
			let opt = document.createElement('option');
			opt.value = playlist['id'];
			opt.innerHTML = playlist['name'];
			select.appendChild(opt);
		}
	}
	request.send();
}

document.addEventListener('DOMContentLoaded', () => {
	update_playlist_select();

	const save_snapshot_button = document.getElementById('save-snapshot');
	save_snapshot_button.onclick = () => {
		const playlist_select = document.getElementById('playlist');
		const playlist_id = playlist_select.value;
		const params = `playlist_id=${playlist_id}`;

		const request = new XMLHttpRequest();
		request.open('POST', '/api/save-snapshot', true);
		request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
		request.onload = () => {
			const response = request.responseText;
			console.log(response);
		}
		request.send(params);
	}
});
