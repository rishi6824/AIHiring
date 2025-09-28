// Voice Recognition Handler
class VoiceRecognition {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.audioContext = null;
        this.analyser = null;
        this.mediaStreamSource = null;
        this.animationId = null;
        this.onResultCallback = null;
        
        this.initializeRecognition();
    }
    
    initializeRecognition() {
        // Check if browser supports speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;
            
            this.recognition.onstart = () => {
                this.isListening = true;
                console.log('Voice recognition started');
            };
            
            this.recognition.onresult = (event) => {
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                // Call the callback with the results
                if (this.onResultCallback) {
                    this.onResultCallback(finalTranscript || interimTranscript);
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopListening();
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                console.log('Voice recognition ended');
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
        }
    }
    
    initialize(stream) {
        // Set up audio visualization
        this.setupAudioVisualization(stream);
    }
    
    setupAudioVisualization(stream) {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.mediaStreamSource = this.audioContext.createMediaStreamSource(stream);
            
            this.analyser.fftSize = 256;
            this.mediaStreamSource.connect(this.analyser);
            
            this.setupVisualizer();
        } catch (e) {
            console.log('Audio visualization not supported:', e);
        }
    }
    
    setupVisualizer() {
        const canvas = document.getElementById('visualizer');
        const canvasCtx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const draw = () => {
            this.animationId = requestAnimationFrame(draw);
            
            if (!this.isListening) return;
            
            this.analyser.getByteFrequencyData(dataArray);
            
            canvasCtx.fillStyle = 'rgb(0, 0, 0)';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
            
            const barWidth = (canvas.width / bufferLength) * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                
                canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        };
        
        draw();
    }
    
    startListening() {
        if (this.recognition && !this.isListening) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Error starting speech recognition:', error);
            }
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
        
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
    
    set onResult(callback) {
        this.onResultCallback = callback;
    }
}



// Global instance
const voiceRecognition = new VoiceRecognition();

// Check browser support
if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    console.warn('Speech recognition not supported in this browser');
    
    // Show a message to the user
    document.addEventListener('DOMContentLoaded', function() {
        const voiceSection = document.querySelector('.voice-section');
        if (voiceSection) {
            voiceSection.innerHTML = `
                <div style="text-align: center; padding: 1rem; color: #666;">
                    <p>⚠️ Voice input is not supported in your browser.</p>
                    <p>Please use Chrome, Edge, or Safari for voice features.</p>
                    <p>You can still type your answers below.</p>
                </div>
            `;
        }
    });
}