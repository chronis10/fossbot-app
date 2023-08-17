//attributes for adding a new project 
let new_project_title;
let new_project_description;
let last_table_size = 0;
let editor = 'blockly';

function loadProjects(data) {
    console.log('load projects');

    //get the array with the projects
    const projects_array = data.data;
    console.log('projects:', projects_array);

    // const rows = document.getElementById("body-table-projects").rows.length;
    // if(rows >0){
    //     for(var i=1; i<=rows; i++) {
    //         document.getElementById("body-table-projects").deleteRow(i);
    //     }
    //     location.reload();
    // }


    if (last_table_size != projects_array.length) {
        for (var i = 0; i < projects_array.length; i++) {
            const project = projects_array[i];

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

            //add every time the the project name as the last row
            document.getElementById("body-table-projects").insertRow(-1).innerHTML =
                '<tr>' +
                '<td>' + project['title'] + '</td>' +
                '<td>' + project['info'] + '</td>' +
                '<td><img src="' + imageSrc + '" alt="Logo" style="width: ' + imageSize + '; height: ' + imageSize + '"></td>' +
                // '<td> ' + 
                // `<div id="button__controls_row">
                //             <div id="button_fa_wrap_controls_table">
                //             <a onclick="jsfunction()" href="javascript:runCode(` + project['project_id'] +`);"  style="color: rgb(56, 199, 0); text-decoration: none;">
                //             <i class="fa-solid fa-circle-play"></i>
                //             </a>
                //             </div>
                //             <div id="button_fa_wrap_controls_table">
                //             <a onclick="jsfunction()" href="javascript:stop_script();"  style="color: rgb(199, 30, 0); text-decoration: none;">
                //             <i class="fa-solid fa-circle-stop"></i>
                //             </a>
                //             </div>
                //         ` +

                // '</td>' +
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
                // '<div id="open-Blockly-Button-container" class="open-Blockly-Button-container">' +
                //     '<div id="open-Blockly-Button-wrap" class="open-Blockly-Button-wrap">' +
                //         '<button type="button" class="open-Blockly" id="open-Blockly">' +
                //             '<a href="/blockly?id='+ project['project_id'] +'" id="open-Blockly-href" style="color: white; text-decoration: none;">Επεξεργασία</a>' +
                //         '</button>' +
                // '</div>' +
                // '</div>' +
                '</td>' +
                '<td>' +
                `<div id="button_fa_wrap_controls_table">
                    <a href="#" onclick="deleteElement(this,`+ project['project_id'] + `)" style="color: rgb(199, 30, 0); text-decoration: none;">
                    <i class="fa-solid fa-trash"></i>
                    </a>
                    </div>` +

                //   '<div id="delete-Blockly-Button-container" class="delete-Blockly-Button-container">' +
                //             '<div id="delete-Blockly-Button-wrap" class="delete-Blockly-Button-wrap">' +
                //                 '<button onclick="deleteElement(this,'+ project['project_id'] +')" type="button" class="delete-Blockly" id="open-Blockly">' +
                //                     '<a id="open-Blockly-href" style="color: white; text-decoration: none;">Διαγραφή</a>' +
                //                 '</button>' +
                //             '</div>' +
                //         '</div>' +
                '</td>' +
                '</tr>';
        }
        last_table_size = projects_array.length
    }



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

            //open decription modal
            showModalNewProjectDescription();

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

        const result = await newProject(new_project_title, new_project_description, editor)
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