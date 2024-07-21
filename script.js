document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const uploadArea = document.getElementById('uploadArea');
    const imageUpload = document.getElementById('imageUpload');
    const addCustomLightBtn = document.getElementById('addCustomLightBtn');
    const customLightModal = document.getElementById('customLightModal');
    const closeModal = document.querySelector('.close');
    const imageCanvas = document.getElementById('imageCanvas');
    const drawCanvas = document.getElementById('drawCanvas');
    const drawBtn = document.getElementById('drawBtn');
    const eraseBtn = document.getElementById('eraseBtn');
    const clearBtn = document.getElementById('clearBtn');
    const applyCustomLightBtn = document.getElementById('applyCustomLightBtn');
    const generateBtn = document.getElementById('generateBtn');
    const generatedImage = document.getElementById('generatedImage');
    const downloadBtn = document.getElementById('downloadBtn');
    const templateItems = document.querySelectorAll('.template-item');
    const brushSizeInput = document.getElementById('BrushPx');
    const positivePromptInput = document.getElementById('positivePrompt');
    const negativePromptInput = document.getElementById('negativePrompt');
    
    // Variables
    const templateImages = {};
    let uploadedImage = null;
    let isUploading = false;
    let ctx, drawCtx;
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let currentGeneratedImageUrl = null;
    let brushSize = 30; // Default brush size
    let currentMode = 'draw'; // Current drawing mode
    let isProcessingClick = false;
    let uploadedImageBin = null;
    let LightMaskBin = null;

    // Event Listeners
    const handleUploadAreaClick = function(event) {
        if (isProcessingClick) return;
        isProcessingClick = true;

        console.log('Upload area clicked');
        event.preventDefault();
        event.stopPropagation();
        
        imageUpload.click();

        setTimeout(() => {
            isProcessingClick = false;
        }, 500);  // Prevent additional clicks for 500ms
    };
    
    uploadArea.addEventListener('click', handleUploadAreaClick);
    imageUpload.addEventListener('change', handleFileSelect);
    
    addCustomLightBtn.addEventListener('click', openModal);
    if (closeModal) {
        closeModal.addEventListener('click', closeModalFunction);
    }
    drawBtn.addEventListener('click', () => setMode('draw'));
    eraseBtn.addEventListener('click', () => setMode('erase'));
    clearBtn.addEventListener('click', clearCanvas);
    applyCustomLightBtn.addEventListener('click', applyCustomLight);
    downloadBtn.addEventListener('click', downloadImage);
    brushSizeInput.addEventListener('input', updateBrushSize);

    generateBtn.addEventListener('click', function() {
    const positivePrompt = positivePromptInput.value.trim();
    const negativePrompt = negativePromptInput.value.trim();
    
    if (!positivePrompt) {
        alert('Please enter a positive prompt.');
        return;
    }
    
    generateImage(positivePrompt, negativePrompt);
});
    

