# The intake

How messages from africareframed.com reach us.

1. A form on the site (Request access, or the partner message form on the Partner portal) sends its fields as one
   JSON text to a Google Apps Script web app.
2. The script (`Code.gs`, this folder is its master copy) writes one row to the spreadsheet "Partner database"
   (Drive, 06 Partners), saves an attached file to the folder "Partner database – files received", sends us an
   email and sends the sender a confirmation with the row's reference (R-0001 for a request, M-0001 for a message).
3. If the script cannot be reached, the form says so and offers the same text as an email.

The script runs in the Google account td@africareframed.com as "Execute as: Me", "Who has access: Anyone". It must
stay in that account's own Drive: a web app stops working if it is moved to a shared drive. The spreadsheet and the
folder are on the shared drive. Their two addresses stand in the first line of the copy in the script project
(`const IDS = { SHEET_ID: '…', FOLDER_ID: '…' };`) and not in this public repository.

To change the script: edit `Code.gs` here, paste it into the script project under that first line, then Deploy >
Manage deployments > edit > New version. The web app keeps its address, which the site holds as INTAKE_URL in `src/build.py`.

Every Monday at 08:00 the script sends a summary of the week. If it stops coming, the script has stopped.
