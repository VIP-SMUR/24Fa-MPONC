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


## The Four-Step Model
Given that the agents move across various subregions of the Atlanta area in our simulation, one of the critical steps of the simulation is figuring out what subregion the agents go to. To do this in a way that accurately represents real-world distributions, we turned to the four-step model, a common trip generation algorithm: 

<img width="758" alt="Screenshot 2024-12-03 at 2 19 28 PM" src="https://github.com/user-attachments/assets/fc8916ff-ec4b-41e5-ad1c-c1d37fbbd40c">

The model has four components:

1. Trip Generation: This part of the model estimates the number of trips originating from or destined for a specific area. It focuses on understanding how many trips are generated rather than specific travel patterns. This process usually involves some type of data pertaining to the area at hand, such as demographics, income, or land usage.
2. Trip Distribution; This part of the model estimates the number of trips for routes that go from an area to another, as determined in the trip generation step. This process is typically done using the gravity model, which assumes that the number of trips are positively correlated with the attractiveness of an area and inversely correlated to distance.
3. Mode Choice: This part of the model determines the mode of transporation used to make the trips. This is typically done by considering demographic data (such as the percentage of people with cars) in an area.
4. Route Assignment: This part of the model determines the routes travelers take between origins and destinations. This is typically done by considering the route that takes the shorted possible time, and following that. 

Our approach closely follows these four components. We first generate trips by considering the amenity density of areas. We sum up all amenity densities, and divide each area's density by this sum to generate a probability. We then utilize a Poisson Distribution to generate the number of trips by multipling a base number of trips by the probability. We then consider trip distribution through a modified gravity model. The equation for our model is the following, given that we aim to go from area/region i to j:

<img width="686" alt="Screenshot 2024-12-03 at 2 37 56 PM" src="https://github.com/user-attachments/assets/ad0e2d78-bd8f-46d4-b4a4-b19ad4e37912">

We essentially multiply the total number of trips from area i to area j with the net amenity score for the destination j times transportation cost for that specific trip from area i to j, divided by the net amenity score for area j times the transportation cost from area i to j summed up over all destination j's. 

For our modal split, we assume that the car ownership rate is 0.7, and that the transit rate is 0.3. Each region's trips are split based on this. We then assign these routes based on the shortest possible distance.

Through this process, we were able to have a methodical way of distributing the agents across Atlanta based on area factors such as amenity density.

## Strengths and Weaknesses
### Strengths
Our approach is very modularized. For instance, the four-step model created can be used in any other simulation of any other region. It simply needs lists of agents, a NetworkX graph, and other generalized parameters to operate. Furthermore, Our approach is backed by established human behavior approaches (no-regret dynamics), utilizes a distribution system that is also established (four-step model). We are able to produce dynamic visuals (GIFs).

### Weaknesses
Our approach is only limited to the 2010 Census data for “training purposes.” This may cause our model to overfit and be unable to reliably extrapolate to 2022 Census Data. Additionally, it is very time-consuming to run the simulation, as 37 minutes are currently needed to generate centroids. We aimed to solve this issue with multithreading, but API calls caused this to fail (we kept running into buffering issues). Our simulation also assumes that there is no immigration/emigration in Atlanta, as we have a set, fixed number of agents. We also limit transportation choices to cars and public transportation, even though there are other mediums. 
