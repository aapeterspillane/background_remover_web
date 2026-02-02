// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const error = document.getElementById('error');
const errorMessage = document.getElementById('error-message');
const originalImage = document.getElementById('original-image');
const processedImage = document.getElementById('processed-image');
const downloadBtn = document.getElementById('download-btn');
const newImageBtn = document.getElementById('new-image-btn');
const retryBtn = document.getElementById('retry-btn');

// Supported formats
const SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

// State
let processedBlob = null;
let originalFileName = null;

// Event Listeners
dropZone.addEventListener('click', (e) => {
    // Don't trigger if clicking on the label or input (they handle themselves)
    if (e.target.closest('.file-input-label')) return;
    fileInput.click();
});
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadImage);
newImageBtn.addEventListener('click', reset);
retryBtn.addEventListener('click', reset);

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Validate format
    if (!SUPPORTED_FORMATS.includes(file.type)) {
        showError('Unsupported format. Please use JPEG, PNG, WebP, or GIF.');
        return;
    }

    // Validate size
    if (file.size > MAX_FILE_SIZE) {
        showError('File too large. Maximum size is 20MB.');
        return;
    }

    processImage(file);
}

async function processImage(file) {
    showLoading();

    // Store original filename (without extension) for download
    const nameParts = file.name.split('.');
    nameParts.pop(); // Remove extension
    originalFileName = nameParts.join('.') || 'image';

    // Show original image
    const originalUrl = URL.createObjectURL(file);
    originalImage.src = originalUrl;

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Processing failed');
        }

        processedBlob = await response.blob();
        const processedUrl = URL.createObjectURL(processedBlob);
        processedImage.src = processedUrl;

        showResult();
    } catch (err) {
        showError(err.message || 'An error occurred while processing the image.');
    }
}

function downloadImage() {
    if (!processedBlob) return;

    const url = URL.createObjectURL(processedBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${originalFileName}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showLoading() {
    dropZone.classList.add('hidden');
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    error.classList.add('hidden');
}

function showResult() {
    dropZone.classList.add('hidden');
    loading.classList.add('hidden');
    result.classList.remove('hidden');
    error.classList.add('hidden');
}

function showError(message) {
    dropZone.classList.add('hidden');
    loading.classList.add('hidden');
    result.classList.add('hidden');
    error.classList.remove('hidden');
    errorMessage.textContent = message;
}

function reset() {
    dropZone.classList.remove('hidden');
    loading.classList.add('hidden');
    result.classList.add('hidden');
    error.classList.add('hidden');
    fileInput.value = '';
    processedBlob = null;
    originalFileName = null;

    // Clean up object URLs
    if (originalImage.src) {
        URL.revokeObjectURL(originalImage.src);
        originalImage.src = '';
    }
    if (processedImage.src) {
        URL.revokeObjectURL(processedImage.src);
        processedImage.src = '';
    }
}
