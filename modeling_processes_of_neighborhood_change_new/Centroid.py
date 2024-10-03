#wealth - average endowment of all agents visiting
class Centroid:
    self.longitude = 0.0
    self.latitude = 0.0
    self.name = ""
    self.inBeltline = False
    
    agentList = []
    wealth = 0.0
    
    def __init__(self, longitude, latitude, name, inBeltline): # constructor
        self.longitude = longitude
        self.latitude = latitude
        self.name = name

    def updateWealth(agentList): # get average wealth of all agents at that time
        totalWealth = 0
        for agent in agentList :
            totalWealth = totalWealth + agent.dow
        wealth = totalWealth / len(agentList)

    
    