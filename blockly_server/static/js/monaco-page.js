var editor;
			
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
    var terminal = document.getElementById('terminal_scrollable-content');

    var codeLines = code.split('\n');  // Split the code string into an array of lines
    for (var i = 0; i < codeLines.length; i++) {
        // Print each line separately
        terminal.innerHTML += '<p>' + codeLines[i] + '</p>';
    }
    console.log(code);
}

//send the code from thw workspace to be run in the robot 
async function runCode(id) {
    let monaco_code = editor.getValue();
    
    
    if (monaco_code == "") {
      console.log("no code to run");
  
      //show modal
      showModalError("No code detected!")
      return;
    }

    alert(monaco_code);
  
    const result = await sendMonacoCode(id, monaco_code)
    const status = result.status
    if (status == 'started') {
      showModalSuccess("The program running successfully!");
    }
    // let xmlDom = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
    // let xmlText = Blockly.Xml.domToPrettyText(xmlDom);
  
    // const result_save = await saveXml(id, xmlText);
  
    // if (result_save.status == 200) {
    //   console.log("The program running successfully!");
    // }
  }
  
  //stop the code that was being exeuted in the robot 
  function stop_script() {
    stopScript();
  }