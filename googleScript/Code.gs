/* ************************************************************************
 Función que recibe los datos mediante POST y crea los archivos Sheet con los mismos.
 ************************************************************************** */
function doPost(e) {
  // Leyendo configuración
  var strDebug = "<br>Modo debug activado: ";
  //[1.0, 0.0, jquintero@iac.es,nehk018@gmail.com, dataGris, Sat Dec 30 13:00:00 GMT-01:01 1899, {"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}]

  var vals = loadFileConfig(strDebug);
  var initParams = vals[0];
  var debug = initParams[0];
  var enviarEmail = initParams[1];
  var emailList= initParams[2];
  var timeReport= initParams[4];
  var dataGrisDirectory = initParams[5];
  
  strDebug = vals[1];
  //e = 1
  if (e != null) {
    //sheetLocal = SpreadsheetApp.create("loggerC");
    //row1 = [e.postData.contents];
    //sheetLocal.appendRow(row1);

    var json = JSON.parse(e.postData.contents);
    //json = JSON.parse('{"ts": 1649259302000, "name": "Pres2", "values": {"Pres2_value": 355.0, "Pres2_category": "Pres2", "Pres2_minstatus": 0, "Pres2_maxstatus": 0, "Pres2_min": 355.0, "Pres2_max": 355.0, "Pres2_mean": 355.0, "Pres2_median": 355.0, "Pres2_samples": 60, "Pres2_tstamp": "2022-04-06 16:35:02"}}');

    var name = json.name;
    folder = getOrCreateSubFolder(dataGrisDirectory);
    var now = new Date();
    var fileName = Utilities.formatDate(now, 'Etc/GMT', 'yyyyMMdd') + "_" + name;
    var sheet = getFileData(folder, fileName, strDebug, false);   
    var time = json.values[name + "_tstamp"];
    //Logger.log(time);
    //time = Utilities.formatDate(time, "Etc/GMT", "HH:mm:ss");
    var minStatus = json.values[name + "_minstatus"];
    var maxStatus = json.values[name + "_maxstatus"];
    var min = json.values[name + "_min"];
    var max = json.values[name + "_max"];
    var mean = json.values[name + "_mean"];
    var median = json.values[name + "_median"];
    var samples = json.values[name + "_samples"];
    var current = json.values[name + "_value"];
    row = [time, minStatus, maxStatus, min, max, mean, median, samples, current];
    //sheetLocal.appendRow(row);

    sheet.appendRow(row);

    if (debug == 1) {
      Logger.log(strDebug);
    }
    return ContentService.createTextOutput("Ok");
  } else {
     console.warn("No se han recibido datos");
     return ContentService.createTextOutput("Error. No se han recibido datos.");
  }
}

/* ************************************************************************
 Función que envía un email diario con los datos actuales.
 ************************************************************************** */
