// TODO: update this to your folder id!
// folder id of RGH folder (what we are using as our root)
var fid = "1Kd-B43p61-A9JMlTf_GYqAbXOryfOtjX"

var target = "Summary and Project Info"

function run() {
  var root = DriveApp.getFolderById(fid)
  
  // the second parameter is a flag whether you want to print files
  // (you can set to false to only list folders)
  printContents(root, true) 
}

function printContents(root, includeFiles) {
  try { 
    var rootName = root.getName()
    Logger.log("Starting at folder: " + rootName)
    
    // check if we are in the directory we are looking for
    if (rootName === target) {
      Logger.log("-- Target Hit! --") 
    }
    
    // iterate over file contents in the directory
    var files = root.getFiles()
    while (includeFiles === true && files.hasNext()) {
      file = files.next()
      Logger.log(rootName + " :: " + file)
    }
    
    // iterate over each sub folder in the directory
    var subfolders = root.getFolders()
    while (subfolders.hasNext()) {
      // here we make the recursive call... like magic!
      printContents(subfolders.next(), includeFiles)
    }
  }
  catch (e) {
    Logger.log("printContents() :: " + e.toString()) 
  }
}
