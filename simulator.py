#!/usr/bin/env python
from __future__ import division, print_function

## @mainpage
# Documentation for the brownout load-balancer simulator. If confused, start
# with the @ref simulator namespace.

import argparse
import numpy as np
import os
import sys
import time

from plants import ClosedLoopClient, OpenLoopClient, LoadBalancer, Server, Cloner, LoadBalancerCentralQueue
from base import SimulatorKernel
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
    parser.add_argument('--printRespTime',
        type = int,
        help = 'Log the response times for each request',
        default = 1)
    parser.add_argument('--printsim',
        type = int,
        help = "Insert simulation number to print, usable from MC top script to manually keep track of iterations",
        default=-1)
    parser.add_argument('--setSeed',
        type = int,
        help = "Set the seed",
        default = 65184)
    parser.add_argument('--maxRunTime',
        type = int,
        help = "Set an upper runtime limit on each simulation",
        default = -1)

    # Add scenario specific arguments
    group_s = parser.add_argument_group('scen', 'Scenario options')
    group_s.add_argument('--dist',
        type = str,
        help = 'Define service rate distribution',
        default = 'expon')
    group_s.add_argument('--path',
         type=str,
         help='Define service rate distribution path',
         default='')
    group_s.add_argument('--serviceRate',
        type = float,
        help = 'Enables setting the service rate from command line',
        default = 1.0)
    group_s.add_argument('--arrivalRateFrac',
        type = float,
        help = 'Enables setting the arrival rate fraction of servers*serviceRate from command line',
        default = 0.3)
    group_s.add_argument('--nbrOfServers',
         type = int,
         help = 'Set the number of servers used',
         default = 12)
    group_s.add_argument('--uniformArrivals',
        type = int,
        help = 'Use uniform arrival rates',
        default = 0)
    group_s.add_argument('--arrivalDelay',
        type = float,
        help = 'Use uniform arrival rates',
        default = 0.0)
    group_s.add_argument('--cancellationDelay',
        type = float,
        help = 'Use uniform arrival rates',
        default = 0.0)

    # Add load-balancer specific command-line arguments
    group_lb = parser.add_argument_group('lb', 'Load-balancer options')
    group_lb.add_argument('--lb',
        help = 'Load-balancer algorithm or ALL: ' + ' '.join(LoadBalancer.ALGORITHMS),
        default = 'ALL')
    group_lb.add_argument('--cloning',
        type = float,
        help = '1 if cloning is activated, 0 otherwise',
        default = 0)
    group_lb.add_argument('--nbrClones',
        type = int,
        help = 'Specify nbr clones, 1 is default (aka no cloning)',
        default = 1)

    args = parser.parse_args()

    # Find load-balancing algorithm
    if args.lb == 'ALL':
        loadBalancingAlgorithms = LoadBalancer.ALGORITHMS
    elif 'IQ' in args.lb:
        loadBalancingAlgorithms = [args.lb]
    elif args.lb in LoadBalancer.ALGORITHMS:
        loadBalancingAlgorithms = [args.lb]
    else:
        print("Unsupported algorithm '{0}'".format(args.lb), file = sys.stderr)
        loadBalancingAlgorithms = ""
        parser.print_help()
        quit()

    for loadBalancingAlgorithm in loadBalancingAlgorithms:
        #outdir = os.path.join(args.outdir, loadBalancingAlgorithm) Better if we denote paths individually
        outdir = args.outdir
        if not os.path.exists(outdir): # Not cool, Python!
            os.makedirs(outdir)
        cloner = Cloner(setSeed=args.setSeed)
        sim = SimulatorKernel(cloner=cloner, outputDirectory=outdir, maxRunTime=args.maxRunTime)
        cloner.setSim(sim)

        try:
            runSingleSimulation(
                sim=sim,
                scenario=args.scenario,
                loadBalancingAlgorithm=loadBalancingAlgorithm,
                cloning=args.cloning,
                nbrClones=args.nbrClones,
                logging=args.logging,
                printout=args.printout,
                printRespTime=args.printRespTime,
                dist=args.dist,
                distpath = args.path,
                serviceRate=args.serviceRate,
                arrivalRateFrac=args.arrivalRateFrac,
                nbrOfServers=args.nbrOfServers,
                uniformArrivals=args.uniformArrivals,
                setSeed=args.setSeed,
                arrivalDelay=args.arrivalDelay,
                cancellationDelay=args.cancellationDelay
            )
        except Exception as e:
            print("Caught exception: {0}".format(e))
            sim.closeLogging()

    elapsed_time = time.time() - start_time
    s = "Elapsed time (seconds): {:.3f}".format(elapsed_time)
    if args.printsim >= 0:
        s = "Simulation {} completed, ".format(args.printsim) + s
    print(s)

