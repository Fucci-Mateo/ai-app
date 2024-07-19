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

    // Variables
    let uploadedImage = null;
    let ctx, drawCtx;
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    let currentGeneratedImageUrl = null;
    let brushSize = 30; // Default brush size
    let currentMode = 'draw'; // Current drawing mode

    // Event Listeners
    imageUpload.addEventListener('change', handleFileSelect);
    addCustomLightBtn.addEventListener('click', openModal);
    if (closeModal) {
        closeModal.addEventListener('click', closeModalFunction);
    }
    drawBtn.addEventListener('click', () => setMode('draw'));
    eraseBtn.addEventListener('click', () => setMode('erase'));
    clearBtn.addEventListener('click', clearCanvas);
    applyCustomLightBtn.addEventListener('click', applyCustomLight);
    generateBtn.addEventListener('click', generateImage);
    downloadBtn.addEventListener('click', downloadImage);
    brushSizeInput.addEventListener('input', updateBrushSize);

    templateItems.forEach(item => {
        item.addEventListener('click', function() {
            const template = this.dataset.template;
            drawTemplate(template);
        });
    });

    // Functions
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                uploadedImage = e.target.result;
                displayUploadedImage(uploadedImage);
                addCustomLightBtn.disabled = false;
            }
            reader.readAsDataURL(file);
        }
    }

    function displayUploadedImage(imageDataUrl) {
        uploadArea.innerHTML = '';
        const img = document.createElement('img');
        img.src = imageDataUrl;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '100%';
        img.style.objectFit = 'contain';
        img.onload = () => {
            uploadArea.appendChild(img);
            addCustomLightBtn.disabled = false;
        };
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
    
            ctx = imageCanvas.getContext('2d');
            drawCtx = drawCanvas.getContext('2d');
    
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

        console.log('Drawing/Erasing at:', x, y, 'Mode:', currentMode); // Debugging line
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
        console.log(`Mouse Pos - X: ${x}, Y: ${y}, ScaleX: ${scaleX}, ScaleY: ${scaleY}`);
        return [x, y];
    }

    function setMode(mode) {
        currentMode = mode;
        if (mode === 'erase') {
            drawCtx.globalCompositeOperation = 'destination-out';
            drawCtx.strokeStyle = 'rgba(0,0,0,1)';
        } else {
            drawCtx.globalCompositeOperation = 'source-over';
            drawCtx.strokeStyle = 'white';
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

        console.log('Mode set to:', mode); // Debugging line
    }

    function updateBrushSize() {
        brushSize = parseInt(brushSizeInput.value);
        if (isNaN(brushSize) || brushSize < 1) brushSize = 1;
        if (brushSize > 100) brushSize = 100;
        brushSizeInput.value = brushSize;
        drawCtx.lineWidth = brushSize;
        console.log('Brush size updated to:', brushSize); // Debugging line
    }

    function clearCanvas() {
        drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    }

    function drawTemplate(shape) {
        clearCanvas();
        const centerX = drawCanvas.width / 2;
        const centerY = drawCanvas.height / 2;
        const size = Math.min(drawCanvas.width, drawCanvas.height) / 4;

        drawCtx.strokeStyle = 'white';
        drawCtx.lineWidth = 2;
        drawCtx.beginPath();

        switch(shape) {
            case 'circle':
                drawCtx.arc(centerX, centerY, size, 0, 2 * Math.PI);
                break;
            case 'square':
                drawCtx.rect(centerX - size, centerY - size, size * 2, size * 2);
                break;
            case 'triangle':
                drawCtx.moveTo(centerX, centerY - size);
                drawCtx.lineTo(centerX - size, centerY + size);
                drawCtx.lineTo(centerX + size, centerY + size);
                drawCtx.closePath();
                break;
            case 'star':
                for (let i = 0; i < 5; i++) {
                    const angle = (i * 4 * Math.PI) / 5 - Math.PI / 2;
                    const x = centerX + size * Math.cos(angle);
                    const y = centerY + size * Math.sin(angle);
                    i === 0 ? drawCtx.moveTo(x, y) : drawCtx.lineTo(x, y);
                }
                drawCtx.closePath();
                break;
        }

        drawCtx.stroke();
    }

    function applyCustomLight() {
        closeModalFunction();
        // You can add code here to send the drawCanvas data to your API
    }

    function generateImage() {
        if (!uploadedImage) {
            alert('Please upload an image first.');
            return;
        }

        generatedImage.innerHTML = 'Generating results...';

        // Here you would typically send the data to your backend API
        // For demonstration, we'll just use a placeholder
        setTimeout(() => {
            const generatedImageUrl = 'https://via.placeholder.com/400x400.png?text=Generated+Image';
            generatedImage.innerHTML = `<img src="${generatedImageUrl}" alt="Generated image" style="max-width: 100%; max-height: 100%; object-fit: contain;">`;
            currentGeneratedImageUrl = generatedImageUrl;
            downloadBtn.disabled = false;
        }, 2000);
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