function checkLimits() {
 var strDebug = "<br>Modo debug activado: ";
  //[1.0, 0.0, jquintero@iac.es,nehk018@gmail.com, dataGris, Sat Dec 30 13:00:00 GMT-01:01 1899, {"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}]

  var vals = loadFileConfig(strDebug);
  var initParams = vals[0];
  var debug = initParams[0];
  var isEnviarEmail = initParams[1];
  var emailList= initParams[2];
  var timeReport= initParams[4];
  var dataGrisDirectory = initParams[3];

  
  folder = getOrCreateSubFolder(dataGrisDirectory);
  var ficherosAProcesar = JSON.parse(initParams[5]);
  //console.log(ficherosAProcesar);

  strBody = "ALERT:\n"
  //console.log(dataGrisDirectory);
  var now = new Date();
  //console.log(now);
  var fileName = Utilities.formatDate(now, 'Etc/GMT', 'yyyyMMdd');
  //console.log(fileName);
  keys = Object.keys(ficherosAProcesar);
  var enviarAviso = 0;
  for (i in keys) {  
    strBody += "  " + keys[i] + " \n";

    graphName = keys[i];
    numColumnas = 0;
    //Logger.log(keys[i]);
    graphData = ficherosAProcesar[keys[i]];
    keysGraphs = Object.keys(graphData);
    //Logger.log(keysGraphs);

    
    limits = {};
    listaLimites = [];

    for (k in keysGraphs) {    
      
      fileData = graphData[keysGraphs[k]];  
      nameData = fileData.name;
      columnas = fileData.columns;
      graphName = fileName + "_" + keysGraphs[k];

      limits =  fileData.limit;
      fichero = getFileData(folder, graphName, strDebug, true);
      lastRow = fichero.getLastRow();
      strBody += "      * " + keysGraphs[k] + ": ";
      var valor = [];
      for(j=0; j < 3; j++) {
        strColumna = columnas[columnas.length-1] + lastRow;
        //Logger.log(strColumna);
        valor.push(Number(fichero.getRange(strColumna).getValues()));
        //console.log(bouncer(data));
        if (j == 0) {
          strBody += valor + " ";
        }
        lastRow --;
      }

      //var data = fichero.getRange("A100", "I100"]).getValues();
      //console.log(valor);
      //console.log(limits);
      //console.log("-----------------");
      for (l in limits) {
        //if ()
        val_limit = limits[l];
        
        if (val_limit < valor[0] && 
            val_limit < valor[1] &&
            val_limit < valor[2]) {
          //console.log("Enviar aviso");
          enviarAviso = 1;
        }
      }
      strBody += "    (Limits: " + limits + ")";
      strBody += "\n";
    }

    strBody += "  ---------- \n";
  }

  //console.log(strBody);
  
  if (checkEnviarAviso(enviarAviso)) {
    enviamosEmail(initParams, "GRIS WARNING", strBody);
  } else {
    console.log("No se envía aviso");
  }
}
function checkEnviarAviso(enviarAviso) {

  var fileName = "avisos";
  var files = DriveApp.getFiles();
  var encontrado = false;
  var initParams = null;

  while (files.hasNext() && !encontrado){
    file = files.next();
    if (file.getName() == fileName) {
      encontrado = true;
    }
  }
  var sheet;
  if (encontrado) {
    sheet = SpreadsheetApp.open(file);
    var rango = sheet.getSheets()[0].getRange(1,1,1,1);
    initParams = rango.getValues()[0];
    //Logger.log(initParams);
  } else {
    sheet = SpreadsheetApp.create(fileName);
    initParams = [0];
    sheet.appendRow(initParams);
  }  
  avisoEnviado = initParams[0];

  if (enviarAviso == 1 && avisoEnviado == 0) {
    sheet.getActiveSheet().getRange(1,1).setValue(1);
    console.log("Enviamos aviso");
    return true;
  }
  if (enviarAviso == 0 && avisoEnviado == 1) {  // Se restaura la normalidad.
    sheet.getActiveSheet().getRange(1, 1).setValue(0);
    console.log("Restauramos la normalidad");
  }
  return false;
}

/* ************************************************************************
 Función que envía un email diario con los datos actuales.
 ************************************************************************** */
function dailyEmail() {
 var strDebug = "<br>Modo debug activado: ";
  //[1.0, 0.0, jquintero@iac.es,nehk018@gmail.com, dataGris, Sat Dec 30 13:00:00 GMT-01:01 1899, {"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}]

  var vals = loadFileConfig(strDebug);
  var initParams = vals[0];
  var debug = initParams[0];
  var isEnviarEmail = initParams[1];
  var emailList= initParams[2];
  var timeReport= initParams[4];
  var dataGrisDirectory = initParams[3];

  
  folder = getOrCreateSubFolder(dataGrisDirectory);
  var ficherosAProcesar = JSON.parse(initParams[5]);
  //console.log(ficherosAProcesar);

  strBody = "Daily Gris Instrument report:\n"
  //console.log(dataGrisDirectory);
  var now = new Date();
  //console.log(now);
  var fileName = Utilities.formatDate(now, 'Etc/GMT', 'yyyyMMdd');
  //console.log(fileName);
  keys = Object.keys(ficherosAProcesar);
  
  for (i in keys) {  
    strBody += "  " + keys[i] + " \n";

    graphName = keys[i];
    numColumnas = 0;
    //Logger.log(keys[i]);
    graphData = ficherosAProcesar[keys[i]];
    keysGraphs = Object.keys(graphData);
    //Logger.log(keysGraphs);

    
    limits = {};
    listaLimites = [];

    for (k in keysGraphs) {    
      
      fileData = graphData[keysGraphs[k]];  
      nameData = fileData.name;
      columnas = fileData.columns;
      graphName = fileName + "_" + keysGraphs[k];

      limits =  fileData.limit;
      fichero = getFileData(folder, graphName, strDebug, true);
      lastRow = fichero.getLastRow();
      strBody += "      * " + keysGraphs[k] + ":";

      for(j=0; j < columnas.length; j++) {
        strColumna = columnas[j] + lastRow;
        //Logger.log(strColumna);
        var data = fichero.getRange(strColumna).getValues();
        //console.log(bouncer(data));
        strBody += data + " ";
      }

      //var data = fichero.getRange("A100", "I100"]).getValues();
      //console.log(limits);
      
      strBody += "    (Limits: " + limits + ")";
      strBody += "\n";
    }

    strBody += "  ---------- \n";
  }

  enviamosEmail(initParams, "DAILY REPORT", strBody);
}

