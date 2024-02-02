let newProjectTitle;
let newProjectDescription;
let lastTableSize = 0;

function loadProjects(data) {
    console.log('load projects');
    const projectsArray = data.data;
    console.log('projects:', projectsArray);
    
    if (lastTableSize !== projectsArray.length) {
        const tableBody = document.getElementById("body-table-projects");
        tableBody.innerHTML = '';  // Clear existing content
        projectsArray.forEach(project => {
            tableBody.appendChild(createProjectRow(project));
        });
        lastTableSize = projectsArray.length;
    }
}

function createProjectRow(project) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${project['title']}</td>
        <td>${project['info']}</td>
        <td><a href="/export_project/${project['project_id']}" class="button-style"><i class="fa-solid fa-download"></i></a></td>
        <td><a href="/blockly?id=${project['project_id']}" class="button-style"><i class="fa-solid fa-pencil" style="color: orange;"></i></a></td>
        <td><a href="#" onclick="deleteProject(${project['project_id']})" class="button-style"><i class="fa-solid fa-trash" style="color: red;"></i></a></td>`;
    return row;
}

function createNewProject() {
    showModalNewProjectName();
    document.getElementById("button-project-name").onclick = function () {
        newProjectTitle = getInputValue("project-name-text");
        if (newProjectTitle) {
            closeModalNewProjectName();
            showModalNewProjectDescription();
        }
    }
    
}

function uplodadProject() {
    document.getElementById("fileDialogId").click();
}

async function getDescription() {
    newProjectDescription = getInputValue("project-description-text");
    if (newProjectDescription) {
        closeModalNewProjectDescription();
        try {
            const result = await newProject(newProjectTitle, newProjectDescription);
            console.log('result is ', result);
            window.location.replace(`/blockly?id=${result.project_id}`);
        } catch (error) {
            console.error('Error creating new project:', error);
        }
    }
}

async function deleteProject(projectId) {
    try {
        const result = await deleteProjectById(projectId);
        if (result.status === '200') {
            removeProjectFromTable(projectId);
        } else {
            console.error('Error deleting project:', result);
        }
    } catch (error) {
        console.error('Error deleting project:', error);
    }
}

function showRobotName() {
    const hostname = window.location.hostname;
    const nameParts = hostname.split("-").join(" ").split(".").join(" ").split(" ", 2);
    const robotName = nameParts.length >= 2 ? nameParts.join(" ") : hostname;
    document.getElementById("robot-name").innerHTML = robotName;
}

function removeProjectFromTable(projectId) {
    const tableBody = document.getElementById("body-table-projects");
    for (let i = 0; i < tableBody.rows.length; i++) {
        if (tableBody.rows[i].querySelector(`a[href*='${projectId}']`)) {
            tableBody.deleteRow(i);
            break;
        }
    }
}

function getInputValue(elementId) {
    return document.getElementById(elementId).value.trim();
}
