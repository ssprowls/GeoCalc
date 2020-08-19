// TODO: update this to your folder id!
// folder id of RGH folder (what we are using as our root)
var fid = "1Kd-B43p61-A9JMlTf_GYqAbXOryfOtjX"

var target = "Summary and Project Info"

function run() {
  var root = DriveApp.getFolderById(fid)
  
  // make the inital call to check if the target folder exists
  var found = checkExists(root, target, 4)
  Logger.log("The target folder \"" + target + "\" " + (found ? "exists!" : "does not exist."))
}

function checkExists(root, target, maxDepth, curDepth = 0) {
  try {
    var rootName = root.getName()
    Logger.log("Looking in folder: " + rootName + ", depth = " + curDepth)
    
    // we are in the target folder
    if (rootName === target) {
      return true
    }
    
    // check whether we have hit our max depth
    // we use a post-increment so the value is updated for the recursive call already
    if (curDepth++ === maxDepth) {
      Logger.log("Max depth exceeded.")
      return false
    }
    
    // iterate over each sub folder in the directory
    var subfolders = root.getFolders()
    while (subfolders.hasNext()) {
      // here we make the recursive call... like magic!
      // only want to return on the true case because otherwise need to keep searching
      if (checkExists(subfolders.next(), target, maxDepth, curDepth) == true) {
        return true
      }
    }
  }
  catch (e) {
    Logger.log("printContents() :: " + e.toString()) 
  }
  return false
}
