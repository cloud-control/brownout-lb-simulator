Brownout Simulator [![Build Status](https://travis-ci.com/cloud-control/brownout-lb-simulator.svg?token=fh2Qsy8QJtazXPwAUyeq&branch=master)](https://travis-ci.com/cloud-control/brownout-lb-simulator)
=================
Simulator for exploring the potential of the brownout concept. Currently implements the following behaviours:

* Brownout replicas, using algorithms presented at [Klein14](http://www.diva-portal.org/smash/get/diva2:680477/FULLTEXT01.pdf) and [Maggio13](http://www.nt.ntnu.no/users/skoge/prost/proceedings/ifac2014/media/files/0669.pdf)
* Brownout load-balancing, using algorithms in [Durango14](http://lup.lub.lu.se/luur/download?func=downloadFile&recordOId=4778779&fileOId=4778809)
* Horizontal auto-scaler, algorithm pending implementation
