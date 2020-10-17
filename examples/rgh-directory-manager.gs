// set the folder id of the root to start the project in
const rootId = "1GnJKN-t6DkyWxTbmqOigyAWNK2Upkki_";

// set the folder id of the template to copy files from
const templateId = "";

// set the users we want to specify permissions for
// const users = ["fe@rghgeo.com", "zanemckeithan@yahoo.com", "niya@rghgeo.com"]

// set the email address(es) we want to send output to
const to = ["spencer.sprowls@gmail.com"];

// note for liam: after doing some testing, there are some projects that have
//                an extra space at the end of the name, do you want to allow that?
const validProjectNameRegex = "\s*[0-9]{4}_[0-9A-Z]{5}\s*";
const validSummaryAndProjectInfoFolderNameRegex = "\s*Summary\s*(?:and|&)\s*Project\s*Info\s*";
const validReportsRecsPlansFolderNameRegex = "\s*Reports,\s*Rec's(?:,)?\s*(?:and|&)\s*Plans\s*";
const validCurvesFolderNameRegex = "\s*Curves\s*";

// set the default names to use for the folders we may have to create
const summaryAndProjectInfoFolderName = "Summary & Project Info";
const reportsRecsPlansFolderName = "Reports, Rec's, & Plans";
const curvesFolderName = "Curves";

///////////////////////////////////////////////////////////////////////////////

/*
 * Entry point for the script. Start processing at the root directory.
 */
function run() {
  const root = DriveApp.getFolderById(rootId);
  process(root);
  Logger.log("done.");
}

///////////////////////////////////////////////////////////////////////////////

/*
 * The initial process loop. Iterate over the folders in the root
 * directory and perform validation to determine any project folders.
 * Then pass it along to the next step of processing.
 */
function process(root) {
  let folders = root.getFolders();
  while (folders.hasNext()) {
    let folder = folders.next();
    // we only care about project folders - validate using regex
    if (!folder.getName().match(validProjectNameRegex)) continue;
    processProjectFolder(folder);
  }
}

///////////////////////////////////////////////////////////////////////////////

/*
 * Check a project folder for the expectced sub folders, and if they do not
 * exist then create them and fill with default templates when necessary.
 *
 * Note: I am not entirely convinced this is the cleanest way to do this, but
 *       for now I think this will be more efficient than before. We don't
 *       want to abstract this too much because at a certain point we lose
 *       readability.
 */
function processProjectFolder(projectFolder) {
  // set the flags for the target folders we are looking for
  //  s: summary     r: reports     c: curves
  let sFlag = false, rFlag = false, cFlag = false;
  // iterate over the sub folders
  let subFolders = projectFolder.getFolders();
  while (subFolders.hasNext()) {
    let subFolder = subFolders.next();
    let subFolderName = subFolder.getName();
    // all the sub folders (we care about) have been found
    if (sFlag === true && rFlag === true && cFlag === true) {
      break;
    }
    // by having the check first to see if the found flag is false we can
    // end early and save time in the case of an already found sub folder,
    // otherwise check the regex pattern
    else if (sFlag === false && subFolderName.match(validSFolderNameRegex)) {
      sFlag = true;
    }
    else if (rFlag === false && subFolderName.match(validRFolderNameRegex)) {
      rFlag = true;
    }
    else if (cFlag === false && subFolderName.match(validCFolderNameRegex)) {
      cFlag = true;
    }
  }
  // now that we have seen all the sub folders, determine what we need to do
  if (sFlag === false) {
    // create the new folder under the project folder we are in
    let sFolder = createFolder(summaryAndProjectInfoFolderName, projectFolder);
    // copy the contents of the template folder to the folder we just created
    copyFolder(DriveApp.getFolderById(templateId),
               sFolder,
               projectFolder.getName());
    // iterate over the files we copied over
    let sFiles = sFolder.getFiles()
    while (sFiles.hasNext()) {
      // set permissions
      addWriterPermissions(sFiles.next().getId());  
    }
  }
  if (rFlag === false) {
    createFolder(reportsRecsPlansFolderName, projectFolder);
  }
  if (cFlag === false) {
    createFolder(curvesFolderName, projectFolder);
  } 
}

///////////////////////////////////////////////////////////////////////////////

/*
 * This will create a folder with the given name under the given target.
 */
function createFolder(name, target) {
  let created = target.createFolder(name);
  Logger.log("Added folder \"" + name + "\" to " + target.getName() + ".");
  return created;
}

///////////////////////////////////////////////////////////////////////////////

/*
 * This will copy the source folder and its file contents to the target
 * folder.
 */
function copyFolder(source, target, append="") {
  let folders = source.getFolders();
  let files = source.getFiles();
  // copy the files in the folder
  while (files.hasNext()) {
    let file = files.next();
    if (append === "") {
      file.makeCopy(file.getName(), target);
    }
    else {
      file.makeCopy(file.getName() + " " + append, target);
    }
  }
  // copy the folders and recursively travel down
  while (folders.hasNext()) {
    let subFolder = folders.next();
    let targetFolder = target.createFolder(subFolder.getName());
    // make the recursive call
    copyFolder(subFolder, targetFolder);
  }
}

///////////////////////////////////////////////////////////////////////////////

/*
 * Send an email containing the log output to the provided email address(es).
 */
function sendEmail() {
  let subject = "Files Added Today - " + new Date(Date.now())
      .toLocaleString().split(',')[0];
  let body = Logger.getLog();
  for (let i = 0; i < to.length; i++) {
    MailApp.sendEmail(to[i], subject, body);
    Logger.log("Sent email to \"" + to[i] + "\".");
  }
  Logger.log("All emails sent.");
}

///////////////////////////////////////////////////////////////////////////////

/*
 * Give writer permissions for the provided users list.
 */
function addWriterPermissions(fileId) {
  for (let i = 0; i < users.length; i++) {
    Drive.Permissions.insert(
      {
        'role': 'writer',
        'type': 'user',
        'value': users[i]
      },
      fileId,
      {
        'sendNotificationEmails': 'false'
      }
    );
  }
}

///////////////////////////////////////////////////////////////////////////////

/*
 * Utility to test the 'copyFolder' function. This should create the target
 * folder at the top level of the Google Drive.
 */
function testCopyFolder() {
  // TODO: enter a folder id to perform the copy on
  let source = DriveApp.getFolderById("ENTER THE ID HERE");
  let target = DriveApp.createFolder("testCopyFolder");
  copyFolder(source, target);
}

///////////////////////////////////////////////////////////////////////////////
