async function saveXmlToDB(id) {
  let xmlText = getBlocklyXmlText();

  try {
    const result = await saveXml(id, xmlText);
    if (result.status === '200') {
      showModalSuccess("Project Saved!");
    } else {
      throw new Error('Save Error');
    }
  } catch (error) {
    showModalError("Error on saving!");
  }
}

function loadXmlIntoBlockly(xml) {
  const dom = Blockly.Xml.textToDom(xml);
  Blockly.mainWorkspace.clear();
  Blockly.Xml.domToWorkspace(dom, Blockly.mainWorkspace);
}

async function loadProjectFromDB() {
  const id = new URL(window.location.href).searchParams.get("id");
  console.log("project id", id);

  if (id) {
    try {
      const result = await sendXml(id);
      if (result.status === '200') {
        loadXmlIntoBlockly(result.data);
      } else {
        throw new Error('Load Error');
      }
    } catch (error) {
      console.error('Error when getting project', error);
      showModalError("Error on blocks loading!");
    }
  }
}

async function runBlocklyCode(id) {
  let blocklyCode = Blockly.Python.workspaceToCode(Blockly.mainWorkspace);
  if (!blocklyCode) {
    console.log("no code to run");
    showModalError("No Blocks detected!");
    return;
  }

  try {
    const result = await sendCode(id, blocklyCode);
    
    console.log("sendCode result", result);
    //if (result === '200') {
         
      // showModalSuccess("The program started!");
      //if (id!=-1) {
        //await saveXmlToDB(id); // Save after running the code
      //}
    //} else {
      //showModalError("Error in running the code!");
    //}
    return;

  } catch (error) {
    showModalError("Error in running the code!");
    return;
  }

}

// function stopScript() {
//   // Implementation for stopping the script
// }

function openMapForStage() {
  let stage = document.getElementById("stage_select").value;
  openMap(stage);
}

// function resetStage() {
//   // Implementation for resetting the stage
// }

function getBlocklyXmlText() {
  let xmlDom = Blockly.Xml.workspaceToDom(Blockly.mainWorkspace);
  return Blockly.Xml.domToPrettyText(xmlDom);
}
