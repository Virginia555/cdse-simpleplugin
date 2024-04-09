function startTesting() {
    document.getElementById('testingMessage').style.display = 'block';
}

document.getElementById('testForm').addEventListener('submit', function(event) {
    var test_checkboxes = document.getElementsByName('tests');
    var prov_checkboxes = document.getElementsByName('providers');
    var container_name = document.getElementById('container_name').value.trim();
    var validDockerName = /^[a-zA-Z0-9][a-zA-Z0-9_.-]*$/;
    var isCheckedTest = false;
    var isCheckedProv = false;


    for (var i = 0; i < test_checkboxes.length; i++) {
        if (test_checkboxes[i].checked) {
            isCheckedTest = true;
            break;
        }
    }
    for (var i = 0; i < prov_checkboxes.length; i++) {
        if (prov_checkboxes[i].checked) {
            isCheckedProv = true;
            break;
        }
    }

    if (!isCheckedTest) {
        event.preventDefault();
        alert('Please check at least one test scenario.');
    }
    else if (!isCheckedProv) {
        event.preventDefault();
        alert('Please check at least one Provider.');
    }
    else if (container_name.length<2){
        event.preventDefault();
        alert('Container names must have more than one letter.');
    }
    else if (!validDockerName.test(container_name)) {
        event.preventDefault();
        alert('Please enter a valid Docker container name.\nValid name starts with an alphanumeric character and can contain underscores (_), hyphens (-), and dots (.)');
    }
    else
        startTesting();
});