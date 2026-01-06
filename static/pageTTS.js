// (function () {

//     let audio = null;
//     let audioUrl = null;
//     let isGenerating = false;

//     async function generateAndPlay() {
//         if (isGenerating) return;

//         isGenerating = true;
//         updateButtonStates("loading");

//         const html = document.documentElement.outerHTML;

//         try {
//             const response = await fetch("https://api.indyatools.com/page-tts", {
//                 method: "POST",
//                 headers: { "Content-Type": "application/json" },
//                 body: JSON.stringify({ html })
//             });

//             if (!response.ok) {
//                 throw new Error("TTS API failed");
//             }

//             const blob = await response.blob();

//             if (audioUrl) {
//                 URL.revokeObjectURL(audioUrl);
//             }

//             audioUrl = URL.createObjectURL(blob);
//             audio = new Audio(audioUrl);

//             audio.onloadeddata = () => {
//                 updateButtonStates("ready");
//                 audio.play();
//             };

//             audio.onplay = () => updateButtonStates("playing");
//             audio.onpause = () => updateButtonStates("paused");
//             audio.onended = () => updateButtonStates("ready");

//         } catch (err) {
//             console.error("TTS error:", err);
//             alert("Failed to generate audio");
//             updateButtonStates("ready");
//         } finally {
//             isGenerating = false;
//         }
//     }

//     function playAudio() {
//         if (audio && audio.src) {
//             audio.play();
//         } else {
//             generateAndPlay();
//         }
//     }

//     function pauseAudio() {
//         if (audio && !audio.paused) {
//             audio.pause();
//         }
//     }

//     function stopAudio() {
//         if (audio) {
//             audio.pause();
//             audio.currentTime = 0;
//         }
//     }

//     function updateButtonStates(state) {
//         const playBtn = document.getElementById("tts-play-btn");
//         const pauseBtn = document.getElementById("tts-pause-btn");
//         const stopBtn = document.getElementById("tts-stop-btn");

//         if (!playBtn) return;

//         playBtn.disabled = false;
//         pauseBtn.disabled = false;
//         stopBtn.disabled = false;

//         if (state === "loading") {
//             playBtn.innerHTML = '<span class="spinner"></span>';
//             playBtn.disabled = true;
//             pauseBtn.disabled = true;
//             stopBtn.disabled = true;
//         } else if (state === "playing") {
//             playBtn.innerHTML = '▶';
//             playBtn.disabled = true;
//         } else if (state === "paused") {
//             playBtn.innerHTML = '▶';
//             pauseBtn.disabled = true;
//         } else {
//             playBtn.innerHTML = '▶';
//             pauseBtn.disabled = true;
//             stopBtn.disabled = true;
//         }
//     }

//     function showNotification(message, type = "info") {
//         const notification = document.createElement("div");
//         notification.className = `tts-notification ${type}`;
//         notification.textContent = message;
//         document.body.appendChild(notification);

//         setTimeout(() => notification.classList.add("show"), 10);
//         setTimeout(() => {
//             notification.classList.remove("show");
//             setTimeout(() => notification.remove(), 300);
//         }, 3000);
//     }

//     function makeDraggable(el) {
//         let isDragging = false;
//         let currentX = 0, currentY = 0, initialX = 0, initialY = 0;

//         el.addEventListener("mousedown", dragStart);
//         el.addEventListener("touchstart", dragStart);

//         function dragStart(e) {
//             // Don't drag if clicking a button
//             if (e.target.tagName === "BUTTON" || e.target.closest("button")) return;

//             if (e.type === "touchstart") {
//                 initialX = e.touches[0].clientX - currentX;
//                 initialY = e.touches[0].clientY - currentY;
//             } else {
//                 initialX = e.clientX - currentX;
//                 initialY = e.clientY - currentY;
//             }

//             isDragging = true;
//             el.style.cursor = "grabbing";
//             document.addEventListener("mousemove", drag);
//             document.addEventListener("mouseup", dragEnd);
//             document.addEventListener("touchmove", drag);
//             document.addEventListener("touchend", dragEnd);
//         }

//         function drag(e) {
//             if (!isDragging) return;
//             e.preventDefault();

