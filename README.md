# DataLogger_Graphtec_GL840_Auswertung
This code uses your csv straight out of the DataLogger GL840. No editing of the csv is neccesary!

Copy this code in the same folder as the csv you want to evaluate. Then open the code in vs studio and insert your csv file name as replacment for "name.csv" in line 9.
Then you have to edit the date "2026-00-00 00:00:00" (years-mm-dd dd:mm:ss) to your current date of the data in line 95.
"00:00:00 -> dd:mm:ss" this is your start_time for the Diagramm.
The length of the diagram can be changed in line 111. The left value is deciding how many hours the diagramm starts ahead your setted start_time.
The right value is responsible how many hours after start_time are printed in the diagramm. 
(left=0, right = 1.5) -> Diagramm starts at start_time and ends at (start time + 1.5h)
