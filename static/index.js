const SnapshotSaveResult = {
    'SUCCESS': 0,
    'DUPLICATE': 1
}

function create_play_button(track_ids) {
    const button = document.createElement('div');
    button.className = 'play-btn';
    button.innerHTML = '<i class="fas fa-play"></i>';
    button.addEventListener('click', () => {
        play_tracks(track_ids);
    });
    return button;
}

function play_tracks(track_ids) {
    const track_ids_str = JSON.stringify(track_ids);
    const params = `track_ids=${track_ids_str}`;
    const request = new XMLHttpRequest();
    request.open('POST', '/api/play-tracks');
    request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    request.onload = () => {
        const response = request.responseText;
        if (response == '1') {
            alert("No active Spotify player found");
        }
    }
    request.send(params);
}

function update_playlist_select() {
    const playlist_select = document.getElementById('playlist-select');
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
    const playlist_select = document.getElementById('playlist-select');
    const playlist_id = playlist_select.value;

    const snapshot_select = document.getElementById('snapshot-select');
    for (i = snapshot_select.options.length-1; i >= 1; i--) {
        snapshot_select.options[i] = null;
    }
    snapshot_select.options[0].selected = true;
    snapshot_select.options[0].value = playlist_id;

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
        update_tracks_table();
    }
    request.send();
}

function update_tracks_table(is_current=false) {
    const snapshot_select = document.getElementById('snapshot-select');
    const id = snapshot_select.value;

    if (snapshot_select.selectedIndex == 0) {
        var url = `/api/tracks?playlist_id=${id}`;
    }
    else {
        var url = `/api/tracks?snapshot_id=${id}`;
    }

    const tracks_table = document.getElementById('tracks-table');
    if (tracks_table.tBodies.length != 0) {
        tracks_table.removeChild(tracks_table.tBodies[0]);
    }

    const request = new XMLHttpRequest();
    request.open('GET', url);
    request.onload = () => {
        const response = request.responseText;
        const tracks = JSON.parse(response);

        const track_ids = Array.from(tracks, track => track['id']);
        const new_play_all_button = create_play_button(track_ids);
        new_play_all_button.id = 'play-all-btn';
        new_play_all_button.title = 'Play All Tracks';
        document.getElementById('play-all-btn').replaceWith(new_play_all_button);

        const new_tbody = document.createElement('tbody');

        for (i = 0; i < tracks.length; i++) {
            const new_row = new_tbody.insertRow(-1);
            for (j = 0; j < 3; j++) {
                new_row.insertCell();
            }

            new_row.cells[0].className = 'play-btn-col';
            const play_button = create_play_button([tracks[i]['id']]);
            play_button.title = `Play ${tracks[i]['title']}`;
            new_row.cells[0].appendChild(play_button);
            new_row.cells[1].innerHTML = tracks[i]['title'];
            new_row.cells[2].innerHTML = tracks[i]['artist'];
        }

        tracks_table.appendChild(new_tbody);
    }
    request.send();
}

function rename_snapshot(new_name) {
    const snapshot_select = document.getElementById('snapshot-select');
    const selected = snapshot_select.selectedOptions[0];
    const snapshot_id = selected.value;

    const params = `snapshot_id=${snapshot_id}&new_name=${new_name}`;
    const request = new XMLHttpRequest();
    request.open('POST', '/api/rename-snapshot');
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    request.onload = () => {
        selected.innerHTML = new_name;
    }
    request.send(params);
}

function create_playlist_button_on_click() {
    const snapshot_select = document.getElementById('snapshot-select');
    if (snapshot_select.selectedIndex <= 0) {
        alert("Please select a snapshot");
        return;
    }
    const snapshot_id = snapshot_select.selectedOptions[0].value;

    const params = `snapshot_id=${snapshot_id}`;
    const request = new XMLHttpRequest();
    request.open('POST', '/api/create-playlist');
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    request.onload = () => {
        const response = request.responseText;
        if (response == '1') {
            alert("Error creating playlist");
            return;
        }
        update_playlist_select();
    }
    request.send(params);
}

function delete_snapshot_button_on_click() {
    const snapshot_select = document.getElementById('snapshot-select');
    if (snapshot_select.selectedIndex <= 0) {
        alert("Please select a snapshot");
        return;
    }

    if (!confirm("Are you sure you want to delete this snapshot?  It can't be recovered.")) {
        return;
    }

    const snapshot_id = snapshot_select.selectedOptions[0].value;

    const params = `snapshot_id=${snapshot_id}`;
    const request = new XMLHttpRequest();
    request.open('POST', '/api/delete-snapshot');
    request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    request.onload = () => {
        const response = request.responseText;
        if (response == '1') {
            alert("Error deleting snapshot");
            return;
        }
        update_snapshot_select();
    }
    request.send(params);
}

document.addEventListener('DOMContentLoaded', () => {
    update_playlist_select();

    const save_snapshot_button = document.getElementById('save-snapshot');
    save_snapshot_button.onclick = () => {
        const playlist_select = document.getElementById('playlist-select');
        const playlist_id = playlist_select.value;
        const params = `playlist_id=${playlist_id}`;

        const request = new XMLHttpRequest();
        request.open('POST', '/api/save-snapshot', true);
        request.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        request.onload = () => {
            const response = request.responseText;
            if (response == SnapshotSaveResult.DUPLICATE) {
                alert("Already have a current snapshot");
            }
        }
        request.send(params);
    }

    const rename_snapshot_button = document.getElementById('rename-snapshot');
    rename_snapshot_button.onclick = () => {
        const snapshot_select = document.getElementById('snapshot-select');
        if (snapshot_select.selectedIndex  <= 0) {
            return;
        }

        const new_name = prompt("Enter new snapshot name");
        if (new_name != null) {
            rename_snapshot(new_name);
        }
    }
});
