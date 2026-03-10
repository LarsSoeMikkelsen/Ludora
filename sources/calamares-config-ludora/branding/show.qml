import QtQuick 2.0
import calamares.slideshow 1.0

Presentation {
    id: presentation
    function onActivate() {}
    function onLeave() {}

    Rectangle {
        anchors.fill: parent
        color: "#1e1e2e"

        Text {
            anchors.centerIn: parent
            text: "Welcome to Ludora Gaming Edition\n\nYour installation is in progress..."
            font.pixelSize: 24
            color: "#cdd6f4"
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