templateItems.forEach(item => {
    const template = item.dataset.template;
    const imageUrl = item.style.backgroundImage.slice(4, -1).replace(/"/g, "");
    
    // Preload the image
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
        templateImages[template] = img;
    };

    item.addEventListener('click', function() {
        drawTemplateImage(template);
    });
});
    
    // Functions
    function handleFileSelect(event) {
        const file = event.target.files[0];
        uploadedImageBin = file;
        if (!file) {
            return;
        }
    
        console.log('File details:', {
            name: file.name,
            type: file.type,
            size: file.size,
            lastModified: new Date(file.lastModified).toISOString()
        });
    
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                uploadedImage = e.target.result;
                displayUploadedImage(uploadedImage);
                addCustomLightBtn.disabled = false;
                clearCanvas(); // Clear the canvas after the image is loaded
            }
            reader.readAsDataURL(file);
        } else {
            console.log('Invalid file type selected');
        }
    
        // Reset the input to allow selecting the same file again
        event.target.value = '';
        console.log('File input value after reset:', event.target.value);
    }

    function displayUploadedImage(imageDataUrl) {
        uploadArea.innerHTML = '';
        const img = document.createElement('img');
        img.src = imageDataUrl;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '100%';
        img.style.objectFit = 'contain';
        uploadArea.appendChild(img);
    }

    function openModal() {
        if (uploadedImage) {
            customLightModal.style.display = 'block';
            initializeCanvases();
        } else {
            alert('Please upload an image first.');
        }
    }

    function closeModalFunction() {
        customLightModal.style.display = 'none';
    }

    function initializeCanvases() {
        const img = new Image();
        img.onload = function() {
            const container = document.getElementById('canvasContainer');
            const containerRect = container.getBoundingClientRect();
            const imageWidth = img.width;
            const imageHeight = img.height;
            const aspectRatio = imageWidth / imageHeight;
            let canvasWidth, canvasHeight;
    
            if (containerRect.width / containerRect.height > aspectRatio) {
                canvasHeight = containerRect.height;
                canvasWidth = canvasHeight * aspectRatio;
            } else {
                canvasWidth = containerRect.width;
                canvasHeight = canvasWidth / aspectRatio;
            }
    
            // Set canvas dimensions
            imageCanvas.width = drawCanvas.width = canvasWidth;
            imageCanvas.height = drawCanvas.height = canvasHeight;
            imageCanvas.style.width = drawCanvas.style.width = canvasWidth + 'px';
            imageCanvas.style.height = drawCanvas.style.height = canvasHeight + 'px';
    
            ctx = imageCanvas.getContext('2d');
            drawCtx = drawCanvas.getContext('2d', { willReadFrequently: true });
    
            ctx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
            drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    
            // Draw the image on the canvas
            ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
    
            drawCtx.lineCap = 'round';
            drawCtx.lineJoin = 'round';
    
            drawCanvas.addEventListener('mousedown', startDrawing);
            drawCanvas.addEventListener('mousemove', draw);
            drawCanvas.addEventListener('mouseup', stopDrawing);
            drawCanvas.addEventListener('mouseout', stopDrawing);
    
            setMode('draw'); // Set initial mode to draw
            updateBrushSize(); // Initialize brush size
        };
        img.src = uploadedImage;
    }
    function startDrawing(e) {
        isDrawing = true;
        [lastX, lastY] = getMousePos(drawCanvas, e);
    }

    function draw(e) {
        if (!isDrawing) return;

        const [x, y] = getMousePos(drawCanvas, e);

        drawCtx.beginPath();
        drawCtx.moveTo(lastX, lastY);
        drawCtx.lineTo(x, y);
        drawCtx.stroke();

        [lastX, lastY] = [x, y];
    }

    function stopDrawing() {
        isDrawing = false;
    }

    function getMousePos(canvas, e) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        return [x, y];
    }

    function setMode(mode) {
        currentMode = mode;
        if (mode === 'erase') {
            drawCtx.globalCompositeOperation = 'destination-out';
            drawCtx.strokeStyle = 'rgba(0,0,0,1)';
        } else {
            drawCtx.globalCompositeOperation = 'source-over';
            drawCtx.strokeStyle = 'red';
        }
        drawCtx.lineWidth = brushSize;

        // Update button styles
        drawBtn.classList.remove('selected');
        eraseBtn.classList.remove('selected');
        if (mode === 'draw') {
            drawBtn.classList.add('selected');
        } else if (mode === 'erase') {
            eraseBtn.classList.add('selected');
        }
    }

    function updateBrushSize() {
        brushSize = parseInt(brushSizeInput.value);
        if (isNaN(brushSize) || brushSize < 1) brushSize = 1;
        if (brushSize > 100) brushSize = 100;
        brushSizeInput.value = brushSize;
        drawCtx.lineWidth = brushSize;
    }

    function clearCanvas() {
        if (drawCtx) {
            drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
        } else {
            console.log('Drawing context not initialized yet, skipping canvas clear');
        }
    }

    function drawTemplateImage(template) {
        if (!drawCtx || !templateImages[template]) {
            console.log('Drawing context not initialized or template image not loaded');
            return;
        }
    
        clearCanvas();
    
        const img = templateImages[template];
        const scale = Math.min(drawCanvas.width / img.width, drawCanvas.height / img.height);
        const x = (drawCanvas.width / 2) - (img.width / 2) * scale;
        const y = (drawCanvas.height / 2) - (img.height / 2) * scale;
    
        drawCtx.drawImage(img, x, y, img.width * scale, img.height * scale);
    }

    function applyCustomLight() {
        // Close the modal
        closeModalFunction();

        // Create a temporary canvas to combine the image and drawing
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');

        // Set the temporary canvas dimensions to match the image canvas
        tempCanvas.width = imageCanvas.width;
        tempCanvas.height = imageCanvas.height;

        // Draw the uploaded image onto the temporary canvas
        tempCtx.drawImage(imageCanvas, 0, 0);

        // Set the opacity for the drawing layer
        tempCtx.globalAlpha = 0.3; // Adjust opacity here (0.0 to 1.0)

        // Draw the user drawing on top of the image
        tempCtx.drawImage(drawCanvas, 0, 0);

        // Reset the global alpha to default
        tempCtx.globalAlpha = 1.0;

        // Convert the combined canvas to a data URL
        const combinedImageUrl = tempCanvas.toDataURL('image/png');

        // Display the combined image in the main container
        const img = document.createElement('img');
        img.src = combinedImageUrl;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '100%';
        img.style.objectFit = 'contain';

        // Clear the previous content and append the new combined image
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = '';
        uploadArea.appendChild(img);

        // Enable the download button
        currentGeneratedImageUrl = combinedImageUrl;
        downloadBtn.disabled = false;

        // Create a temporary canvas to save the drawing with black background
        const blackBackgroundCanvas = document.createElement('canvas');
        const blackBackgroundCtx = blackBackgroundCanvas.getContext('2d');

        // Set the temporary canvas dimensions to match the drawCanvas
        blackBackgroundCanvas.width = drawCanvas.width;
        blackBackgroundCanvas.height = drawCanvas.height;

        // Fill the canvas with black
        blackBackgroundCtx.fillStyle = 'black';
        blackBackgroundCtx.fillRect(0, 0, blackBackgroundCanvas.width, blackBackgroundCanvas.height);

        // Draw the user drawing on top of the black background
        blackBackgroundCtx.drawImage(drawCanvas, 0, 0);

        // Convert the canvas to a Blob
        blackBackgroundCanvas.toBlob(function(blob) {
            // Store the Blob in LightMaskBin
            LightMaskBin = blob;
        }, 'image/png');
    }

    async function uploadToBackend(img) {
        if (!img) {
            console.error('No image selected');
            return null;
        }
    
        const formData = new FormData();
        formData.append('file', img);
    
        try {
            const response = await fetch('http://34.116.202.145:9099/upload', {
                method: 'POST',
                body: formData
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }
    
            const data = await response.json();
            console.log('Upload successful:', data);
            return data;
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }
    
    function renderResult(url) {
        generatedImage.innerHTML = `<img src="${url}" alt="Generated image" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;">`;
        currentGeneratedImageUrl = url;
        downloadBtn.disabled = false;
    }

    async function generateImage(positivePrompt, negativePrompt) {
        try {
            const ProductImageUrl = await uploadToBackend(uploadedImageBin);
            const LightMaskUrl = await uploadToBackend(LightMaskBin);
            
            console.log('ProductImageUrl:', ProductImageUrl);
            console.log('LightMaskUrl:', LightMaskUrl);
            console.log('Positive Prompt:', positivePrompt);
            console.log('Negative Prompt:', negativePrompt);
    
            const response = await fetch('http://34.116.202.145:9099/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    productimageurl: ProductImageUrl.secure_url,
                    lightmaskurl: LightMaskUrl.secure_url,
                    positiveprompt: positivePrompt,
                    negativeprompt: negativePrompt
                })
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Generation failed');
            }
    
            const data = await response.json();
            console.log('Generation successful:', data);
    
            // Render the generated image
            if (data.image_url) {
                const generatedImg = document.getElementById('generatedImage');
                generatedImg.innerHTML = `<img src="${data.image_url}" alt="Generated image" style="max-width: 100%; max-height: 100%; object-fit: contain;">`;
                
                // Update the currentGeneratedImageUrl for the download function
                currentGeneratedImageUrl = data.image_url;
                
                // Enable the download button
                downloadBtn.disabled = false;
            } else {
                console.error('No image URL in the response');
            }
    
            return data.image_url;
        } catch (error) {
            console.error('Generation error:', error);
            alert('Failed to generate image. Please try again.');
            throw error;
        }
    }

    

    function downloadImage() {
        if (currentGeneratedImageUrl) {
            const link = document.createElement('a');
            link.href = currentGeneratedImageUrl;
            link.download = 'generated_image.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert('No image has been generated yet.');
        }
    }

    // Initialize
    addCustomLightBtn.disabled = true;
    downloadBtn.disabled = true;
});