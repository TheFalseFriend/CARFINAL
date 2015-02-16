Inf3 - Computer Architecture 
Coursework 1 - 'Understanding Branch Prediction'
Thomas Cumming (Matric no:s1230426)

14/02/15

NB: Every simulation in the coursework handout is implemented in my code, there is nothing incomplete. However, I think there may be a bug with dynamic prediciton simulation, I get surprising precentages.
	
My report on the simulator itself is in SimulatorReport.pdf, and the report on my results is in ResultsReport.pdf.
ResultsReport.pdf is unfinished.

========README==============================

1. Compilation
	At a DICE terminal, do 

		$ python BPSim.py -h

	This will compile the simulator code, and display a message with usage instructions.


2. Using the simulator
	To run the simulator with static branch prediction, type

		$ python BPSim.py s [path_to_trace_file]

	at a DICE terminal, where path_to_trace_file is the filepath to the appropriate trace file. The simulator will then prompt you with a choice of static prediction schemes to use; choose an option and the simulation will commence. Once done, the results will be displayed (this may take around 30 seconds or so) and the program will end.


	To run the simulator with dynamic branch prediction, do

		$ python BPSim.py d [path_to_trace_file] 

	at a DICE terminal, where path_to_trace_file is the filepath to the appropriate trace file. The simulator will then prompt you with a choice of history lengths to use; choose an option and the simulation will commence. Once done, the results will be displayed (this may take around one minute or so) and the program will end.

	NB: If you want to run the code with different parameters such as a differnt history length value or a different static scheme, or change from static/dynamic altogether, you must run the simulator again as above, but with your new desired settings; there is no 'do you want to run again' functionality.
