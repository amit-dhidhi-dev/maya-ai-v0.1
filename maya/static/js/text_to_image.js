

// Handle ratio selection
const ratioOptions = document.querySelectorAll('.ratio-option');
const selectedRatioInput = document.getElementById('selectedRatio');
const widthInput = document.getElementById('width');
const heightInput = document.getElementById('height');

// document.getElementById('generateBtnTextToImage').disabled = true;
document.querySelector('.image-placeholder').querySelector('.spinner-border').style.display = 'none';

ratioOptions.forEach(option => {
    option.addEventListener('click', () => {
        // Remove selected class from all options
        ratioOptions.forEach(opt => opt.classList.remove('selected'));
        // Add selected class to the clicked option
        option.classList.add('selected');
        // Update the hidden input value
        selectedRatioInput.value = option.getAttribute('data-ratio');
        const img = document.querySelector('.image-placeholder');
        const ratioString = option.getAttribute('data-ratio');
        const [widthRatio, heightRatio] = ratioString.split(':').map(Number);

        if (widthRatio > heightRatio) {
            height = 512;
            width = Math.floor(height * (widthRatio / heightRatio));
            img.style.width = `${width}px`; // Set the width
            img.style.height = `${height}px`; // Set the height
        }
        else if (widthRatio < heightRatio) {
            width = 512;
            height = Math.floor(width * (heightRatio / widthRatio));
            img.style.width = `${width}px`; // Set the width
            img.style.height = `${height}px`; // Set the height
        }
        else {
            width = 512;
            height = Math.floor(width * (heightRatio / widthRatio));
            img.style.width = `${width}px`; // Set the width
            img.style.height = `${height}px`; // Set the height
        }
        // make width and height should be divisiable by 8
        widthInput.value = 8 * Math.floor(width/8);
        heightInput.value = 8 * Math.floor(height/8);
    });
});

function checkPrompt() {
    const prompt = document.getElementById('description').value.trim() !== '';
    if (prompt) {
        document.getElementById('generateBtnTextToImage').disabled = false;
    } else {
        document.getElementById('generateBtnTextToImage').disabled = true;
    }
}


document.getElementById('description').addEventListener('input', checkPrompt);



var selectedRatioValue = selectedRatioInput.value;
// Select the 1:1 ratio option by default
if (selectedRatioValue.trim() === '') {
    selectedRatioValue = '1:1';
}
var item = '.ratio-option[data-ratio="1:1"]'
item = ".ratio-option[data-ratio='" + selectedRatioValue.trim() + "']"
// item = ".ratio-option[data-ratio='9:16']"
document.querySelector(item).click();



const displayImage = document.getElementById('displayImage');

// Function to select the first image by default
function selectFirstImage() {
    const firstThumbnail = document.querySelector('.thumbnail-img');
    if (firstThumbnail) {
        firstThumbnail.classList.add('selected-thumbnail');
        displayImage.src = firstThumbnail.src;
        displayImage.style.display = 'block';
    }
}

// Add click listeners to thumbnails
function addThumbnailClickListeners() {
    const thumbnails = document.querySelectorAll('.thumbnail-img');
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', () => {
            document.querySelectorAll('.thumbnail-img').forEach(img => img.classList.remove('selected-thumbnail'));
            // Add the selected class to the clicked thumbnail
            thumbnail.classList.add('selected-thumbnail');
            displayImage.src = thumbnail.src;
        });
    });
}

// Add click listeners to existing thumbnails
addThumbnailClickListeners();

// Select the first image by default
selectFirstImage();

document.getElementById('textToImageForm').addEventListener('submit', function (e) {
    // e.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.disabled = true; // Disable the submit button

    const imagePlaceholder = document.querySelector('.image-placeholder');

    // Show loading effect
    imagePlaceholder.querySelector('.spinner-border').style.display = 'block';
    displayImage.style.display = 'none';

});

// load model 
document.getElementById('model_type_for_text').addEventListener('change',
    () => {


        // Show loading overlay
        const loadingOverlay = document.getElementById('modelLoadingOverlay');
        loadingOverlay.style.display = 'flex';

        console.log('model_type_for_text');
        document.getElementById('generateBtnTextToImage').disabled = true;

        fetch('/loadmodelfortext', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model_type_for_text: document.getElementById('model_type_for_text').value
            })
        }).then(response => response.json())
            .then(data => {
                console.log(data);
                // Hide loading overlay
                loadingOverlay.style.display = 'none';
                document.getElementById('generateBtnTextToImage').disabled = false;
                checkPrompt();

            })
            .catch((error) => {
                console.error('Error:', error);
                // Hide loading overlay
                loadingOverlay.style.display = 'none';
                document.getElementById('generateBtnTextToImage').disabled = false;
                checkPrompt();
            });



    });
