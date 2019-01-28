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

from plants import ClosedLoopClient, OpenLoopClient, LoadBalancer, Server, Cloner
from base import Request, SimulatorKernel
from base.utils import *

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

    # Parsing command line options to find out the algorithm
    parser = argparse.ArgumentParser( \
        description='Run brownout load balancer simulation.', \
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--outdir',
        help = 'Destination folder for results and logs',
        default = 'results')
    parser.add_argument('--scenario',
        help = 'Specify a scenario in which to test the system',
        default = os.path.join(os.path.dirname(sys.argv[0]), 'scenarios', 'replica-steady-1.py'))

    parser.add_argument('--logging',
                        help='Specify if logging should be activated',
                        default=0)
    parser.add_argument('--printout',
        type = int,
        help = 'Get printout on simulation progress',
        default = 1)
    parser.add_argument('--printsim',
        type = int,
        help = "Insert simulation number to print, usable from MC top script to manually keep track of iterations",
        default=-1)

    # Add load-balancer specific command-line arguments
    group = parser.add_argument_group('lb', 'Load-balancer options')
    group.add_argument('--lb',
        help = 'Load-balancer algorithm or ALL: ' + ' '.join(LoadBalancer.ALGORITHMS),
        default = 'ALL')
    group.add_argument('--cloning',
        type = float,
        help = '1 if cloning is activated, 0 otherwise',
        default = 0)
    group.add_argument('--nbrClones',
        type = int,
        help = 'Specify nbr clones, 1 is default (aka no cloning)',
        default = 1)

    args = parser.parse_args()

    # Find load-balancing algorithm
    if args.lb == 'ALL':
        loadBalancingAlgorithms = LoadBalancer.ALGORITHMS
    elif args.lb in LoadBalancer.ALGORITHMS:
        loadBalancingAlgorithms = [args.lb]
    else:
        print("Unsupported algorithm '{0}'".format(args.lb), file = sys.stderr)
        loadBalancingAlgorithms = ""
        parser.print_help()
        quit()

    for loadBalancingAlgorithm in loadBalancingAlgorithms:
        outdir = os.path.join(args.outdir, loadBalancingAlgorithm)
        if not os.path.exists(outdir): # Not cool, Python!
            os.makedirs(outdir)
        cloner = Cloner()
        sim = SimulatorKernel(cloner=cloner, outputDirectory=outdir)

        try:
            runSingleSimulation(
                sim=sim,
                scenario=args.scenario,
                loadBalancingAlgorithm=loadBalancingAlgorithm,
                cloning=args.cloning,
                nbrClones=args.nbrClones,
                logging=args.logging,
                printout=args.printout,
            )
        except Exception as e:
            print("Caught exception: {0}".format(e))
            sim.closeLogging()

        #print("Caught exception {0}".format(e))

    elapsed_time = time.time() - start_time
    s = "Elapsed time (seconds): " + str(elapsed_time)
    if args.printsim >= 0:
        s = "Simulation {} completed, ".format(args.printsim) + s
    print(s)

## Runs a single simulation
# @param outdir folder in which results should be written
# @param scenario file containing the scenario
# @param loadBalancingAlgorithm load-balancing algorithm name
def runSingleSimulation(sim, scenario, loadBalancingAlgorithm, cloning, nbrClones, logging, printout):

    servers = []
    clients = []

    loadBalancer = LoadBalancer(sim, printout)
    loadBalancer.algorithm = loadBalancingAlgorithm
    sim.cloner.setCloning(cloning)
    sim.cloner.setNbrClones(nbrClones)
    sim.setupLogging(logging)

    openLoopClient = OpenLoopClient(sim, loadBalancer)

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
                addServer(at=timeDiff*i)
                i += 1
                nbrDiff -= 1
        sim.add(at, changeActiveServersHandler)

    def addServer(at, serviceTimeDistribution=None):
        #print("at is " + str(at))
        def addServerHandler():
            #print("in handler: at is " + str(at))
            server = Server(sim, serviceTimeDistribution=serviceTimeDistribution)
            servers.append(server)
            loadBalancer.addBackend(server)

        sim.add(at, addServerHandler)

    def setRate(at, rate):
        sim.add(at, lambda: openLoopClient.setRate(rate))

    def endOfSimulation(at):
        otherParams['simulateUntil'] = at

    # Load scenario
    otherParams = {}
    execfile(scenario)

    if 'simulateUntil' not in otherParams:
        raise Exception("Scenario does not define end-of-simulation")
    sim.run(until = otherParams['simulateUntil'])

    # Report end results
    responseTimes = reduce(lambda x,y: x+y, [client.responseTimes for client in clients], []) + openLoopClient.responseTimes

    toReport = []
    toReport.append(( "loadBalancingAlgorithm", loadBalancingAlgorithm.ljust(20) ))
    toReport.append(( "numRequests", str(len(responseTimes)).rjust(7) ))
    toReport.append(( "avgResponseTime", "{:.4f}".format(avg(responseTimes)) ))
    toReport.append(( "p95ResponseTime", "{:.4f}".format(np.percentile(responseTimes, 95)) ))
    toReport.append(( "p99ResponseTime", "{:.4f}".format(np.percentile(responseTimes, 99)) ))
    toReport.append(( "maxResponseTime", "{:.4f}".format(max(responseTimes)) ))
    toReport.append(( "stddevResponseTime", "{:.4f}".format(np.std(responseTimes)) ))

    if printout:
        print(*[k for k,v in toReport], sep = ', ')
        print(*[v for k,v in toReport], sep = ', ')

    sim.output('final-results', ', '.join([k for k,v in toReport]))
    sim.output('final-results', ', '.join([v for k,v in toReport]))

if __name__ == "__main__":
    main() # pragma: no cover
