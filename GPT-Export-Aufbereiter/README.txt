GPT-Export-Aufbereiter
======================

Zweck
- Diese einfache Web-App bereitet einen großen ChatGPT-Export (conversations.json)
  in kleinere, leicht zu öffnende Teile auf und stellt eine Ansicht bereit,
  mit der Unterhaltungen durchsucht und angezeigt werden können.

So starten
1) Öffne die Datei "chat_aufbereiten.html" im Chrome oder Edge (Desktop).
2) Wähle deine Exportdatei (conversations.json) und einen Zielordner.
3) Klicke auf "Aufbereitung starten". Fortschritt wird angezeigt.
4) Danach kannst du den Zielordner direkt in der Oberfläche anzeigen lassen.

Hinweise
- Die App arbeitet vollständig lokal. Es erfolgt kein Upload.
- Fürs Schreiben in Ordner wird die File System Access API benötigt
  (Chrome/Edge). In Firefox/Safari ist das Schreiben ggf. nicht möglich.

