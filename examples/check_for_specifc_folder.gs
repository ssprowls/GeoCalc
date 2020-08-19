// TODO: update this to your folder id!
// folder id of RGH folder (what we are using as our root)
var fid = "1Kd-B43p61-A9JMlTf_GYqAbXOryfOtjX"

var target = "Summary and Project Info"

function run() {
  var root = DriveApp.getFolderById(fid)
  
  // make the inital call to check if the target folder exists
  var found = checkExists(root, target)
  Logger.log("The target folder \"" + target + "\" " + (found ? "exists!" : "does not exist."))
}

function checkExists(root, target) {
  try {
    var rootName = root.getName()
    Logger.log("Starting at folder: " + rootName)
    
    if (rootName === target) {
      return true
    }
    
    // ... implicit 'else' b/c of return statement ...
    
    // iterate over each sub folder in the directory
    var subfolders = root.getFolders()
    while (subfolders.hasNext()) {
      // here we make the recursive call... like magic!
      if (checkExists(subfolders.next(), target) == true) {
        return true
      }
    }
  }
  catch (e) {
    Logger.log("printContents() :: " + e.toString()) 
  }
  return false
}
