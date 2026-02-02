// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const loadingText = document.getElementById('loading-text');
const progressBar = document.getElementById('progress-bar');
const progressFill = document.getElementById('progress-fill');
const result = document.getElementById('result');
const singleResult = document.getElementById('single-result');
const batchResult = document.getElementById('batch-result');
const batchSummary = document.getElementById('batch-summary');
const batchGrid = document.getElementById('batch-grid');
const error = document.getElementById('error');
const errorMessage = document.getElementById('error-message');
const originalImage = document.getElementById('original-image');
const processedImage = document.getElementById('processed-image');
const downloadBtn = document.getElementById('download-btn');
const downloadZipBtn = document.getElementById('download-zip-btn');
const newImageBtn = document.getElementById('new-image-btn');
const retryBtn = document.getElementById('retry-btn');

// Supported formats
const SUPPORTED_FORMATS = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB

// State
let processedResults = []; // Array of {name, blob}

// Event Listeners
dropZone.addEventListener('click', (e) => {
    if (e.target.closest('.file-input-label')) return;
    fileInput.click();
});
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadSingleImage);
downloadZipBtn.addEventListener('click', downloadAllAsZip);
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

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
        handleFiles(files);
    }
});

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    // Filter valid files
    const validFiles = files.filter(file => {
        if (!SUPPORTED_FORMATS.includes(file.type)) {
            console.warn(`Skipping ${file.name}: unsupported format`);
            return false;
        }
        if (file.size > MAX_FILE_SIZE) {
            console.warn(`Skipping ${file.name}: file too large`);
            return false;
        }
        return true;
    });

    if (validFiles.length === 0) {
        showError('No valid images found. Please use JPEG, PNG, WebP, or GIF (max 20MB each).');
        return;
    }

    processImages(validFiles);
}

async function processImages(files) {
    showLoading();
    processedResults = [];

    const total = files.length;
    const isBatch = total > 1;

    if (isBatch) {
        progressBar.classList.remove('hidden');
    }

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        loadingText.textContent = isBatch
            ? `Processing ${i + 1} of ${total}: ${file.name}`
            : 'Processing image...';

        if (isBatch) {
            progressFill.style.width = `${((i) / total) * 100}%`;
        }

        try {
            const blob = await processOneImage(file);
            const nameParts = file.name.split('.');
            nameParts.pop();
            const baseName = nameParts.join('.') || 'image';

            processedResults.push({
                name: `${baseName}.png`,
                blob: blob,
                originalUrl: URL.createObjectURL(file)
            });
        } catch (err) {
            console.error(`Failed to process ${file.name}:`, err);
            // Continue with other files
        }
    }

    if (isBatch) {
        progressFill.style.width = '100%';
    }

    if (processedResults.length === 0) {
        showError('All images failed to process. Please try again.');
        return;
    }

    showResults();
}

async function processOneImage(file) {
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

    return await response.blob();
}

function downloadSingleImage() {
    if (processedResults.length === 0) return;

    const result = processedResults[0];
    const url = URL.createObjectURL(result.blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = result.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function downloadAllAsZip() {
    if (processedResults.length === 0) return;

    downloadZipBtn.disabled = true;
    downloadZipBtn.textContent = 'Creating ZIP...';

    try {
        const zip = new JSZip();

        for (const result of processedResults) {
            zip.file(result.name, result.blob);
        }

        const content = await zip.generateAsync({ type: 'blob' });
        const url = URL.createObjectURL(content);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'background-removed-images.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (err) {
        console.error('Failed to create ZIP:', err);
        alert('Failed to create ZIP file. Please try downloading images individually.');
    } finally {
        downloadZipBtn.disabled = false;
        downloadZipBtn.textContent = 'Download All (ZIP)';
    }
}

function showLoading() {
    dropZone.classList.add('hidden');
    loading.classList.remove('hidden');
    result.classList.add('hidden');
    error.classList.add('hidden');
    progressBar.classList.add('hidden');
    progressFill.style.width = '0%';
}

function showResults() {
    dropZone.classList.add('hidden');
    loading.classList.add('hidden');
    result.classList.remove('hidden');
    error.classList.add('hidden');

    const isBatch = processedResults.length > 1;

    if (isBatch) {
        // Show batch results
        singleResult.classList.add('hidden');
        batchResult.classList.remove('hidden');
        downloadBtn.classList.add('hidden');
        downloadZipBtn.classList.remove('hidden');

        batchSummary.textContent = `Successfully processed ${processedResults.length} images`;
        batchGrid.innerHTML = '';

        for (const result of processedResults) {
            const item = document.createElement('div');
            item.className = 'batch-item';

            const img = document.createElement('img');
            img.src = URL.createObjectURL(result.blob);
            img.alt = result.name;

            const name = document.createElement('p');
            name.textContent = result.name;

            item.appendChild(img);
            item.appendChild(name);
            batchGrid.appendChild(item);
        }
    } else {
        // Show single result
        singleResult.classList.remove('hidden');
        batchResult.classList.add('hidden');
        downloadBtn.classList.remove('hidden');
        downloadZipBtn.classList.add('hidden');

        const result = processedResults[0];
        originalImage.src = result.originalUrl;
        processedImage.src = URL.createObjectURL(result.blob);
    }
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

    // Clean up object URLs
    for (const result of processedResults) {
        if (result.originalUrl) {
            URL.revokeObjectURL(result.originalUrl);
        }
    }
    processedResults = [];

    // Reset UI elements
    singleResult.classList.remove('hidden');
    batchResult.classList.add('hidden');
    downloadBtn.classList.remove('hidden');
    downloadZipBtn.classList.add('hidden');
    batchGrid.innerHTML = '';
    originalImage.src = '';
    processedImage.src = '';
}
