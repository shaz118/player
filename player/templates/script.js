const audioPlayer = document.getElementById("audio-player");
const trackTitle = document.getElementById("track-title");
const playPauseBtn = document.getElementById("play-pause");
const prevBtn = document.getElementById("prev");
const nextBtn = document.getElementById("next");
const cdImage = document.getElementById("cd-image");

let audioFiles = [];
let currentIndex = 0;

function fetchVideos() {
    const link = document.getElementById("youtube-link").value;
    fetch('/get_videos', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({video_id: link})
    })
    .then(() => loadAudioFiles(true))
    .catch(error => console.error("Error fetching videos:", error));
}

function loadAudioFiles(onUserAction = false) {
    fetch('/list_audio')
        .then(response => response.json())
        .then(files => {
            if (JSON.stringify(files) !== JSON.stringify(audioFiles)) {
                audioFiles = files;
                if (onUserAction && audioFiles.length > 0) {
                    loadTrack(0);
                }
            }
        })
        .catch(error => console.error('Error loading audio files:', error));
}

setInterval(loadAudioFiles, 5000);

function togglePlayPause() {
    if (audioPlayer.paused) {
        audioPlayer.play();
        playPauseBtn.innerHTML = "&#10074;&#10074;";
        cdImage.style.animationPlayState = "running";
    } else {
        audioPlayer.pause();
        playPauseBtn.innerHTML = "&#9658;";
        cdImage.style.animationPlayState = "paused";
    }
}

function loadTrack(index) {
    if (audioFiles.length === 0) return;
    currentIndex = index;
    let filename = audioFiles[currentIndex];
    let audioSrc = `/stream_audio/${filename}`;
    
    audioPlayer.src = audioSrc;
    audioPlayer.load();
    audioPlayer.play();
    trackTitle.textContent = filename;
    cdImage.style.animationPlayState = "running";
}

playPauseBtn.addEventListener("click", () => {
    loadAudioFiles(true);
    togglePlayPause();
});

nextBtn.addEventListener("click", () => {
    loadAudioFiles(true);
    currentIndex = (currentIndex + 1) % audioFiles.length;
    loadTrack(currentIndex);
});

prevBtn.addEventListener("click", () => {
    loadAudioFiles(true);
    currentIndex = (currentIndex - 1 + audioFiles.length) % audioFiles.length;
    loadTrack(currentIndex);
});

loadAudioFiles();
