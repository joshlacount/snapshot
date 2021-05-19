const SnapshotSaveResult = {
	'SUCCESS': 0,
	'DUPLICATE': 1
}

function update_playlist_select() {
	const playlist_select = document.getElementById('playlist');
	for (i = playlist_select.options.length-1; i >= 0; i--) {
		playlist_select.options[i] = null;
	}

	const request = new XMLHttpRequest();
	request.open('GET', '/api/playlists');
	request.onload = () => {
		const response = request.responseText;
		const playlists = JSON.parse(response);
		

		for (i = 0; i < playlists.length; i++) {
			const playlist = playlists[i];
			const opt = document.createElement('option');
			opt.value = playlist['id'];
			opt.innerHTML = playlist['name'];
			playlist_select.appendChild(opt);
		}
		playlist_select.options[0].selected = true;
		update_snapshot_select();
	}
	request.send();
}

function update_snapshot_select() {
	const playlist_select = document.getElementById('playlist');
	const playlist_id = playlist_select.value;

	const snapshot_select = document.getElementById('snapshot');
	for (i = snapshot_select.options.length-1; i >= 1; i--) {
		snapshot_select.options[i] = null;
	}
	snapshot_select.options[0].selected = true;

	const request = new XMLHttpRequest();
	request.open('GET', `/api/snapshots?playlist_id=${playlist_id}`);
	request.onload = () => {
		const response = request.responseText;
		const snapshots = JSON.parse(response);

		for (i = 0; i < snapshots.length; i++) {
			const snapshot = snapshots[i]
			const opt = document.createElement('option');
			opt.value = snapshot['id'];
			opt.innerHTML = snapshot['name'];
			snapshot_select.appendChild(opt);
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
			if (response == SnapshotSaveResult.DUPLICATE) {
				alert("Already have a current snapshot");
			}
		}
		request.send(params);
	}
});
