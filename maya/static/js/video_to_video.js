

document.getElementById('generateButtonVideo').disabled = true;
document.querySelector('.spinner-border').style.display = 'none';



function checkFormFields() {
  const imageInput = document.getElementById('videoFile').files.length > 0;
  const description = document.getElementById('description').value.trim() !== '';
  const modelType = document.getElementById('model_type').value !== '';


  if (imageInput && description && modelType) {
    document.getElementById('generateButtonVideo').disabled = false;
  } else {
    document.getElementById('generateButtonVideo').disabled = true;
  }
}



document.getElementById('videoFile').addEventListener('change', function (e) {
  const file = e.target.files[0];
  if (file) {
      const video = document.createElement('video');
      video.src = URL.createObjectURL(file);

      video.addEventListener('loadeddata', function () {
          // Get the first frame
          const canvas = document.getElementById('framePreview');
          const context = canvas.getContext('2d');

          // Set canvas dimensions to match video
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;

          // Draw the first frame
          context.drawImage(video, 0, 0, canvas.width, canvas.height);

          // Show the canvas and Copilot link
          canvas.style.display = 'block';
          // document.getElementById('downloadFrame').style.display = 'block';
          // Create Copilot link with frame data
          const frameData = canvas.toDataURL('image/jpeg');
          const copilotLink = document.getElementById('copilotLink');
          copilotLink.style.display = 'block';
          copilotLink.querySelector('a').href = `https://copilot.microsoft.com/?desc=${encodeURIComponent('Describe this video frame:')}`;

          // Enable generate button
          // document.getElementById('generateButtonVideo').disabled = false;
      });

      // Show video preview
      const videoPreview = document.getElementById('videoPreview');
      videoPreview.src = URL.createObjectURL(file);
      videoPreview.style.display = 'block';
      document.getElementById('videoPreviewtext').style.display = 'none';
  }

  checkFormFields();
});


// Add download function
function downloadFrame() {
  const canvas = document.getElementById('framePreview');
  const videoFile = document.getElementById('videoFile').files[0];

  if (canvas && videoFile) {
      // Create a download link
      const link = document.createElement('a');

      // Get the filename without extension
      const baseFileName = videoFile.name.replace(/\.[^/.]+$/, "");

      // Set the download attributes
      link.download = `${baseFileName}_frame.jpg`;
      link.href = canvas.toDataURL('image/jpeg', 0.8);

      // Trigger the download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  }
}



document.getElementById('description').addEventListener('input', checkFormFields);

document.getElementById('model_type').addEventListener('change', () => {

  checkFormFields();

  document.getElementById('generateButtonVideo').disabled = true;

  fetch('/loadvideomodel', {
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
      document.getElementById('generateButtonVideo').disabled = false;

    })
    .catch((error) => {
      console.error('Error:', error);
      document.getElementById('generateButtonVideo').disabled = false;
    });
});



document.getElementById('generateButtonVideo').addEventListener('click', function (event) {

  console.log('clicked ' + (document.getElementById('videoFile').files.length > 0));

  document.querySelector('.spinner-border').style.display = 'block';

});


document.getElementById("flexCheckChecked").addEventListener("change", function() {
  let button = document.getElementById("generateButtonVideo");
  var status = document.getElementById("checkbox");
  if (this.checked) {
      button.textContent = "Check Style ";
      status.value = "style"
  } else {
      button.textContent = "Generate Video";
      status.value = "video"
  }
});