## Runs a single simulation
# @param outdir folder in which results should be written
# @param scenario file containing the scenario
# @param loadBalancingAlgorithm load-balancing algorithm name
def runSingleSimulation(sim, scenario, loadBalancingAlgorithm, cloning, nbrClones, logging, printout, printRespTime,
                        dist, distpath, serviceRate, arrivalRateFrac, nbrOfServers, uniformArrivals, setSeed,
                        arrivalDelay, cancellationDelay):

    servers = []
    clients = []

    if loadBalancingAlgorithm == "central-queue":
        loadBalancer = LoadBalancerCentralQueue(sim, printout=printout, printRespTime=printRespTime)
    else:
        loadBalancer = LoadBalancer(sim, printout=printout, printRespTime=printRespTime, seed=(setSeed+1))
    if 'IQ-' in loadBalancingAlgorithm:
        index = loadBalancingAlgorithm.index('-')
        intstr = loadBalancingAlgorithm[index+1:]
        loadBalancer.setD(int(intstr))
        loadBalancingAlgorithm = loadBalancingAlgorithm[:index]

    loadBalancer.algorithm = loadBalancingAlgorithm
    sim.cloner.setCloning(cloning)
    sim.cloner.setNbrClones(nbrClones)
    sim.setupLogging(logging)
    sim.setServers(servers)

    openLoopClient = OpenLoopClient(sim, loadBalancer, uniformArrivals=uniformArrivals, seed=(setSeed+2))

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

    def addServer(at, serviceTimeDistribution=None, dollySlowdown=1,
                  meanStartupDelay = 0.0, meanCancellationDelay = 0.0):
        def addServerHandler():
            server = Server(sim, serviceTimeDistribution=serviceTimeDistribution,dollySlowdown=dollySlowdown,
                            seed=setSeed,meanStartupDelay=meanStartupDelay,
                            meanCancellationDelay=meanCancellationDelay)
            servers.append(server)
            loadBalancer.addBackend(server)

        sim.add(at, addServerHandler)

    def setRate(at, rate):
        sim.add(at, lambda: openLoopClient.setRate(rate))
        sim.reportRate(rate)

    def endOfSimulation(at):
        otherParams['simulateUntil'] = at

    # Load scenario
    otherParams = {}
    execfile(scenario)

    if 'cluster' in loadBalancingAlgorithm:
        sim.add(0, loadBalancer.setClusters)

    if 'simulateUntil' not in otherParams:
        raise Exception("Scenario does not define end-of-simulation")
    simulationTime = otherParams['simulateUntil']
    sim.run(until = simulationTime)

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
    toReport.append(( "serviceRate", "{:.4f}".format(serviceRate)))
    toReport.append(( "arrivalRateFrac", "{:.4f}".format(arrivalRateFrac)))
    totalActiveTime = 0.0
    for k, server in enumerate(loadBalancer.backends):
        if server.isActive:
            server.activeTime += (sim.now - server.latestActivation)
        toReport.append(( "s{} util".format(k), "{:.4f}".format(server.activeTime / sim.now)))
        totalActiveTime = totalActiveTime + server.activeTime
    toReport.append(("avg util", "{:.4f}".format(totalActiveTime/(sim.now*len(loadBalancer.backends)))))
    toReport.append(("clone std coeff", "{:.5f}".format(sim.cloner.processorShareVarCoeff)))
    toReport.append(("clone mean share", "{:.5f}".format(sim.cloner.processorShareMean)))

    sim.output('final-results', ', '.join([k for k,v in toReport]))
    sim.output('final-results', ', '.join([v for k,v in toReport]))

    if printout:
        print(*[k for k,v in toReport], sep = ', ')
        print(*[v for k,v in toReport], sep = ', ')

    #for key in sorted(utils.iterkeys()):
    #    s = "server %s util: %s" % (key, utils[key])
    #    if printout:
    #        print(s)
    #    sim.output('final-results', s)

if __name__ == "__main__":
    main() # pragma: no cover