//             let clientX, clientY;
//             if (e.type === "touchmove") {
//                 clientX = e.touches[0].clientX;
//                 clientY = e.touches[0].clientY;
//             } else {
//                 clientX = e.clientX;
//                 clientY = e.clientY;
//             }

//             currentX = clientX - initialX;
//             currentY = clientY - initialY;

//             // Keep within screen bounds
//             const rect = el.getBoundingClientRect();
//             const originalLeft = rect.left - currentX;
//             const originalTop = rect.top - currentY;

//             const maxX = window.innerWidth - rect.width;
//             const maxY = window.innerHeight - rect.height;

//             currentX = Math.max(-originalLeft, Math.min(currentX, maxX - originalLeft));
//             currentY = Math.max(-originalTop, Math.min(currentY, maxY - originalTop));

//             el.style.transform = `translate(${currentX}px, ${currentY}px)`;
//         }

//         function dragEnd() {
//             isDragging = false;
//             el.style.cursor = "grab";
//             document.removeEventListener("mousemove", drag);
//             document.removeEventListener("mouseup", dragEnd);
//             document.removeEventListener("touchmove", drag);
//             document.removeEventListener("touchend", dragEnd);
//         }
//     }

//     function createControls() {
//         // Add styles
//         const style = document.createElement("style");
//         style.textContent = `
//             .tts-player-container {
//                 position: fixed;
//                 bottom: 20px;
//                 right: 20px;
//                 z-index: 9999;
//                 background: rgba(0, 0, 0, 0.85);
//                 padding: 12px;
//                 border-radius: 12px;
//                 box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
//                 user-select: none;
//                 backdrop-filter: blur(10px);
//                 border: 1px solid rgba(255, 255, 255, 0.1);
//                 cursor: grab;
//             }

//             .tts-player-container:active {
//                 cursor: grabbing;
//             }

//             .tts-controls {
//                 display: flex;
//                 gap: 6px;
//             }

//             .tts-btn {
//                 width: 40px;
//                 height: 40px;
//                 border: none;
//                 border-radius: 8px;
//                 background: rgba(255, 255, 255, 0.1);
//                 color: white;
//                 cursor: pointer;
//                 font-size: 14px;
//                 transition: all 0.15s ease;
//                 display: flex;
//                 align-items: center;
//                 justify-content: center;
//             }

//             .tts-btn:hover:not(:disabled) {
//                 background: rgba(255, 255, 255, 0.2);
//             }

//             .tts-btn:active:not(:disabled) {
//                 transform: scale(0.95);
//             }

//             .tts-btn:disabled {
//                 opacity: 0.4;
//                 cursor: not-allowed;
//             }

//             .tts-btn-primary:not(:disabled) {
//                 background: rgba(255, 255, 255, 0.9);
//                 color: #000;
//             }

//             .tts-btn-primary:hover:not(:disabled) {
//                 background: white;
//             }

//             .spinner {
//                 width: 14px;
//                 height: 14px;
//                 border: 2px solid rgba(255, 255, 255, 0.3);
//                 border-top-color: white;
//                 border-radius: 50%;
//                 animation: spin 0.8s linear infinite;
//             }

//             @keyframes spin {
//                 to { transform: rotate(360deg); }
//             }
//         `;
//         document.head.appendChild(style);

//         const container = document.createElement("div");
//         container.className = "tts-player-container";
//         container.setAttribute("data-tts-ignore", "true");

//         container.innerHTML = `
//             <div class="tts-controls">
//                 <button id="tts-play-btn" class="tts-btn tts-btn-primary" title="Play">▶</button>
//                 <button id="tts-pause-btn" class="tts-btn" title="Pause">⏸</button>
//                 <button id="tts-stop-btn" class="tts-btn" title="Stop">⏹</button>
//             </div>
//         `;

//         document.body.appendChild(container);

//         document.getElementById("tts-play-btn").onclick = playAudio;
//         document.getElementById("tts-pause-btn").onclick = pauseAudio;
//         document.getElementById("tts-stop-btn").onclick = stopAudio;

//         makeDraggable(container);
//         updateButtonStates("ready");
//     }

//     window.addEventListener("DOMContentLoaded", createControls);

// })();