/* ************************************************************************
 Función que envía un email
 ************************************************************************** */
function enviamosEmail(initParams, subject, mensaje) {
  var isEnviarEmail = initParams[1];
  var emailList= initParams[2];
  if (isEnviarEmail == 1) {
    MailApp.sendEmail(emailList, subject, mensaje);
  } else {
    console.log("Enviar email desactivado");
    console.log(mensaje);
  }
}

/* ************************************************************************
 Función que sirve muestra el HTML con las gráficas.
 ************************************************************************** */
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('graficas').setTitle('Gris graphics');;
}

/* ************************************************************************
 Función que devuelve un map con los datos de la fecha especificada por parámetro.
 ************************************************************************** */
function getGraphs(date, numDays) {
  //date = '20230306';
  numDays = 1;
  var strDebug = "<br>Get Graph's List:";
  //[1.0, 0.0, jquintero@iac.es,nehk018@gmail.com, dataGris, Sat Dec 30 13:00:00 GMT-01:01 1899, {"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}]
  var vals = loadFileConfig(strDebug);

  /*var debug = initParams[0];
  var enviarEmail = initParams[1];
  var emailList= initParams[2];
  var timeReport= initParams[4];
  var dataGrisDirectory = initParams[5];*/
  

  var initParams = vals[0];
  var debug = initParams[0];
  var dataGrisDirectory = initParams[3];
  
  /*sheetLocal = SpreadsheetApp.create("loggerC");
  row1 = [date, numDays];
  sheetLocal.appendRow(row1);*/

  var ficherosAProcesar = JSON.parse(initParams[5]);
  strDebug = vals[1];
  
  folder = getOrCreateSubFolder(dataGrisDirectory);
  
  resultado = [];
  keys = Object.keys(ficherosAProcesar);
  var year = +date.substring(0, 4)
  var month = +date.substring(4, 6)
  var day = +date.substring(6, 8)
  var files = [];
  var pubdate = new Date(year, month - 1, day)

  //Logger.log(ficherosAProcesar);
  for (i in keys) {  
    graphName = keys[i];
    numColumnas = 0;
    //Logger.log(keys[i]);
    graphData = ficherosAProcesar[keys[i]];
    keysGraphs = Object.keys(graphData);
    //Logger.log(keysGraphs);

    
    limits = {};
    listaLimites = [];

    for (k in keysGraphs) {    
      fileData = graphData[keysGraphs[k]];  
      nameData = fileData.name;
      columnas = fileData.columns;

      limits =  fileData.limit;

      counter = 0;  
      
      for (l in limits) {
        var limite = {};
        nameLimit = "Limit " + counter + " (" +  keysGraphs[k] + ")";
        //Logger.log(nameLimit);
        //Logger.log(limits[l]);
        limite["name"]= nameLimit;
        limite["value"] = limits[l];
        limite["origen"] = keysGraphs[k];
        //Logger.log(limite);
        listaLimites.push(limite);
        counter ++;
      }
      //Logger.log(listaLimites);

      for(m=0; m<numDays; m++) {
        dateAux = subDaysFromDate(pubdate,m);
        date = Utilities.formatDate(dateAux, 'Etc/GMT', 'yyyyMMdd');
        nameFile = date + "_" + keysGraphs[k];
        files.push(nameFile)
       
        fichero = getFileData(folder, nameFile, strDebug, true);
        
        fileData["datos"] = [];
        numColumnas +=columnas.length -1; // Le quitamos la columna índice. 
        
        for(j=0; j < columnas.length; j++) {
          strColumna = columnas[j] + "2:" +columnas[j];
          //Logger.log(strColumna);
          var data = fichero.getRange(strColumna).getValues();
          fileData["datos"].push(bouncer(data));
          //fileData["datos"].push(data);
        }
       
      }
    }
    // YA tenemos los datos por separado, así que vamos a agruparlos.
    var agrupados={};
    contador = 0;
    for (k in keysGraphs) {
      //Logger.log(keysGraphs[k]);
      datas = graphData[keysGraphs[k]].datos;
      //Logger.log(datas);
      //Logger.log(datas);
      // Siempre Procesamos la columna 0 como índice.
      for (j=0; j < datas[0].length; ++j){
        fecha = new Date(datas[0][j]);
        //Logger.log(fecha);
        //Logger.log(datas[0][j]);
        //yyyyMMdd
        //clave = Utilities.formatDate(fecha, 'Etc/GMT', 'yyyyMMddHHmmss');
        clave = fecha
        //Logger.log(clave);
        //Logger.log("-------------------------");
        //row1 = ["1"];
        //sheetLocal.appendRow(row1);
        if (!agrupados.hasOwnProperty(clave)) {
          //Logger.log("Creadno clave");
          agrupados[clave] = {};
          //row1 = [clave];
          //sheetLocal.appendRow(row1);

          agrupados[clave]["date"] = datas[0][j];
          agrupados[clave]["datos"] = [];
          agrupados[clave]["datos"].push(datas[0][j]);
          //agrupados[clave]["datos"].push(convertiFechaHora(datas[0][j]));
          //agrupados[clave]["datos"].push(convertiFechaHora(datas[0][j]));
          for(l=0; l<numColumnas;l++) {
            agrupados[clave]["datos"].push(null);
          }
        }
        pos = (contador * (numColumnas-1))+1;
        //row1 = ["2"];
        //sheetLocal.appendRow(row1);
        for(l=1; l < datas.length; l++) {
          //row1 = [datas[l][j]];
          //sheetLocal.appendRow(row1);
          agrupados[clave]["datos"][pos + l-1] = datas[l][j];
          pos ++;
        }
        
        //row1 = ["3"];
        //sheetLocal.appendRow(row1);
      }
      contador ++;
    }
    datosAgrupados = [];
    resumen = {};
    
    //Logger.log(Object.keys(agrupados).length);
    var clavesFechas = Object.keys(agrupados);
    //Logger.log(keys2);
    //for (clave in clavesFechas) {
    for(l=0; l< clavesFechas.length; l++) {
      clave = clavesFechas[l];
      datosAgrupados.push(agrupados[clave].datos);

    }
    resumen["nombre"] = graphName
    resumen["file"] = files;
    resumen["data"] = datosAgrupados;
    resumen["limites"] = listaLimites;
    //Logger.log("Mostrando datos");
    //Logger.log(listaLimites);
    resumen["campos"] = keysGraphs;
    //Logger.log(resumen);
    resultado.push(resumen);
  }

  //Logger.log(resultado);
  return JSON.stringify(resultado);
}

