#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import numpy as np
import random
import os
import sys
import time

from plants import AutoScaler, ClosedLoopClient, OpenLoopClient, LoadBalancer, Server, CoOperativeLoadBalancer, Cloner
from base import Request, SimulatorKernel
from base.utils import *
from controllers import loadControllerFactories

## Custom type for argparse to represent a random distribution
def distribution(s):
    parts = s.split(',')
    if parts[0] == 'normalvariate':
        try:
            return parts[0], float(parts[1]), float(parts[2])
        except:
            raise argparse.ArgumentTypeError(
                'Distribution must be normalvariate,average,variance')
    elif parts[0] == 'expovariate':
        try:
            return parts[0], float(parts[1])
        except:
            raise argparse.ArgumentTypeError(
                'Distribution must be expovariate,average')
    else:
        raise argparse.ArgumentTypeError(
            'Unknown distribution; choose normalvariate or expovariate')

## @package simulator Main simulator namespace

## Entry-point for simulator.
# Setups up all entities, then runs simulation(s).
def main():
    start_time = time.time()
    # Load all controller factories
    autoScalerControllerFactories = loadControllerFactories('autoscaler')
    replicaControllerFactories = loadControllerFactories('server')

    # Parsing command line options to find out the algorithm
    parser = argparse.ArgumentParser( \
        description='Run brownout load balancer simulation.', \
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--outdir',
        help = 'Destination folder for results and logs',
        default = 'results')
    parser.add_argument('--timeSlice',
        type = float,
        help = 'Time-slice of server scheduler',
        default = 0.01)
    parser.add_argument('--scenario',
        help = 'Specify a scenario in which to test the system',
        default = os.path.join(os.path.dirname(sys.argv[0]), 'scenarios', 'replica-steady-1.py'))

    group = parser.add_argument_group('ac', 'General autoscaler controller options')
    group.add_argument('--ac',
        help = 'Autoscaler controller: ' + ' '.join([ acf.getName() for acf in autoScalerControllerFactories ]),
        default = 'trivial')
    group.add_argument('--startupDelay',
        help = 'Set the distribution of the startup delay of a new replica',
        type = distribution,
        default = ('normalvariate', 60, 0))

    # Add autoscaler controller factories specific command-line arguments
    for acf in autoScalerControllerFactories:
        group = parser.add_argument_group("Options for '{0}' autoscaler controller".format(acf.getName()))
        acf.addCommandLine(group)

    group = parser.add_argument_group('rc', 'General replica controller options')
    group.add_argument('--rc',
        help = 'Replica controller: ' + ' '.join([ rcf.getName() for rcf in replicaControllerFactories ]),
        default = 'static')
    group.add_argument('--rcSetpoint',
        type = float,
        help = 'Replica controller setpoint',
        default = 1)
    group.add_argument('--rcPercentile',
        type = float,
        help = 'What percentile reponse time to drive to target',
        default = 95)

    # Add load-balancer specific command-line arguments
    group = parser.add_argument_group('lb', 'Load-balancer options')
    group.add_argument('--lb',
        help = 'Load-balancer algorithm or ALL: ' + ' '.join(LoadBalancer.ALGORITHMS),
        default = 'ALL')
    group.add_argument('--equal-theta-gain',
        type = float,
        help = 'Gain in the equal-theta algorithm',
        default = 0.025) #0.117)
    group.add_argument('--equal-thetas-fast-gain',
        type = float,
        help = 'Gain in the equal-thetas-fast algorithm',
        default = 2.0) #0.117)
    group.add_argument('--cloning',
        type = float,
        help = '1 if cloning is activated, 0 otherwise',
        default = 0)
    group.add_argument('--nbrClones',
        type = int,
        help = 'Specify nbr clones, 1 is default (aka no cloning)',
        default = 1)

    # Add replica controller factories specific command-line arguments
    for rcf in replicaControllerFactories:
        group = parser.add_argument_group("Options for '{0}' replica controller".format(rcf.getName()))
        rcf.addCommandLine(group)

    args = parser.parse_args()

    # Find autoscaler controller factory
    autoScalerControllerFactories = filter(lambda ac: args.ac == 'ALL' or ac.getName() == args.ac, autoScalerControllerFactories)
    if not autoScalerControllerFactories:
        print("Unsupported autoscaler controller '{0}'".format(args.ac), file = sys.stderr)
        parser.print_help()
        quit()

    # Find load-balancing algorithm
    if args.lb == 'ALL':
        loadBalancingAlgorithms = LoadBalancer.ALGORITHMS
    elif args.lb in LoadBalancer.ALGORITHMS:
        loadBalancingAlgorithms = [args.lb]
    else:
        print("Unsupported algorithm '{0}'".format(args.lb), file = sys.stderr)
        parser.print_help()
        quit()

    # Find replica controller factory
    replicaControllerFactories = filter(lambda rc: args.rc == 'ALL' or rc.getName() == args.rc, replicaControllerFactories)
    if not replicaControllerFactories:
        print("Unsupported replica controller '{0}'".format(args.rc), file = sys.stderr)
        parser.print_help()
        quit()

    # Allow controller factories to analyse command-line
    for autoScalerControllerFactory in autoScalerControllerFactories:
        autoScalerControllerFactory.parseCommandLine(args)
    for replicaControllerFactory in replicaControllerFactories:
        replicaControllerFactory.parseCommandLine(args)

    for autoScalerControllerFactory in autoScalerControllerFactories:
        for loadBalancingAlgorithm in loadBalancingAlgorithms:
            for replicaControllerFactory in replicaControllerFactories:
                outdir = os.path.join(args.outdir, autoScalerControllerFactory.getName(), replicaControllerFactory.getName())
                if not os.path.exists(outdir): # Not cool, Python!
                    os.makedirs(outdir)
                try:
                    runSingleSimulation(
                        outdir = outdir,
                        autoScalerControllerFactory = autoScalerControllerFactory,
                        replicaControllerFactory = replicaControllerFactory,
                        scenario = args.scenario,
                        timeSlice = args.timeSlice,
                        loadBalancingAlgorithm = loadBalancingAlgorithm,
                        cloning=args.cloning,
                        nbrClones=args.nbrClones,
                        equal_theta_gain = args.equal_theta_gain,
                        equal_thetas_fast_gain = args.equal_thetas_fast_gain,
                        startupDelay = args.startupDelay,
                    )
                except Exception as e:
                    print("Caught exception with {0} and {1}: {2}".
                        format(autoScalerControllerFactory, replicaControllerFactory, e))

    elapsed_time = time.time() - start_time
    print("Elapsed time (seconds): " + str(elapsed_time))

