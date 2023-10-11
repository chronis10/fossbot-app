//attributes for adding a new project 
let new_project_title;
let new_project_description;
let new_project_creator;
let new_project_mode;
let last_table_size = 0;
let editor = 'blockly';

function loadProjects(data) {
  console.log('load projects');

  // Get the user's name from the URL
  const userName = getParameterByName("name");

  // Check the current URL
  const currentUrl = window.location.href;

  // Filter the projects based on the creator's name and the user's role
  let projects_array;
  if (currentUrl.includes("/classroom") && userName) {
    // Apply filtering logic for the classroom URL
    projects_array = data.data.filter(project => (userName.toLowerCase() === 'teacher' && project.mode === 'classroom') || (project.creator === userName && project.mode === 'classroom'));
  } else if (!currentUrl.includes("/classroom")) {
    // Display all projects for the homepage URL
    projects_array = data.data.filter(project => project.mode === 'homepage');
  }
  console.log('projects:', projects_array);

  // Get the table body elements
  const homepageTableBody = document.getElementById("body-table-projects-homepage");
  const adminTableBody = document.getElementById("body-table-projects-admin");
  const studentTableBody = document.getElementById("body-table-projects-student");

  // Clear the existing content
  if (homepageTableBody) {
    homepageTableBody.innerHTML = "";
  }
  if (adminTableBody) {
    adminTableBody.innerHTML = "";
  }
  if (studentTableBody) {
    studentTableBody.innerHTML = "";
  }

  if (last_table_size != projects_array.length) {
    for (var i = 0; i < projects_array.length; i++) {
      const project = projects_array[i];

      // Create the project row
      const projectRow = createProjectRow(project);

      // Add the project row to the table body
      if (currentUrl.includes("/classroom")) {
        if (userName.toLowerCase() === 'teacher') {
          adminTableBody.appendChild(projectRow.cloneNode(true));
        } else {
          studentTableBody.appendChild(projectRow.cloneNode(true));
        }
      } else if (homepageTableBody) {
        homepageTableBody.appendChild(projectRow.cloneNode(true));
      }
    }
    last_table_size = projects_array.length
  }
}

function createProjectRow(project) {
  // check editor type
  var editorURL;
  var imageSrc;
  var imageSize = "50px";

  if (project['editor'] == 'blockly') {
    editorURL = "/blockly?id=" + project['project_id'];
    imageSrc = "/static//photos/blockly.png";
  } else if (project['editor'] == 'python') {
    editorURL = "/monaco?id=" + project['project_id'];
    imageSrc = "/static//photos/python-logo.png";
  }

  // Check if the current URL includes "/classroom"
  const isClassroomPage = window.location.href.includes("/classroom");

  // Add the creator's name only for the classroom page
  const creatorColumn = isClassroomPage ? '<td>' + project['creator'] + '</td>' : '';

  // Create the project row
  const row = document.createElement("tr");
  row.innerHTML =
    '<td>' + project['title'] + '</td>' +
    '<td>' + project['info'] + '</td>' +
    '<td><img src="' + imageSrc + '" alt="Logo" style="width: ' + imageSize + '; height: ' + imageSize + '"></td>' +
    creatorColumn +
    '<td>' +
    `<div id="button__controls_row">
                                <div id="button_fa_wrap_controls_table">
                                <a href="/export_project/` + project['project_id'] + `"  style="color: rgb(0, 110, 255); text-decoration: none;">
                                <i class="fa-solid fa-download"></i>
                                </a>
                                </div>` +
    '</td>' +
    '<td>' +
    `<div id="button__controls_row">
                                <div id="button_fa_wrap_controls_table">
                                <a href="`+ editorURL + `"  style="color: rgb(255, 175, 2); text-decoration: none;">
                                <i class="fa-solid fa-pencil"></i>
                                </a>
                                </div>` +
    '</td>' +
    '<td>' +
    `<div id="button_fa_wrap_controls_table">
                    <a href="#" onclick="deleteElement(this,`+ project['project_id'] + `)" style="color: rgb(199, 30, 0); text-decoration: none;">
                    <i class="fa-solid fa-trash"></i>
                    </a>
                    </div>` +
    '</td>';

  return row;
}

function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function uplodadProject() {

  document.getElementById("fileDialogId").click();
}


