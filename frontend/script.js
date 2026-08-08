const API = "http://127.0.0.1:5000";

function showMessage(element, message) {
    element.innerHTML = `<p>${message}</p>`;
}

async function discoverSong() {
    const input = document.getElementById("songInput");
    const results = document.getElementById("results");
    const song = input.value.trim();

    if (!song) {
        showMessage(results, "Enter a song first.");
        return;
    }

    showMessage(results, "Finding songs that match your taste...");

    try {
        const response = await fetch(
            `${API}/api/recommend?song=${encodeURIComponent(song)}`
        );

        const data = await response.json();

        if (!response.ok || data.length === 0) {
            showMessage(results, "Sorry, we couldn't find that song.");
            return;
        }

        results.innerHTML = data.map((song, index) => `
            <div class="result">
                <div class="result-info">
                    <strong>${String(index + 1).padStart(2, "0")} &nbsp; ${song.track_name}</strong>
                    <span>${song.artists} · ${song.track_genre}</span>
                </div>
                <span class="result-score">${song.similarity}% match</span>
            </div>
        `).join("");
    } catch {
        showMessage(results, "Could not connect to Music Lab.");
    }
}

async function getDNA() {
    const input = document.getElementById("dnaInput");
    const results = document.getElementById("dnaResults");
    const song = input.value.trim();

    if (!song) {
        showMessage(results, "Enter a song first.");
        return;
    }

    showMessage(results, "Analyzing song...");

    try {
        const response = await fetch(
            `${API}/api/dna?song=${encodeURIComponent(song)}`
        );

        const data = await response.json();

        if (!response.ok) {
            showMessage(results, "Song not found.");
            return;
        }

        const labels = {
            energy: "Energy",
            danceability: "Danceability",
            valence: "Happiness",
            acousticness: "Acousticness",
            instrumentalness: "Instrumentalness",
            speechiness: "Speechiness"
        };

        results.innerHTML = Object.entries(labels).map(([key, label]) => `
            <div class="dna-card">
                <span>${label}</span>
                <strong>${data[key]}%</strong>
                <div class="dna-bar">
                    <div style="width:${data[key]}%"></div>
                </div>
            </div>
        `).join("");
    } catch {
        showMessage(results, "Could not connect to Music Lab.");
    }
}

async function getMood(mood) {
    const results = document.getElementById("moodResults");

    showMessage(results, "Finding your soundtrack...");

    try {
        const response = await fetch(
            `${API}/api/mood?mood=${encodeURIComponent(mood)}`
        );

        const data = await response.json();

        if (!data.length) {
            showMessage(results, "No songs found.");
            return;
        }

        results.innerHTML = data.map((song, index) => `
            <div class="result">
                <div class="result-info">
                    <strong>${String(index + 1).padStart(2, "0")} &nbsp; ${song.track_name}</strong>
                    <span>${song.artists} · ${song.track_genre}</span>
                </div>
                <span class="result-score">${song.popularity} popularity</span>
            </div>
        `).join("");
    } catch {
        showMessage(results, "Could not connect to Music Lab.");
    }
}

async function loadGems() {
    const results = document.getElementById("gemsResults");

    showMessage(results, "Searching for hidden gems...");

    try {
        const response = await fetch(`${API}/api/gems`);
        const data = await response.json();

        results.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Song</th>
                        <th>Artist</th>
                        <th>Genre</th>
                        <th>Popularity</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(song => `
                        <tr>
                            <td>${song.track_name}</td>
                            <td>${song.artists}</td>
                            <td>${song.track_genre}</td>
                            <td>${song.popularity}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch {
        showMessage(results, "Could not connect to Music Lab.");
    }
}

async function loadEvolution() {
    const results = document.getElementById("evolutionResults");

    showMessage(results, "Analyzing music trends...");

    try {
        const response = await fetch(`${API}/api/evolution`);
        const data = await response.json();

        results.innerHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Genre</th>
                        <th>Tracks</th>
                        <th>Popularity</th>
                        <th>Energy</th>
                        <th>Danceability</th>
                        <th>Valence</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(item => `
                        <tr>
                            <td>${item.track_genre}</td>
                            <td>${item.tracks}</td>
                            <td>${item.popularity}</td>
                            <td>${item.energy}%</td>
                            <td>${item.danceability}%</td>
                            <td>${item.valence}%</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch {
        showMessage(results, "Could not connect to Music Lab.");
    }
}

async function compareSongs() {
    const song1 = document.getElementById("song1").value.trim();
    const song2 = document.getElementById("song2").value.trim();
    const results = document.getElementById("compareResults");

    if (!song1 || !song2) {
        showMessage(results, "Enter both songs.");
        return;
    }

    showMessage(results, "Comparing songs...");

    try {
        const response = await fetch(
            `${API}/api/compare?song1=${encodeURIComponent(song1)}&song2=${encodeURIComponent(song2)}`
        );

        const data = await response.json();

        if (!response.ok) {
            showMessage(results, "One or both songs could not be found.");
            return;
        }

        const labels = {
            energy: "Energy",
            danceability: "Danceability",
            valence: "Happiness",
            acousticness: "Acousticness",
            instrumentalness: "Instrumentalness",
            speechiness: "Speechiness"
        };

        let html = `
            <div class="compare-header">
                <div class="compare-song">
                    <h3>${data.song_one.name}</h3>
                    <p>${data.song_one.artists} · ${data.song_one.genre}</p>
                    <p>Popularity: ${data.song_one.popularity}</p>
                </div>
                <div class="compare-song">
                    <h3>${data.song_two.name}</h3>
                    <p>${data.song_two.artists} · ${data.song_two.genre}</p>
                    <p>Popularity: ${data.song_two.popularity}</p>
                </div>
            </div>
        `;

        Object.entries(labels).forEach(([key, label]) => {
            const one = data.features[key].one;
            const two = data.features[key].two;

            html += `
                <div class="compare-feature">
                    <div class="compare-label">
                        <span>${label}</span>
                        <span>${one}% &nbsp; vs &nbsp; ${two}%</span>
                    </div>
                    <div class="compare-bars">
                        <div class="bar"><div style="width:${one}%"></div></div>
                        <div class="bar"><div style="width:${two}%"></div></div>
                    </div>
                </div>
            `;
        });

        results.innerHTML = html;
    } catch {
        showMessage(results, "Could not connect to Music Lab.");
    }
}