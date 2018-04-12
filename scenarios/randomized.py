from numpy.random import uniform as randomize
from numpy import mean as mean
from numpy import random
import os


random.seed(5)

def initOutput(issuer):

    directory = '/local/home/tommi/CloudControl/ICAC2018/sim-repo/brownout-lb-simulator//results/trivial/co-op/'
    filename = 'sim-' + str(issuer) + '.csv'
    outputFilename = os.path.join(directory, filename)
    outputFile = open(outputFilename, 'w')

    return outputFile


def output(outputFile, outputLine):

    outputFile.write(outputLine + "\n")

    # kills performance, but reduces experimenter's impatience :D
    outputFile.flush()


outputFile = initOutput('scenarios')

nbrIterations = 2

for i in range(0, nbrIterations):
    servers = int(randomize(3, 11)) # 3-10 servers

    serverSpeeds = []
    for j in range(0, servers):
        optSpeed = randomize(0.02, 0.07)
        manSpeed = randomize(0.001, 0.004)
        serverSpeeds.append((optSpeed, manSpeed))

    meanOpt = mean([speed[0] for speed in serverSpeeds])
    meanMan = mean([speed[1] for speed in serverSpeeds])

    desiredOptContent = randomize(0.1, 0.9)

    arrivals = 1/(desiredOptContent*meanOpt/servers + (1-desiredOptContent)*meanMan/servers)

    setRate(at=i*50.0, rate=arrivals)
    changeActiveServers(at=i*50.0, nbrActive=servers, serverSpeeds=serverSpeeds)

    print("Scenario " + str(i+1))
    print("Nbr servers " + str(servers))
    print("meanOpt " + str(meanOpt))
    print("meanMan " + str(meanMan))
    print("desiredOptContent " + str(desiredOptContent))
    print("Arrival rate " + str(arrivals))

    valuesToOutput = [i+1, servers, meanOpt, meanMan, desiredOptContent, arrivals]

    output(outputFile, ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))


endOfSimulation(at = nbrIterations*50.0)