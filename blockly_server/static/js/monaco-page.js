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

function getCode() {
  var code = editor.getValue();
  // var terminal = document.getElementById('terminal_scrollable-content');

  // var codeLines = code.split('\n');  // Split the code string into an array of lines
  // for (var i = 0; i < codeLines.length; i++) {
  //   // Print each line separately
  //   terminal.innerHTML += '<p>' + codeLines[i] + '</p>';
  // }
  return code;
}

function loadXml(xml) {
  if (xml !== null) {
    const dom = Blockly.Xml.textToDom(xml);
    Blockly.mainWorkspace.clear();
    Blockly.Xml.domToWorkspace(dom, Blockly.mainWorkspace);
  }
}

function loadPythonCode(code) {
  if (code !== null) {
    editor.setValue(code);
  }
}

async function loadProject() {
  const url_str = window.location.href;
  console.log(url_str)

  var url = new URL(url_str);
  var id = url.searchParams.get("id");
  console.log("project is id", id);

  if (id) {
    const result = await sendXml(id);
    console.log("result", result)
    if (result.status == '200') {
      if (result.editor === 'blockly') {
        loadXml(result.data);
      } else {
        loadPythonCode(result.data);
      }
    } else {
      console.log('Error when getting project\n', err);
      showModalError("Error on code loading!");
    }
  }
}

//send the code from the workspace to enter the queue to run in the robot 
async function runCode(id) {
  let monaco_code = editor.getValue();


  if (monaco_code == "") {
    console.log("no code to run");

    //show modal
    showModalError("No code detected!")
    return;
  }

  const result = await sendMonacoCode(id, monaco_code)
  const status = result.status
  if (status == 'started') {
    showModalSuccess("The program running successfully!");
  }
}

//stop the code that was being exeuted in the robot 
function stop_script() {
  stopScript();
}

async function save_xml(id) {
  let xmlText = getCode();
  const result = await saveXml(id, xmlText)
  const status = result.status
  if (status == '200') {
    showModalSuccess("Project Saved!");
  } else {
    showModalError("Error on saving!")
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