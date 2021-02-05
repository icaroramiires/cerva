# CERVA - SBRC 2020

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/lucaslzl/cerva/issues)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

:man_student: This project is part of my Marter's degree at Universidade Estadual de Campinas ([UNICAMP](https://ic.unicamp.br/)). 

:airplane: It was published in [SBRC 2020](http://sbrc2020.sbc.org.br/?lang=en) and the paper :notebook: is available at [CERVA: Roteamento Contextual para Veículos com Risco Espaço-temporal](https://sol.sbc.org.br/index.php/sbrc/article/view/12296)

:car: The goal is propose a Traffic Management System (TMS) that manages traffic by suggesting routes to vehicles. It has three modules being context window identification ([MARTINI](https://github.com/lucaslzl/martini)), context mapping, routing personalization. The previous version of the TMS proposed is [PONCHE](https://github.com/lucaslzl/ponche). The novelty compared with the previous work comprehends a traffic mapping strategy to generate SUMO routes, using kernel density estimation to obtain contextual data score, and a road balancing strategy.

### Tasks

- cd: CleanData
Clean tabular data according to it's columns and generate output.

- cm: ContextMapping
Identifies timewindow, apply clustering, and save clusters at 'mapped/' folder.

- ge: Generator
Generate the execution cfgs and trips.

- ro: RouteMiner
Mine routes and converts to simulator.

- tm: TrafficMiner
Mine traffic and saves the result.

- fm: FlowManager
Maps the flow to the .net edge ids.

- si: Simulation
Simulate the available scenarios.

- pl: Plotter
Plot the generated results.


To simulate execute the next command.

```bash
python torulethemall.py --si --times=20 --cities='chicago'
```

### Requirements

- [Python 2.7](https://www.python.org/downloads/)

To install python modules execute the next command.

```bash
pip install -r requirements.txt
```

All requirements are listed in requirements.txt file.

- [SUMO 0.25.0](https://sourceforge.net/projects/sumo/files/sumo/version%200.25.0/)
