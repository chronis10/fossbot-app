var editor = null;

require.config({ paths: { vs: '../static/js/monaco-editor/min/vs' } });

require(['vs/editor/editor.main'], function () {
  editor = monaco.editor.create(document.getElementById('container'), {
    value: ['#The robot object is "robot"', '#Example of usage: ', 'robot.move_forward_default()'].join('\n'),
    language: 'python',
    theme: 'vs-dark',
    fontSize: '18px'
  });
});

function getMonacoXmlText() {
  var code = editor.getValue();
  return code;
}


function loadXmlIntoMonaco(code) {
  if (code !== null) {
    editor.setValue(code);
  }
}

async function loadProjectFromDB() {
  const id = new URL(window.location.href).searchParams.get("id");
  console.log("project id", id);

  if (id) {
    try {
      const result = await sendXml(id);
      if (result.status === '200') {
        loadXmlIntoMonaco(result.data);
      } else {
        throw new Error('Load Error');
      }
    } catch (error) {
      console.error('Error when getting project', error);
      showModalError("Error on code loading!");
    }
  }
}

//send the code from the workspace to run on the robot 
async function runMonacoCode(id) {
  let monacoCode = editor.getValue();
  if (!monacoCode) {
    console.log("no code to run");
    showModalError("No Code detected!");
    return;
  }

  try {
    const result = await sendMonacoCode(id, monacoCode);

    console.log("sendMonacoCode result", result);
    if (result === '200') {

      showModalSuccess("The program started!");
      if (id!=-1) {
        await saveXmlToDB(id); // Save after running the code
      }
    } else {
      showModalError("Error in running the code.");
    }
  } catch (error) {
    showModalError("Error in running the code.")
  }
}

// //stop the code that was being exeuted in the robot 
// function stopScript() {
//   stopScript();
// }

async function saveXmlToDB(id) {
  let xmlText = getMonacoXmlText();

  try{
    const result = await saveXml(id, xmlText)
    if (result.status === '200') {
      showModalSuccess("Project Saved!");
    } else {
      throw new Error('Save Error');
    }
  } catch (error) {
    showModalError("Error on saving!");
  }
}

// Open accordion tabs
var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function () {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight) {
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

// Copy function
function copyFunction(functionName) {
  const textarea = document.createElement('textarea');
  textarea.value = functionName;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  showModalSuccess("Copied to clipboard!");
}

// Resize editor window
window.addEventListener('resize', function () {
  if (editor) {
    editor.layout();
  }
});