function bouncer(arr) {
  return arr.filter(function(v) { return !!v[[0]]; });
}

function subDaysFromDate(date,d){
  // d = number of day ro substract and date = start date
  var result = new Date(date.getTime()-d*(24*3600*1000));
  return result
}

function convertiFechaHora(aux) {
  fecha = new Date(aux);
  //const timeZone = AdsApp.currentAccount().getTimeZone();
  const noonString = Utilities.formatDate(fecha, "Etc/GMT", 'MMMM dd, yyyy HH:mm:ss');
  aux2 = "'" + noonString + "'";
  return aux;

}

function convertiFecha(aux) {
  
  aux = aux.toString().split(" ");
  aux2 = aux[4].split(":");
  aux3 = [];
  for(k=0; k < aux2.length; k++) {
    aux3.push(Number(aux2[k]));
  }
  aux2 = JSON.stringify(aux3);

  aux2 = '{"v":' + aux2 + '}';
  return JSON.parse(aux2);

}

function getData(graph, files, date) {
  files = '["Temp1","Temp2"]';
  date = '20220407';
  graph = "Temperature";

  var strDebug = "<br>Get Graph's Data:";
  //sheetLocal = SpreadsheetApp.create("logger");

  var ficherosAProcesar = JSON.parse(files);
//[1.0, 0.0, jquintero@iac.es,nehk018@gmail.com, dataGris, Sat Dec 30 13:00:00 GMT-01:01 1899, {"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}]

  var vals = loadFileConfig(strDebug);
  var initParams = vals[0];
  var debug = initParams[0];
  var dataGrisDirectory = initParams[3];
  var listGraph = initParams[7];
  var columns = JSON.parse(initParams[5]);
  strDebug = vals[1];
  
  result = {"origen":files};
  result["name"] = graph;

  folder = getOrCreateSubFolder(dataGrisDirectory);
  var myarray = [];
  counter = 0;
  var mapByDate = {};

  //row = ["1", convert];
  //sheetLocal.appendRow(row);

  //Logger.log(ficherosAProcesar);
  //Logger.log(columns);
  for (i=0; i < columns.length; i++) {
    name = date + "_" + ficherosAProcesar[i];
    
    fichero = getFileData(folder, name, strDebug, true);
    
    columnas = columns[ficherosAProcesar[i]];
    //row = [JSON.stringify(columnas), JSON.stringify(columns), JSON.stringify(convert), ];
    //sheetLocal.appendRow(row);
    //row = ["2", columnas];
    //sheetLocal.appendRow(row);
    myarray = [];
   //Logger.log(columnas);
    /*if (fichero != null) {
      for(j=0; j < columnas.length; j++) {
          strColumna = columnas[j] + "2:" +columnas[j];
          var data = fichero.getRange(strColumna).getValues();
          var myFilterArray = bouncer(data);
          if (j = 0) {

          }
          //Logger.log(strColumna);
          //Logger.log(myFilterArray);
          myarray.push(myFilterArray);
      }
      // La primera Columna siempre será fecha.
      Logger.log(myarray);
      for (k=0; k < myarray[0].length; k++) { // Recorremos todas las filas.
          // La primera columna siempre será el tiempo y nos servirá para el mapa.
          var fecha = myarray[0][k];
          fechaArray = convertiFecha(fecha);
          Logger.log(fecha);
          
      }
    }*/
  }

 //Logger.log(mapByDate);
  

  //row = [JSON.stringify(myarray)];
  //sheetLocal.appendRow(row);

  auxResult = [];
  /*for (i=0; i < myarray[0].length; i++) {
    tempArray = [];
    for (j = 0; j < myarray.length; j++) {
      //Logger.log(i + "-" + j);
      //Logger.log(myarray[j][i]);
      if (myarray[j][i] != "" && myarray[j][i] != null) {
        if (j == 0) {
          //Logger.log("Fecha: " + myarray[j][i]);
          aux = myarray[j][i];
          aux = aux.toString().split(" ");
          aux2 = aux[4].split(":");
          aux3 = [];
          for(k=0; k < aux2.length; k++) {
            aux3.push(Number(aux2[k]));
          }
          aux2 = JSON.stringify(aux3);
         
          aux2 = '{"v":' + aux2 + '}';
          tempArray.push(JSON.parse(aux2));
        } else {  
          tempArray.push(myarray[j][i][0]);
        }
      }
    }
    auxResult.push(tempArray);
  }*/
  
  //console.log(auxResult);
  //console.log(JSON.stringify(auxResult));
  //console.log(JSON.stringify(result));

  result["values"] = auxResult;

  //Logger.log(JSON.stringify(auxResult));

  //row = [JSON.stringify(auxResult), JSON.stringify(result), auxResult];
  //sheetLocal.appendRow(row);

  return JSON.stringify(result);
}