(function () {

    let audio = null;
    let audioUrl = null;
    let isGenerating = false;
    let progressInterval = null;

    // async function generateAndPlay() {
    //     if (isGenerating) return;

    //     isGenerating = true;
    //     updateButtonStates("loading");

    //     const html = document.documentElement.outerHTML;

    //     try {
    //         const response = await fetch("https://api.indyatools.com/page-tts", {
    //             method: "POST",
    //             headers: { "Content-Type": "application/json" },
    //             body: JSON.stringify({ html })
    //         });

    //         if (!response.ok) {
    //             throw new Error("TTS API failed");
    //         }

    //         const blob = await response.blob();

    //         if (audioUrl) {
    //             URL.revokeObjectURL(audioUrl);
    //         }

    //         audioUrl = URL.createObjectURL(blob);
    //         audio = new Audio(audioUrl);

    //         audio.onloadeddata = () => {
    //             updateButtonStates("ready");
    //             updateDuration();
    //             audio.play();
    //         };

    //         audio.onplay = () => {
    //             updateButtonStates("playing");
    //             startProgressTracking();
    //         };

    //         audio.onpause = () => {
    //             updateButtonStates("paused");
    //             stopProgressTracking();
    //         };

    //         audio.onended = () => {
    //             updateButtonStates("ready");
    //             stopProgressTracking();
    //             resetProgress();
    //         };

    //         audio.ontimeupdate = updateProgress;

    //     } catch (err) {
    //         console.error("TTS error:", err);
    //         showNotification("Failed to generate audio", "error");
    //         updateButtonStates("ready");
    //     } finally {
    //         isGenerating = false;
    //     }
    // }


    let mediaSource = null;
    let sourceBuffer = null;
    let reader = null;


    async function generateAndPlay() {
        if (isGenerating) return;
        isGenerating = true;

        updateButtonStates("loading");

        const html = document.documentElement.outerHTML;

        mediaSource = new MediaSource();
        audio = new Audio(URL.createObjectURL(mediaSource));
        audio.play();

        mediaSource.addEventListener("sourceopen", async () => {
            sourceBuffer = mediaSource.addSourceBuffer('audio/wav; codecs="1"');

            const response = await fetch("https://api.indyatools.com/page-tts-stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ html })
            });

            reader = response.body.getReader();
            updateButtonStates("playing");

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                sourceBuffer.appendBuffer(value);
                await waitForUpdate(sourceBuffer);
            }

            mediaSource.endOfStream();
            isGenerating = false;
        });
    }

    function playAudio() {
        if (audio && audio.src) {
            audio.play();
        } else {
            generateAndPlay();
        }
    }

    function pauseAudio() {
        if (audio && !audio.paused) {
            audio.pause();
        }
    }

    function stopAudio() {
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
            resetProgress();
        }
    }

    function formatTime(seconds) {
        if (isNaN(seconds)) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    function updateProgress() {
        if (!audio) return;

        const progressBar = document.getElementById("tts-progress-bar");
        const currentTimeEl = document.getElementById("tts-current-time");

        if (progressBar && audio.duration) {
            const percent = (audio.currentTime / audio.duration) * 100;
            progressBar.style.width = `${percent}%`;
        }

        if (currentTimeEl) {
            currentTimeEl.textContent = formatTime(audio.currentTime);
        }
    }

    function updateDuration() {
        if (!audio) return;

        const durationEl = document.getElementById("tts-duration");
        if (durationEl && audio.duration) {
            durationEl.textContent = formatTime(audio.duration);
        }
    }

    function resetProgress() {
        const progressBar = document.getElementById("tts-progress-bar");
        const currentTimeEl = document.getElementById("tts-current-time");

        if (progressBar) progressBar.style.width = "0%";
        if (currentTimeEl) currentTimeEl.textContent = "0:00";
    }

    function startProgressTracking() {
        stopProgressTracking();
        progressInterval = setInterval(updateProgress, 100);
    }

    function stopProgressTracking() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }

    function seekAudio(e) {
        if (!audio || !audio.duration) return;

        const progressTrack = document.getElementById("tts-progress-track");
        const rect = progressTrack.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        audio.currentTime = percent * audio.duration;
        updateProgress();
    }

    function updateButtonStates(state) {
        const playBtn = document.getElementById("tts-play-btn");
        const pauseBtn = document.getElementById("tts-pause-btn");
        const stopBtn = document.getElementById("tts-stop-btn");
        const progressTrack = document.getElementById("tts-progress-track");
        const loadingSpinner = document.getElementById("tts-loading-spinner");

        if (!playBtn) return;

        // Hide loading spinner by default
        if (loadingSpinner) {
            loadingSpinner.style.display = "none";
        }

        playBtn.style.display = "flex";
        pauseBtn.style.display = "flex";
        stopBtn.disabled = false;

        if (state === "loading") {
            playBtn.style.display = "none";
            pauseBtn.style.display = "none";
            if (loadingSpinner) {
                loadingSpinner.style.display = "flex";
            }
            stopBtn.disabled = true;
            if (progressTrack) progressTrack.style.pointerEvents = "none";
        } else if (state === "playing") {
            playBtn.style.display = "none";
            pauseBtn.style.display = "flex";
            if (progressTrack) progressTrack.style.pointerEvents = "auto";
        } else if (state === "paused") {
            playBtn.style.display = "flex";
            pauseBtn.style.display = "none";
            if (progressTrack) progressTrack.style.pointerEvents = "auto";
        } else {
            playBtn.style.display = "flex";
            pauseBtn.style.display = "none";
            stopBtn.disabled = true;
            if (progressTrack) progressTrack.style.pointerEvents = "none";
        }
    }

    function showNotification(message, type = "info") {
        const notification = document.createElement("div");
        notification.className = `tts-notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => notification.classList.add("show"), 10);
        setTimeout(() => {
            notification.classList.remove("show");
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    function makeDraggable(el) {
        let isDragging = false;
        let currentX = 0, currentY = 0, initialX = 0, initialY = 0;

        const dragHandle = el.querySelector(".tts-drag-handle");
        dragHandle.addEventListener("mousedown", dragStart);
        dragHandle.addEventListener("touchstart", dragStart);

        function dragStart(e) {
            if (e.type === "touchstart") {
                initialX = e.touches[0].clientX - currentX;
                initialY = e.touches[0].clientY - currentY;
            } else {
                initialX = e.clientX - currentX;
                initialY = e.clientY - currentY;
            }

            isDragging = true;
            el.style.cursor = "grabbing";
            document.addEventListener("mousemove", drag);
            document.addEventListener("mouseup", dragEnd);
            document.addEventListener("touchmove", drag);
            document.addEventListener("touchend", dragEnd);
        }

        function drag(e) {
            if (!isDragging) return;
            e.preventDefault();

            let clientX, clientY;
            if (e.type === "touchmove") {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }

            currentX = clientX - initialX;
            currentY = clientY - initialY;

            const rect = el.getBoundingClientRect();
            const originalLeft = rect.left - currentX;
            const originalTop = rect.top - currentY;

            const maxX = window.innerWidth - rect.width;
            const maxY = window.innerHeight - rect.height;

            currentX = Math.max(-originalLeft, Math.min(currentX, maxX - originalLeft));
            currentY = Math.max(-originalTop, Math.min(currentY, maxY - originalTop));

            el.style.transform = `translate(${currentX}px, ${currentY}px)`;
        }

        function dragEnd() {
            isDragging = false;
            el.style.cursor = "default";
            document.removeEventListener("mousemove", drag);
            document.removeEventListener("mouseup", dragEnd);
            document.removeEventListener("touchmove", drag);
            document.removeEventListener("touchend", dragEnd);
        }
    }

    function createControls() {
        const style = document.createElement("style");
        style.textContent = `
            .tts-player-container {
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 9999;
                background: #fff;
                padding: 16px 20px;
                border-radius: 16px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08), 0 8px 32px rgba(0, 0, 0, 0.12);
                user-select: none;
                min-width: 320px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }

            .tts-drag-handle {
                cursor: grab;
                padding: 4px 0 12px;
                margin: -8px -12px 0;
                display: flex;
                justify-content: center;
            }

            .tts-drag-handle:active {
                cursor: grabbing;
            }

            .tts-drag-indicator {
                width: 32px;
                height: 4px;
                background: #dadce0;
                border-radius: 2px;
            }

            .tts-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
            }

            .tts-icon {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
            }

            .tts-title {
                flex: 1;
                font-size: 14px;
                font-weight: 500;
                color: #202124;
            }

            .tts-progress-container {
                margin: 16px 0;
            }

            .tts-progress-track {
                width: 100%;
                height: 4px;
                background: #e8eaed;
                border-radius: 2px;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }

            .tts-progress-bar {
                height: 100%;
                background: #4285f4;
                border-radius: 2px;
                width: 0%;
                transition: width 0.1s linear;
            }

            .tts-progress-spinner {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    #4285f4 50%, 
                    transparent 100%);
                animation: shimmer 1.5s infinite;
            }

            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }

            .tts-time-display {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: #5f6368;
                margin-top: 8px;
            }

            .tts-controls {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-top: 8px;
            }

            .tts-btn {
                width: 48px;
                height: 48px;
                border: none;
                border-radius: 50%;
                background: transparent;
                color: #5f6368;
                cursor: pointer;
                font-size: 18px;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            }

            .tts-btn:hover:not(:disabled) {
                background: #f1f3f4;
            }

            .tts-btn:active:not(:disabled) {
                background: #e8eaed;
            }

            .tts-btn:disabled {
                opacity: 0.4;
                cursor: not-allowed;
            }

            .tts-btn-primary {
                width: 56px;
                height: 56px;
                background: #4285f4;
                color: white;
                font-size: 20px;
            }

            .tts-btn-primary:hover:not(:disabled) {
                background: #1a73e8;
                box-shadow: 0 2px 8px rgba(66, 133, 244, 0.3);
            }

            .tts-btn-primary:active:not(:disabled) {
                background: #1765cc;
            }

            .tts-loading-container {
                width: 56px;
                height: 56px;
                display: none;
                align-items: center;
                justify-content: center;
            }

            .tts-spinner {
                width: 24px;
                height: 24px;
                border: 3px solid #e8eaed;
                border-top-color: #4285f4;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            .tts-notification {
                position: fixed;
                top: 24px;
                right: 24px;
                background: #202124;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                font-size: 14px;
                opacity: 0;
                transform: translateY(-20px);
                transition: all 0.3s ease;
                z-index: 10000;
            }

            .tts-notification.show {
                opacity: 1;
                transform: translateY(0);
            }

            .tts-notification.error {
                background: #d93025;
            }
        `;
        document.head.appendChild(style);

        const container = document.createElement("div");
        container.className = "tts-player-container";
        container.setAttribute("data-tts-ignore", "true");

        container.innerHTML = `
            <div class="tts-drag-handle">
                <div class="tts-drag-indicator"></div>
            </div>
            <div class="tts-header">
                <div class="tts-icon">🔊</div>
                <div class="tts-title">Text to Speech</div>
            </div>
            <div class="tts-progress-container">
                <div id="tts-progress-track" class="tts-progress-track">
                    <div id="tts-progress-bar" class="tts-progress-bar"></div>
                    <div class="tts-progress-spinner" style="display: none;"></div>
                </div>
                <div class="tts-time-display">
                    <span id="tts-current-time">0:00</span>
                    <span id="tts-duration">0:00</span>
                </div>
            </div>
            <div class="tts-controls">
                <button id="tts-stop-btn" class="tts-btn" title="Stop">⏹</button>
                <button id="tts-play-btn" class="tts-btn tts-btn-primary" title="Play">▶</button>
                <button id="tts-pause-btn" class="tts-btn tts-btn-primary" title="Pause" style="display: none;">⏸</button>
                <div id="tts-loading-spinner" class="tts-loading-container">
                    <div class="tts-spinner"></div>
                </div>
            </div>
        `;

        document.body.appendChild(container);

        document.getElementById("tts-play-btn").onclick = playAudio;
        document.getElementById("tts-pause-btn").onclick = pauseAudio;
        document.getElementById("tts-stop-btn").onclick = stopAudio;
        document.getElementById("tts-progress-track").onclick = seekAudio;

        makeDraggable(container);
        updateButtonStates("ready");
    }

    window.addEventListener("DOMContentLoaded", createControls);

})();