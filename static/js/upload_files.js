var dropZone = document.getElementById('drop-zone');
var API_URL = 'http://localhost:5000/'

dropZone.ondrop = function(e) {
    e.preventDefault();
    this.className = 'upload-drop-zone';
    if (e.dataTransfer.files.length) {
         $("#error").hide();
         $("#success").hide();
         var data = new FormData();
         data.append('file', e.dataTransfer.files[0]);
         $.ajax({
            url: API_URL + 'upload',
            method: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function(response){
                $("#success").html($("<p></p>").text(response.message || 'File saved successfully'));
                $("#error").hide();
                $("#success").show();
            },
            error: function(response) {
                $("#error").html($("<p></p>").text(response.message || 'Failed to save file'));
                $("#success").hide();
                $("#error").show();
            }
        });
    }
}

$("#js-upload-files").change(function(e) {
    var uploadFiles = document.getElementById('js-upload-files').files;
    e.preventDefault()
    for(var i = 0; i < uploadFiles.length; i++)
    checkUploadPiece(uploadFiles[i])
});

dropZone.onclick = function(e) {
    $("#js-upload-files").click();
}

dropZone.ondragover = function() {
    this.className = 'upload-drop-zone drop';
    return false;
}

dropZone.ondragleave = function() {
    this.className = 'upload-drop-zone';
    return false;
}