function descOrder(element1, element2) {
  if(element1 > element2)
    return -1; //Sort element1 before element2
  if(element1 < element2)
    return 1;  //Sort element1 after element2
  return 0;    //Don't change the positions of element1 and element2
}

function ascOrder(element1, element2) {
  if(element1 > element2)
    return 1; //Sort element1 before element2
  if(element1 < element2)
    return -1;  //Sort element1 after element2
  return 0;    //Don't change the positions of element1 and element2
}

function getFilesNames() {
  var strDebug = "<br>GetFilesnames";
  //[1.0, 0.0, jquintero@iac.es,nehk018@gmail.com, dataGris, Sat Dec 30 13:00:00 GMT-01:01 1899, {"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}]
  var vals = loadFileConfig(strDebug);
  var initParams = vals[0];
  var debug = initParams[0];
  var dataGrisDirectory = initParams[3];
  strDebug = vals[1];

  folder = getOrCreateSubFolder(dataGrisDirectory);

  var files = folder.getFiles();
  var aux = {};
  while (files.hasNext()){
    file = files.next();
    name = file.getName().split("_")[0];
    aux[name] = 1;
  }
  var result = [];
  for (var key in aux) {
    result.push(key);
  } 
  //Logger.log(strDebug);
  //Logger.log(result);
  return result.sort(descOrder);
}

