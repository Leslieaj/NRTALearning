# NRTALearning
A prototype on learning nondeterministic real-time automata.

### Overview 

This tool is dedicated to learning nondeterministic real-time automata (NRTAs), a subclass of timed automata with only one clock which resets at each transition. In 1987, Dana Angluin introduced the L* Algorithm for learning regular sets from queries and counterexamples. The tool implements two Angluin-style active learning algorithms for NRTAs. This branch implements the Extended-NL* algorithm which extends the learning algorithm for NFA. The `newlstar` branch implements the NRTALearning algorithm. The `drta` branch implements the learning algorithm for deterministic real-time automata.

### Installation & Usage

#### Prerequisite

- Python 3.5.* (or high)


#### Installation

- Just download.

It's a pure Python program.  We have test it on Ubuntu 16.04 64bit with Python 3.5.2.

#### Usage

For example

```shell
python3 learnrta.py test/a.json
```

- `learnota.py` is the main file of the program.

- The target DOTA is stored in a JSON file, in this example, `a.json` . The details are as follows.

  ```json
  {
    "name": "A",
    "l": ["1", "2", "3"],
    "sigma": ["a", "b"],
    "tran": {
  	    "0": ["1", "a", "[2,3)", "2"],
  	    "1": ["2", "a", "[5,+)", "3"],
  	    "2": ["2", "b", "(1,4)", "2"],
        	"3": ["2", "b", "(3,9]", "3"],
        	"4": ["3", "a", "[1,2]", "2"]
    },
    "init": ["1"],
    "accept": ["3"]
  }
  ```
  
  - "name" : the name of the target DOTA;
  - "l" : the set of the name of locations;
  - "sigma" : the alphabet;
  - "tran" : the set of transitions in the following form:
    - transition id : [name of the source location, action, guard, name of the target location];
    - "+" in a guard means INFTY;
    
  - "init" : the set of the name of initial location;
  - "accept" : the set of the name of accepting locations.

