# 24Fa-MPONC
Modeling Processes of Neighborhood Change


## Team

| Name                  | Seniority | Major                  | Department | GitHub Handle                                                 | 
| --------------------- | --------- | ---------------------- | ---------- | ------------------------------------------------------------- | 
| Matthew Lim           | Sophomore | Computer Science       | COC        | [mlim70](https://github.com/mlim70)                           |                                
| Reyli Olivo           | Junior    | Civil Engineering      | CEE        | [Rolivo05](https://github.com/Rolivo05)                       |                   
| Devam Mondal          | Junior    | Computer Science       | COC        | [Dodesimo](https://github.com/Dodesimo)                       | 



:   !!! abstract

        abstract goes here



## Setup

```bash
cd modeling_processes_of_neighborhood_change_new
conda create -n mponc python=3.12
conda activate mponc
pip install -r requirements.txt
python main.py
```


## Reference paper

```bibtex
@misc{mori2024modelingprocessesneighborhoodchange,
      title={Modeling Processes of Neighborhood Change}, 
      author={J. Carlos Martínez Mori and Zhanzhan Zhao},
      year={2024},
      eprint={2401.03307},
      archivePrefix={arXiv},
      primaryClass={cs.MA},
      url={https://arxiv.org/abs/2401.03307}, 
}
```

## Presentation


<a href="https://www.youtube.com/watch?v=sXhnPRdE7Hk" target="_blank" rel="noopener noreferrer">
    <img src="https://img.youtube.com/vi/sXhnPRdE7Hk/maxresdefault.jpg" width="480" alt="Final Presentation --- 24Fa --- Modeling Processes of Neighborhood Change (MPONC)" class="off-glb">
</a>

## Intro and Description
This semester, we utilized concepts in game theory, more specifically no-regret dynamics, in order to simulate the effects of the Atlanta Beltline on gentrification. We did so by considering the movement of agents that aim to reduce a cost function that is dependent on various factors, including number of amenities, upkeep, and other factors.


## Distribution of Trips
Given that the agents move across various subregions of the Atlanta area in our simulation, one of the critical steps of the simulation is figuring out what subregion the agents go to. To do this in a way that accurately represents real-world distributions, we turned to the four-step model, a common trip generation algorithm: 


<img src="https://www.researchgate.net/profile/Matthew-Burke-4/publication/29465763/figure/fig1/AS:340341136871431@1458155058829/Traditional-four-step-transport-model-adapted-from-Button-1977-p117.png" width="480" alt="Final Presentation --- 24Fa --- Modeling Processes of Neighborhood Change (MPONC)" class="off-glb">
