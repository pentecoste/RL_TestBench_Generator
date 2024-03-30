# RL_TestBench_Generator

Python script that generates a file called "output.vhd". The file consists of one big test case composed by a number of smaller test cases, tested one subsequently to another. All test cases values are generated randomly, the probability of getting a "0" as a value in a given position of the test sequence is approximatively 79%.
Each test case sequence has a random length and starts from a randomly chosen memory address.
A reset signal is generated between elaborations with a probability of 10%.

## What to use output.vhd for?

output.vhd is a .vhd file generated for testing the component built in Vivado for the "Prova Finale di Reti Logiche 2023-2024" course at Politecnico Di Milano. 
