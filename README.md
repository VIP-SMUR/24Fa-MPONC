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

## Census-based approach
A key part of our approach is that it utilizes data from the US census; namely, the graphical regions our agents inhabit correspond directly to US census tracts. Consequently, our simulation produces economic and population data for individual census tracts, which we can then compare to live census data. Since the US Census TIGER/Line Geodatabases contain publicly downloadable shapefiles of all the geographic regions it reports on, our simulation can likewise operate with any other census-reported region, not just census tracts, including zip codes, housing districts, school districts, etc. 

Additionally, each 'agent' has a unique wealth attribute as one of the factors influencing decision-making. Instead of assigning these wealths arbitrarily, we create this distribution of wealth using census population and median income data, so that our agents are representative of actual Fultona and Dekalb county resident demographics. Namely, we use the following tables from the Census website: "[S1903 | Median Income In The Past 12 Months (In 2010 Inflation-adjusted Dollars) - ACS 5-Year Estimates Subject Tables](https://data.census.gov/table/ACSST5Y2010.S1903?q=s1903%202010&g=050XX00US13089$1400000,13121$1400000)" and "[B01003 | Total Population - 2010: ACS 5-Year Estimates Detailed Tables](https://data.census.gov/table/ACSDT5Y2022.B01003?q=B01003&g=050XX00US13089$1400000,13121$1400000)". By changing the hyperlinks in our code, our simulation can run with different distributions; for example, those from different years.
* *Note: For the median income and population tables, the hyperlinks in the code won't be 'activated' until a request is made directly on the Census website - navigate to those links and use the 'Download' button for the appropriate graphs; no other action needed (Fix incoming)*

TIGER/Line Geodatabases shapefiles:
![image](https://github.com/user-attachments/assets/33f8e895-4e59-420c-96c7-d83cf9c69178)

Income distribution tables:
![image](https://github.com/user-attachments/assets/28d80cd9-3e67-451f-a37d-4aaf1c0ff2e7)

Example of simulating a different geographic region [close-up of Atlanta beltline area]:
![image](https://github.com/user-attachments/assets/0ba8680c-d1c0-4bfd-8eaa-169e966240e0)
![image](https://github.com/user-attachments/assets/0c8d82fc-7977-4dac-a02a-6cecb64f7991)


## Project status
### Outputs & configuration
Our code outputs a GIF to visualize agent behavior over time. Each circle represents the centroid of a census tract - green signifying those 'in the Atlanta Beltline' - and the encircled number is the agent population.
Our code also outputs a CSV file containing all the simulated data at every single timestep.

* *Data contained in CSV's: Census tract name, agent population, raw average income, average income reported by census, normalized average incomes, and amenity density.*
        * *TODO: Include raw amenity counts, census tract geographic area (sqkm).*
* *Note: 'Timestep' refers to a single instance agent action (relocation); 20,000 timesteps mean the agent's relocate 20,000 times.*

#### GIF
This GIF shows the behavior of 1,000 agents up to 20,000 timesteps, frames being captured every 400 timesteps. Rho=1, alpha=0.25.
![Georgia_1_0 25_1000](https://github.com/user-attachments/assets/0bb37051-1701-436b-afd3-de92eea845d5)

#### Configuration
In **configuration.py**, the user can specify various settings of the simulation. Changing graph settings is a matter of changing the hyperlinks in **configuration.py**.

**Simulation settings:** 
* Total timesteps run in the simulation
* Timestep interval at which to capture the GIF's frames
* Number of agents
* Variables affect agent behavior
**Graph settings:**
* Regions to simulate
* Economic distribution data
* Regions to mark as 'in the Atlanta Beltline'

Simulation and graph settings:
![image](https://github.com/user-attachments/assets/beb16d76-38b4-410c-85cb-dc922fe924e7)
![image](https://github.com/user-attachments/assets/ae233654-75dc-4472-b5d1-b637ff252c82)

### Runtimes
(1000 agents, 530 census tracts)
Run on a laptop,
Fetching amenities from OpenStreetMap via OSMnx: ~37 minutes
Computing centroid distances: ~18 minutes
Simulation (x8): ~45 minutes
GIF creation (x1), 50 frames: ~19 min
* *Everything except the actual Simulation and the GIF creation is cached, so those runtimes are negligible in subsequent runs*

## Atlanta Beltline in our Simulation
We automate the process of labelling certain regions as 'in the Atlanta Beltline' by using commuting paths from OpenStreetMap that correspond to the Atlanta Beltline - namely, a bike trail and a railway. To experiment with a different beltline, such as a beltline that spanned across Atlanta horizontally, or simply expanded north by x miles, we would acquire the OpenStreetMap ID's of existing paths (bike trails, walking paths, roads, etc.) corresponding to our desired Beltline, and paste these into **configuration.py**. Alternatively, we can create a such path ourselves in OpenStreetMap.
Then, any region containing segments of these trails would automatically be marked as "In the Atlanta Beltline". 

* *Note: our current code only works if these trails are labelled as "Relations" in OpenStreetMap*
        * *TODO: make this dynamic*

In **configuration.py** - bike trail and railroad OpenStreetMap ID's:

![image](https://github.com/user-attachments/assets/bef11cd0-ba21-450f-ab3b-7d81b650688e)

Bike Trail                 |  Railroad
:-------------------------:|:-------------------------:
<img src=https://github.com/user-attachments/assets/8f692216-771d-4f2e-b88e-7e282c595fc1 width="400"/>   |  <img src=https://github.com/user-attachments/assets/7477fa8d-6e14-4a14-8558-678b3f8f7121 width="400"/>

<img src=https://github.com/user-attachments/assets/be9bb85e-05c8-423e-94d2-0f02e97b33cf width="400"/>


## Strengths and Weaknesses
### Strengths
Our approach is very modularized. For instance, the four-step model created can be used in any other simulation of any other region. It simply needs lists of agents, a NetworkX graph, and other generalized parameters to operate. Furthermore, Our approach is backed by established human behavior approaches (no-regret dynamics), utilizes a distribution system that is also established (four-step model). We are able to produce dynamic visuals (GIFs).

### Weaknesses
Our approach is only limited to the 2010 Census data for “training purposes.” This may cause our model to overfit and be unable to reliably extrapolate to 2022 Census Data. Additionally, it is very time-consuming to run the simulation, as 37 minutes are currently needed to generate centroids. We aimed to solve this issue with multithreading, but API calls caused this to fail (we kept running into buffering issues). Our simulation also assumes that there is no immigration/emigration in Atlanta, as we have a set, fixed number of agents. We also limit transportation choices to cars and public transportation, even though there are other mediums. 
