

// document.getElementById('generateBtnImageToImage').disabled = true;
// const spinner = document.querySelector('.spinner-border');
document.querySelector('.image-placeholder').querySelector('.spinner-border').style.display = 'none';


function imageCheckFormFields() {
    const imageInput = document.getElementById('imageInput').files.length > 0;
    const description = document.getElementById('description').value.trim() !== '';
    const modelType = document.getElementById('model_type').value !== '';

    console.log(`video file: ${imageInput}, description : ${description}, model type: ${modelType} `)
    console.log(`total output: ${imageInput && description && modelType}`)


    if (imageInput && description && modelType) {
        document.getElementById('generateBtnImageToImage').disabled = false;
    } else {
        document.getElementById('generateBtnImageToImage').disabled = true;
    }
}



document.getElementById('imageInput').addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const imagePreview = document.getElementById('imagePreview');
            imagePreview.innerHTML = `<img src="${e.target.result}" alt="Selected Image">`;
            // Save the image data to local storage
            sessionStorage.setItem('imagePreview', e.target.result);
        }
        reader.readAsDataURL(file);
        // document.getElementById('generateBtnImageToImage').disabled = false;
    }
    imageCheckFormFields();
});


document.getElementById('description').addEventListener('input', imageCheckFormFields);

document.getElementById('model_type').addEventListener('change',
    () => {

        imageCheckFormFields();
        document.getElementById('generateBtnImageToImage').disabled = true;
        document.getElementById('modelLoadingOverlay').style.display = 'flex';
        fetch('/loadmodel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model_type: document.getElementById('model_type').value
            })
        }).then(response => response.json())
            .then(data => {
                console.log(data);
                document.getElementById('generateBtnImageToImage').disabled = false;
                document.getElementById('modelLoadingOverlay').style.display = 'none';
            })
            .catch((error) => {
                console.error('Error:', error);
                document.getElementById('generateBtnImageToImage').disabled = false;
                document.getElementById('modelLoadingOverlay').style.display = 'none';
            });

    });



// Function to select the first image by default
function selectFirstImage() {
    const firstThumbnail = document.querySelector('.thumbnail-img');
    if (firstThumbnail) {
        firstThumbnail.classList.add('selected-thumbnail');
        document.querySelector('#displayImage').src = firstThumbnail.src;
        document.querySelector('#displayImage').style.display = 'block';
        adjustImagePlaceholderSize(firstThumbnail.src);
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
            document.querySelector('#displayImage').src = thumbnail.src;
            adjustImagePlaceholderSize(thumbnail.src);
        });
    });
}

// Add click listeners to existing thumbnails
addThumbnailClickListeners();

// Select the first image by default
selectFirstImage();


function adjustImagePlaceholderSize(imageSrc) {
    const img = new Image();
    img.onload = function () {
        const imagePlaceholder = document.querySelector('.image-placeholder');
        imagePlaceholder.style.width = `${img.width}px`;
        imagePlaceholder.style.height = `${img.height}px`;
    }
    img.src = imageSrc;
}




document.getElementById('generateBtnImageToImage').addEventListener('click', function () {
    console.log('Generating Image...1');

    document.querySelector('.image-placeholder').querySelector('.spinner-border').style.display = 'block';

});



document.getElementById('downloadAllBtn').addEventListener('click', function () {
   
    const dataValue = this.getAttribute("data-value"); // Or use: this.dataset.value


    let jsonCompatible = dataValue.replace(/'/g, '"');
    let list = JSON.parse(jsonCompatible);
 
    list.forEach((image, index) => {
        const link = document.createElement('a');   
        link.download = `output_${index}.jpg`;
        link.href = image;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});