function createNewProject() {

  //title 
  showModalNewProjectName();

  document.getElementById("button-project-name").onclick = function () {
    //get the input value 
    new_project_title = document.getElementById("project-name-text").value

    if (new_project_title != '') {
      //close the modal 
      closeModalNewProjectName();

      //empty the input value 
      document.getElementById("project-name-text").value = "";

      if (!document.location.href.includes('classroom')) {
        new_project_creator = 'default'
        new_project_mode = 'homepage'
        //open decription modal
        showModalNewProjectDescription();
      }else {
        new_project_mode = 'classroom'
        new_project_creator = getParameterByName("name");
        showModalNewProjectDescription();
      }
    }
  }
}

async function getDescription() {
  //get the input value 
  new_project_description = document.getElementById("project-description-text").value
  editor = document.querySelector('input[type=radio][name="editor"]:checked').value;

  if (new_project_description != '') {
    //close the modal 
    closeModalNewProjectDescription();

    //empty the input value 
    document.getElementById("project-description-text").value = "";
    const result = await newProject(new_project_title, new_project_description, editor, new_project_creator, new_project_mode)
    console.log('result is ', result)
    if (editor == 'blockly') {
      window.location.replace('/blockly?id=' + result.project_id)
    } else {
      window.location.replace('/monaco?id=' + result.project_id)
    }
  }
}


// tell which process will be executed in the robot
async function playWorker(id) {
  try {
    //   const response = await fetch(`/run/${id}`, { method: 'GET' });
    //   const result = await response.json();

    const result = await executeByID(id)
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while playing the worker.');
  }
}


// tell which process will stop
async function stopWorker(id) {
  try {

    const result = await stopByID(id)
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while stopping the worker.');
  }
}

// delete project
async function deleteWorker(id) {
  try {
    const result = await deleteByID(id)
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
      // location.reload();
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while deleting the worker.');
  }
}

async function runAllWorkers() {
  try {
    const result = await runAllSerially()
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while running all the workers.');
  }
}


// document.addEventListener('DOMContentLoaded', function() {
//   var loginForm = document.getElementById("login-form");
//   if (loginForm) {
//     loginForm.addEventListener("submit", redirectToClassroom);
//   }
// });

// function redirectToClassroom(event) {
//   event.preventDefault(); // Prevent form submission

//   // Get the value of the name input field
//   var name = document.getElementById("name").value;
//   var password = document.getElementById("password").value;
//   var passwordField = document.getElementById("password-field");

//   // Check if the name is empty
//   if (name.trim() === "") {
//     showModalError('Please enter your name.');
//     return;
//   }

//   // If the password field is not displayed and the name is "teacher", show the password field
//   if (passwordField.style.display === "none" && name.toLowerCase() === "teacher") {
//     passwordField.style.display = "block";
//     return;
//   }

//   // Check if the case-insensitive name is "teacher" and the password is correct
//   if (name.toLowerCase() === "teacher" && password !== "1234") {
//     showModalError('Incorrect password.');
//     return;
//   }

//   showModalSuccess('Redirecting to classroom...');

//   // Redirect to /classroom and pass the name as a query parameter
//   window.location.href = "/classroom?name=" + encodeURIComponent(name);
// }

// function redirectToClassroom(event) {
//   event.preventDefault();

//   var name = document.getElementById("name").value;
//   var password = document.getElementById("password").value;

//   // Send an AJAX request to the server for authentication
//   fetch('/login', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ username: name, password: password })
//   })
//   .then(response => response.json())
//   .then(data => {
//     if (data.success) {
//       window.location.href = "/classroom?name=" + encodeURIComponent(name);
//     } else {
//       showModalError(data.error);
//     }
//   });
// }


function checkTeacher() {
  var name = document.getElementById("name").value;
  var passwordField = document.getElementById("password-field");

  if (name.toLowerCase() === "teacher") {
    passwordField.style.display = "block";
  } else {
    passwordField.style.display = "none";
  }
}


async function stopAllWorkers() {
  try {
    const result = await stopAllQueue()
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while stopping all the workers.');
  }
}

async function deleteFinishedWorkers() {
  try {
    const result = await deleteAllFinished()
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
      // location.reload();
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while deleting all the finished workers.');
  }
}

async function deleteAllWorkers() {
  try {
    const result = await deleteAllQueue()
    const status = result.status
    if (result.status === 'success') {
      showModalSuccess(result.message);
      // location.reload();
    } else {
      showModalError(result.message);
    }
  } catch (error) {
    console.error(error);
    showModalError('An error occurred while deleting all the finished workers.');
  }
}