## Runs a single simulation
# @param outdir folder in which results should be written
# @param autoScalerControllerFactory factory for the auto-scaler controller
# @param replicaControllerFactory factory for the replica controller
# @param scenario file containing the scenario
# @param timeSlice time-slice for the server processor-sharing model
# @param loadBalancingAlgorithm load-balancing algorithm name
# @param equal_theta_gain parameter for load-balancing algorithm (TODO: move into LoadBalancingAlgorithm)
# @param equal_thetas_fast_gain paramater for load-balancing algorithm (TODO: move into LoadBalancingAlgorithm)
# @param startupDelay a tuple of the form (distribution, param1, param2)
def runSingleSimulation(outdir, autoScalerControllerFactory, replicaControllerFactory, scenario, timeSlice,
        loadBalancingAlgorithm, cloning, equal_theta_gain, equal_thetas_fast_gain, startupDelay, nbrClones):
    startupDelayRng = random.Random()
    startupDelayFunc = lambda: \
        getattr(startupDelayRng, startupDelay[0])(*startupDelay[1:])
    assert startupDelayFunc() # ensure the PRNG works
    startupDelayRng.seed(1)

    cloner = Cloner()
    sim = SimulatorKernel(cloner=cloner, outputDirectory=outdir)

    servers = []
    clients = []
    if loadBalancingAlgorithm == 'co-op':
        loadBalancer = CoOperativeLoadBalancer(sim, controlPeriod=1.0)
    else:
        loadBalancer = LoadBalancer(sim, controlPeriod=1.0)
        loadBalancer.algorithm = loadBalancingAlgorithm
        sim.cloner.setCloning(cloning)
        sim.cloner.setNbrClones(nbrClones)
        loadBalancer.equal_theta_gain = equal_theta_gain
        loadBalancer.equal_thetas_fast_gain = equal_thetas_fast_gain

    autoScaler = AutoScaler(sim, loadBalancer,
                controller = autoScalerControllerFactory.newInstance(sim,
                    'as-ctr'), startupDelay = startupDelayFunc)
    openLoopClient = OpenLoopClient(sim, autoScaler)


    # Define verbs for scenarios
    def addClients(at, n):
        def addClientsHandler():
            for _ in range(0, n):
                clients.append(ClosedLoopClient(sim, loadBalancer))
        sim.add(at, addClientsHandler)

    def delClients(at, n):
        def delClientsHandler():
            for _ in range(0, n):
                client = clients.pop()
                client.deactivate()
        sim.add(at, delClientsHandler)

    def changeServiceTime(at, serverId, y, n):
        def changeServiceTimeHandler():
            server = servers[serverId]
            server.serviceTimeY = y
            server.serviceTimeN = n
        sim.add(at, changeServiceTimeHandler)

    def changeMC(at, newMC):
        def changeMCHandler():
            if servers:
                for server in servers:
                    if server:
                        server.changeMC(newMC)
        sim.add(at, changeMCHandler)

    def changeActiveServers(at, nbrActive, serverSpeeds):
        def changeActiveServersHandler():
            oldActiveServers = len(loadBalancer.backends)
            #print("Old active servers was " + str(oldActiveServers))

            #print(serverSpeeds)

            nbrDiff = nbrActive - oldActiveServers

            while nbrDiff < 0:
                backendToRemove = loadBalancer.backends[-1]
                loadBalancer.removeBackend(backendToRemove)
                nbrDiff += 1

            i = 0
            for backend in loadBalancer.backends:
                backend.serviceTimeY = serverSpeeds[i][0]
                backend.serviceTimeN = serverSpeeds[i][1]
                i += 1

            timeDiff = 0.01
            while nbrDiff > 0:
                addServer(at=timeDiff*i, y=serverSpeeds[i][0], n=serverSpeeds[i][1])
                i += 1
                nbrDiff -= 1
        sim.add(at, changeActiveServersHandler)

    def addServer(at, y, n, seed, autoScale = False):
        #print("at is " + str(at))
        def addServerHandler():
            #print("in handler: at is " + str(at))
            server = Server(sim, \
                serviceTimeY = y, serviceTimeN = n, \
                timeSlice = timeSlice, seed=seed)
            newReplicaController = replicaControllerFactory.newInstance(sim, server, str(server) + "-ctl")
            server.controller = newReplicaController
            servers.append(server)
            if autoScale:
                autoScaler.addBackend(server)
            else:
                loadBalancer.addBackend(server)
        sim.add(at, addServerHandler)

    def setRate(at, rate):
        sim.add(at, lambda: openLoopClient.setRate(rate))

    def endOfSimulation(at):
        otherParams['simulateUntil'] = at

    # Load scenario
    otherParams = {}
    execfile(scenario)

    # For weighted-RR algorithm set the weights
    if loadBalancingAlgorithm == 'weighted-RR':
        serviceRates = np.array([ 1.0/x.serviceTimeY for x in servers ])
        sumServiceRates = sum(serviceRates)
        loadBalancer.weights = list(np.array(serviceRates / sumServiceRates))

    if 'simulateUntil' not in otherParams:
        raise Exception("Scenario does not define end-of-simulation")
    sim.run(until = otherParams['simulateUntil'])

    # Report end results
    responseTimes = reduce(lambda x,y: x+y, [client.responseTimes for client in clients], []) + openLoopClient.responseTimes
    numRequestsWithOptional = sum([client.numCompletedRequestsWithOptional for client in clients]) + openLoopClient.numCompletedRequestsWithOptional

    toReport = []
    toReport.append(( "autoScalerAlgorithm", autoScalerControllerFactory.getName().ljust(20) ))
    toReport.append(( "loadBalancingAlgorithm", loadBalancingAlgorithm.ljust(20) ))
    toReport.append(( "replicaAlgorithm", replicaControllerFactory.getName().ljust(20) ))
    toReport.append(( "numRequests", str(len(responseTimes)).rjust(7) ))
    toReport.append(( "numRequestsWithOptional", str(numRequestsWithOptional).rjust(7) ))
    toReport.append(( "optionalRatio", "{:.4f}".format(numRequestsWithOptional / len(responseTimes)) ))
    toReport.append(( "avgResponseTime", "{:.4f}".format(avg(responseTimes)) ))
    toReport.append(( "p95ResponseTime", "{:.4f}".format(np.percentile(responseTimes, 95)) ))
    toReport.append(( "p99ResponseTime", "{:.4f}".format(np.percentile(responseTimes, 99)) ))
    toReport.append(( "maxResponseTime", "{:.4f}".format(max(responseTimes)) ))
    toReport.append(( "stddevResponseTime", "{:.4f}".format(np.std(responseTimes)) ))

    print(*[k for k,v in toReport], sep = ', ')
    print(*[v for k,v in toReport], sep = ', ')

    sim.output('final-results', ', '.join([k for k,v in toReport]))
    sim.output('final-results', ', '.join([v for k,v in toReport]))

if __name__ == "__main__":
    main() # pragma: no cover