function loadFileConfig(strDebug) {
  var fileName = "configGris3";
  var files = DriveApp.getFiles();
  var encontrado = false;
  var initParams = null;

  while (files.hasNext() && !encontrado){
    file = files.next();
    if (file.getName() == fileName) {
      encontrado = true;
    }
  }
  
  if (encontrado) {
    strDebug += "<br>Abriendo fichero: " + fileName;
    sheet = SpreadsheetApp.open(file);
    var rango = sheet.getSheets()[0].getRange(2,1,1,6);
    initParams = rango.getValues()[0];
    //Logger.log(initParams);
  } else {
    sheet = SpreadsheetApp.create(fileName);
    initParams = ["Debug", "Send emails", "List of emails", "Excel directory", "Time Email", 'Graph configuration'];
    sheet.appendRow(initParams);
    initParams = [1, 0, "jquintero@iac.es,nehk018@gmail.com", "dataGris", "13:00", '{"Pressure":{"Pres2":{"name":"Presion2","columns":["A","I"]}},"Temperature":{"Temp1":{"name":"Temperature1","columns":["A","I"]},"Temp2":{"name":"Temperature2","columns":["A","I"]}}}'];
    strDebug += "<br>Creando fichero: " + fileName;
    
    sheet.appendRow(initParams);
  }  
  // Establecemos las variables globales.
  strDebug += "<br>Configuración: " + initParams;

  return [initParams, strDebug];
}

function getFileData(folder, fileName, strDebug, soloabrir) {
  var files = folder.getFiles();
  var encontrado = false;
  while (files.hasNext() && !encontrado){
    file = files.next();
    if (file.getName() == fileName) {
      encontrado = true;
    }
  }
  var sheet = null;
  if (encontrado) {
    //Logger.log(folder);
    strDebug += "<br>Abriendo fichero: " + folder.getName() + " " + fileName;
    sheet = SpreadsheetApp.open(file);
  } else if (!soloabrir) {

    strDebug += "<br>Creando fichero: " + fileName;
    sheet = SpreadsheetApp.create(fileName);
    var row =  ["tstamp","min",	"max",	"min",	"max",	"mean", 	"median", "samples", "current"];
    sheet.appendRow(row);
    var file = DriveApp.getFileById(sheet.getId());
    var docfile = file.moveTo(folder);
  }
  return sheet;
}

function getOrCreateSubFolder(childFolderName) {
  folders = DriveApp.getFolders();
  var encontrado = false;
  var folder = null;
  while (folders.hasNext() && ! encontrado) {
    folder = folders.next();
    if (folder.getName() == childFolderName) {
      encontrado = true;      
    }
  }
  if (! encontrado) {
    folder = DriveApp.createFolder(childFolderName);
  }
  return folder;
}