async function deleteElement(el, id) {
  var tbl = el.parentNode.parentNode.parentNode.parentNode.parentNode;
  var row = el.parentNode.parentNode.parentNode.rowIndex;

  const result = await deleteProject(id)
  console.log('result is ', result)
  if (result.status == '200') {
    tbl.deleteRow(row);
    location.reload();
  } else {
    console.error('Error deleting project:', result.error_message);
  }
}

function logoutButtonClickListener() {
  const studentLogoutButton = document.getElementById('student-logout-button');
  const adminLogoutButton = document.getElementById('admin-logout-button');

  if (studentLogoutButton) {
    studentLogoutButton.addEventListener('click', function() {
      window.location.href = '/logout';
    });
  }

  if (adminLogoutButton) {
    adminLogoutButton.addEventListener('click', function() {
      window.location.href = '/logout';
    });
  }
}

async function execute_script(project_id) {
  const result = await executeScript(project_id)
  console.log('execute script result is ', result)
  if (result == "file not found") {
    showModalError("Δεν βρέθηκε εκτελέσιμος κώδικας!")
  } else if (result == "started") {
    showModalSuccess("Η εκτέλεση έχει ξεκινήσει!")
  } else {
    showModalSucces("Το πρόγραμμα εκτελείται ήδη!")
  }

}

function stop_script() {
  stopScript();
}

function showRobotName() {
  var hostname = window.location.hostname;
  let array = hostname.split("-").join(" ").split(".").join(" ");
  array = array.split(" ", 2)
  if (array[0] && array[1]) {
    document.getElementById("robot-name").innerHTML = array[0] + " " + array[1]
  } else {
    document.getElementById("robot-name").innerHTML = window.location.hostname
  }
}

function addRadioListeners() {
  document.getElementById("blockly").addEventListener("click", function () {
    editor = "blockly";
  });

  document.getElementById("python").addEventListener("click", function () {
    editor = "python";
  });
}

document.addEventListener("DOMContentLoaded", function () {
  addRadioListeners();
});


socket.on("refresh_list", (incoming) => {
  // console.log(incoming);
  // document.getElementById('terminal_scrollable-content').innerHTML+= '<p>' + incoming.data + '</p>';
  // var elem = document.getElementById('terminal_scrollable-content');
  // elem.scrollTop = elem.scrollHeight;

  alert(incoming.data);
});

socket.on('refresh_table', (data) => {
  // Get the table body
  var tableBody = document.getElementById('workers');

  // Clear the existing table rows
  while (tableBody.firstChild) {
    tableBody.removeChild(tableBody.firstChild);
  }

  // Update the table with the new data
  const workers = data.workers;
  console.log("refresh_table", workers);

  // Add each new project to the table
  for (var i = 0; i < workers.length; i++) {
    addProjectToTable(workers[i]);
  }
});

function addProjectToTable(project) {
  // Get the table body
  var tableBody = document.getElementById('workers');

  // Create a new row
  var row = document.createElement('tr');

  // Create the cells for the new row
  var indexCell = document.createElement('th');
  indexCell.scope = 'row';
  indexCell.textContent = tableBody.children.length + 1;

  var idCell = document.createElement('td');
  idCell.textContent = project.project_id;

  var userCell = document.createElement('td');
  userCell.textContent = project.user;

  var statusCell = document.createElement('td');
  statusCell.textContent = project.status;

  // Create the buttons
  var buttonCell = document.createElement('td');

  var playButton = document.createElement('button');
  playButton.className = 'btn btn-success btn-sm';
  playButton.textContent = 'Play';
  playButton.onclick = function() { playWorker(indexCell.textContent); };
  buttonCell.appendChild(playButton);

  var stopButton = document.createElement('button');
  stopButton.className = 'btn btn-danger btn-sm';
  stopButton.textContent = 'Stop';
  stopButton.onclick = function() { stopWorker(indexCell.textContent); };
  buttonCell.appendChild(stopButton);

  var deleteButton = document.createElement('button');
  deleteButton.className = 'btn btn-warning btn-sm';
  deleteButton.textContent = 'Delete';
  deleteButton.onclick = function() { deleteWorker(indexCell.textContent); };
  buttonCell.appendChild(deleteButton);

  // Append the cells to the row
  row.appendChild(indexCell);
  row.appendChild(idCell);
  row.appendChild(userCell);
  row.appendChild(statusCell);
  row.appendChild(buttonCell); // Append the button cell

  // Append the row to the table
  tableBody.appendChild(row);
}

document.addEventListener('DOMContentLoaded', function() {
  logoutButtonClickListener();
});