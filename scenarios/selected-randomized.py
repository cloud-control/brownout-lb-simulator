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

s = 0

nbrIterations = 100

selectedScenarios = [21-1, 28-1, 68-1, 18-1, 21-1]

for i in range(0, nbrIterations):
    servers = int(randomize(3, 11)) # 3-10 servers

    serverSpeeds = []
    for j in range(0, servers):
        optSpeed = randomize(0.05/5, 0.20/5)
        manSpeed = randomize(0.001/5, 0.004/5)
        serverSpeeds.append((optSpeed, manSpeed))

    meanOpt = mean([speed[0] for speed in serverSpeeds])
    meanMan = mean([speed[1] for speed in serverSpeeds])

    desiredOptContent = randomize(0.1, 0.9)

    arrivals = 1/(desiredOptContent*meanOpt/servers + (1-desiredOptContent)*meanMan/servers)

    #minMc = max(int(1/meanOpt - 200*servers/(arrivals*meanOpt)), 5)

    #maxMc = min(max(int(1 / meanOpt - 60 * servers / (arrivals * meanOpt)), minMc), 50)

    minMc = 5
    maxMc = 30

    MC = int(randomize(minMc, maxMc))

    quote = (arrivals*(1-meanOpt*MC)/servers)

    if i in selectedScenarios:
        for nbr in range(0, 22):
            scenarioNbr = selectedScenarios.index(i)
            time = scenarioNbr*50.0 + 250*nbr
            setRate(at=time, rate=arrivals)
            changeActiveServers(at=time, nbrActive=servers, serverSpeeds=serverSpeeds)
            changeMC(at=time+1, newMC=MC)

            if i == 20:
                setRate(at=4* 50.0 + 250 * nbr, rate=arrivals)
                changeActiveServers(at=4* 50.0 + 250 * nbr, nbrActive=servers, serverSpeeds=serverSpeeds)
                changeMC(at=1+4* 50.0 + 250 * nbr, newMC=MC)

                """print("Scenario " + str(i + 1))
                print("Nbr servers " + str(servers))
                print("meanOpt " + str(meanOpt))
                print("meanMan " + str(meanMan))
                print("desiredOptContent " + str(desiredOptContent))
                print("Arrival rate " + str(arrivals))
                print("minMC is: " + str(minMc))
                print("maxMc is: " + str(maxMc))
                print("MC is: " + str(MC))
                print("quote is: " + str(quote))"""

            s += 1

            """print("Scenario " + str(i+1))
            print("Nbr servers " + str(servers))
            print("meanOpt " + str(meanOpt))
            print("meanMan " + str(meanMan))
            print("desiredOptContent " + str(desiredOptContent))
            print("Arrival rate " + str(arrivals))
            print("minMC is: " + str(minMc))
            print("maxMc is: " + str(maxMc))
            print("MC is: " + str(MC))
            print("quote is: " + str(quote))"""

            valuesToOutput = [i+1, servers, meanOpt, meanMan, desiredOptContent, arrivals, MC, quote]

            output(outputFile, ','.join(["{0:.5f}".format(value) for value in valuesToOutput]))


endOfSimulation(at = 22*250.0)