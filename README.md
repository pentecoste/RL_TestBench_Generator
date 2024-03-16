# RL_TestBench_Generator

Python script that generates a file called "output.vhd" containing a test case made of a chosen number of test cases that get tested one subsequently to another. All test cases are generated randomly, the probability of getting a "0" as a value in a given position of the test sequence is approximatively 79%.
Each test case sequence has a random length and starts from a randomly chosen memory address.

## What to use output.vhd for?

output.vhd is a .vhd file generated for testing the component built in Vivado for the "Prova Finale di Reti Logiche 2023-2024" course at Politecnico Di Milano. 
