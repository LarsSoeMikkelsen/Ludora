/*
   Set launcher icon to ludora-start-here
   Based on Fedora's kickoff icon setup script
*/

if ( applet.readConfig("icon", "start-here-kde") == "start-here-kde" ) {
  applet.currentConfigGroup = ["General"]
  applet.writeConfig("icon", "ludora-start-here");
}
