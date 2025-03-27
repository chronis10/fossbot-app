// MOVE FORWARD 
Blockly.Blocks['move_forward'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Mover para frente");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // MOVE FORWARD DEFAULT 
  Blockly.Blocks['move_forward_default'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Mover um passo para frente");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // MOVE FORWARD DISTANCE
  Blockly.Blocks['move_forward_distance'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Mover para frente por")
        .appendField(new Blockly.FieldNumber(0, 0, 1000), "number_of_steps")
        .appendField("cm");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // MOVE REVERSE 
  Blockly.Blocks['move_reverse'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Mover para trás");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // MOVE REVERSE DEFAULT
  Blockly.Blocks['move_reverse_default'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Mover um passo para trás");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // MOVE REVERSE DISTANCE
  Blockly.Blocks['move_reverse_distance'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Mover para trás por")
        .appendField(new Blockly.FieldNumber(0, 0, 1000), "number_of_steps")
        .appendField("cm");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // STOP
  Blockly.Blocks['stop'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Parar");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // WAIT 
  Blockly.Blocks['wait'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Esperar")
        .appendField(new Blockly.FieldNumber(0, null, null), "wait_s")
        .appendField("seg");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // TURN RIGHT / CLOCKWISE 
  Blockly.Blocks['turn_right'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Virar à direita");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  Blockly.Blocks['turn_right_90'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Virar 90 graus à direita");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // TURN LEFT / COUNTERCLOCKWISE 
  Blockly.Blocks['turn_left'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Virar à esquerda");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // TURN LEFT STEP / COUNTERCLOCKWISE STEP
  Blockly.Blocks['turn_left_90'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Virar 90 graus à esquerda");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // BEEP
  Blockly.Blocks['beep'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Bip");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // SET COLOR 
  Blockly.Blocks['set_color'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Escolher")
        .appendField(new Blockly.FieldDropdown([["vermelho", "'red'"], ["verde", "'green'"], ["azul", "'blue'"], ["branco", "'white'"], ["violeta", "'violet'"], ["ciano", "'cyan'"], ["amarelo", "'yellow'"], ["fechado", "'closed'"]]), "color_option")
        .appendField("cor");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // PLAY SOUND
  Blockly.Blocks['play_sound'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Tocar o som")
        .appendField(new Blockly.FieldDropdown(this.generateOptions), "option");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // DISTANCE
  Blockly.Blocks['distance'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Distância de");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // LIGHT SENSOR 
  Blockly.Blocks['light_sensor'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Sensor de luz");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // NOISE DETECTION 
  Blockly.Blocks['noise_detection'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Ruído");
      this.setOutput(true, 'Boolean');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // CHECK FOR OBSTACLE 
  Blockly.Blocks['check_for_obstacle'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Existência de obstáculo");
      this.setOutput(true, 'Boolean');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // CHECK FOR BORDER LINE 
  Blockly.Blocks['check_for_line'] = {
    init: function () {
      this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["esquerda", "3"], ["meio", "1"], ["direita", "2"]]), "check_for_line_option")
        .appendField("Existência de linha preta");
      this.setOutput(true, 'Boolean');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // GET FLOOR SENSOR 
  Blockly.Blocks['floor_sensor'] = {
    init: function () {
      this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["esquerda", "3"], ["meio", "1"], ["direita", "2"]]), "floor_sensor_option")
        .appendField("Sensor de chão");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // CHECK FOR DARK
  Blockly.Blocks['check_for_dark'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Está escuro?");
      this.setOutput(true, 'Boolean');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // GET LAST MOVE DISTANCE
  Blockly.Blocks['get_last_move_distance'] = {
    init: function () {
      this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["esquerda", "left "], ["direita", "right"]]), "option")
        .appendField("Distância do último movimento");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // GET ACCELERATION
  Blockly.Blocks['get_acceleration'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Aceleração no eixo")
        .appendField(new Blockly.FieldDropdown([["x", "x"], ["y", "y"], ["z", "z"]]), "option");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // GET GYROSCOPE
  Blockly.Blocks['get_gyroscope'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Valor do giroscópio no eixo")
        .appendField(new Blockly.FieldDropdown([["x", "x"], ["y", "y"], ["z", "z"]]), "option");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // TEMPERATURE
  Blockly.Blocks['temperature'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Temperatura");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // HUMIDITY
  Blockly.Blocks['humidity'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Umidade");
      this.setOutput(true, 'Number');
      this.setColour(45);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // BEGIN TIMER
  Blockly.Blocks['begin_timer'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Iniciar temporizador");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // STOP TIMER
  Blockly.Blocks['stop_timer'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Parar temporizador");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // GET TIMER
  Blockly.Blocks['get_timer'] = {
    init: function () {
      this.appendDummyInput()
        .appendField("Tempo que passou");
      this.setOutput(true, 'Number');
      this.setColour(290);
      this.setTooltip("");
      this.setHelpUrl("");
    }
  };
  
  // PRINT TERMINAL
  Blockly.Blocks['transmit'] = {
    init: function() {
      this.appendValueInput("for_print")
          .setCheck(null)
          .appendField("Imprimir");
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setColour(120);
      this.setTooltip(" ");
      this.setHelpUrl(" ");
    }
  };
